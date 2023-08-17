import argparse
import json
import shutil
import subprocess
import brotli
from pathlib import Path
from pathvalidate import sanitize_filename
from selenium.webdriver.chrome.service import Service as ChromeService
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def get_book_requests(book_url: str) -> list:
    print("Getting book requests. Please wait...")
    service = ChromeService(executable_path=ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    with webdriver.Chrome(service=service, options=options) as driver:
        driver.get(book_url)
        return driver.requests


def analyse_book_requests(book_requests: list) -> tuple:
    print('Analysing book requests...')
    try:
        # find request with book json data
        book_json_requests = [r for r in book_requests if r.method == 'POST' and r.path.startswith('/ajax/b/')]
        # assert that we have only 1 request for book data found
        assert len(book_json_requests) == 1, 'Error: Book data not found. Exiting.'
        print('Book data found')
        # find request with m3u8 file
        m3u8_file_requests = [r for r in book_requests if 'm3u8' in r.url]
        # assert that we have only 1 request for m3u8 file found
        assert len(m3u8_file_requests) == 1, 'Error: m3u8 file request not found. Exiting.'
        print('m3u8 file found')
        book_json = json.loads(brotli.decompress(book_json_requests[0].response.body))
        return book_json, m3u8_file_requests[0].url
    except AssertionError as message:
        print(message)
        exit()


def separate_into_chapters(book_json: dict, full_mp3_filepath: Path, book_folder: Path):
    print('Separating chapters. Please wait...')
    for chapter in book_json['chapters']:
        chapter_path = book_folder / sanitize_filename(chapter['title'])
        ffmpeg_command = ['ffmpeg', '-i', f'{full_mp3_filepath}.mp3', '-acodec', 'copy', '-ss',
                          str(chapter['time_from_start']), '-to', str(chapter['time_finish']), f'{chapter_path}.mp3']
        subprocess.run(ffmpeg_command)


def download_book(book_json: dict, target_folder: Path, single_chapter: bool = False):
    print('Downloading book. Please wait...')
    if single_chapter:
        filepath = target_folder / book_json['chapters'][0]['title']
    else:
        filepath = target_folder / book_json['title']
    ffmpeg_command = ['ffmpeg', '-i', book_json['m3u8_url'], f'{filepath}.mp3']
    subprocess.run(ffmpeg_command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download a book from akniga.org')
    parser.add_argument('url', help='Book\'s url for downloading')
    parser.add_argument('output', help='Absolute or relative path where book will be downloaded')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--delete', action='store_true',
                       help='Delete full book folder, after chapter separation is done')
    group.add_argument('-f', '--full', action='store_true',
                       help='Do not separate the book into multiple chapters, if any')
    args = parser.parse_args()
    print(args)

    book_requests = get_book_requests(args.url)
    book_json, m3u8_url = analyse_book_requests(book_requests)
    book_json['m3u8_url'] = m3u8_url
    book_json['title'] = sanitize_filename(book_json['title'])
    book_json['chapters'] = json.loads(book_json['items'])

    # check if output folder is an absolute or relative
    if Path(args.output).is_absolute():
        output_path = args.output
    else:
        output_path = Path(__file__).parent / args.output

    # create book folder
    book_folder = Path(output_path) / book_json['title']
    Path(book_folder).mkdir(parents=True)

    if len(book_json['chapters']) == 1:
        print('Only one chapter found')
        # download book directly in book folder
        download_book(book_json, book_folder, single_chapter=True)
    elif len(book_json['chapters']) >= 2:
        print('Multiple chapters found')
        if args.f:
            print("Downloading full book without chapters separation")
            # download book directly in book folder
            download_book(book_json, book_folder, single_chapter=True)
        else:
            # create full book folder
            full_book_folder = book_folder / 'full_book'
            Path(full_book_folder).mkdir()
            if args.d:
                print("Downloading full book with chapters separation, deleting full book folder afterwards")
                # download book in full book folder, delete it afterward
                download_book(book_json, full_book_folder, single_chapter=False)
                separate_into_chapters(book_json, full_book_folder / book_json['title'], book_folder)
                shutil.rmtree(full_book_folder, ignore_errors=True)
            else:
                print("Downloading full book with chapters separation and keeping full book folder afterwards")
                download_book(book_json, full_book_folder, single_chapter=False)
                separate_into_chapters(book_json, full_book_folder / book_json['title'], book_folder)

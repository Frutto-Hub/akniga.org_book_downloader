import subprocess
import brotli
import requests
from selenium.webdriver.chrome.service import Service as ChromeService
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import json
import shutil
from pathlib import Path
from pathvalidate import sanitize_filename


class BookData:
    def __init__(self, items):
        self.title = items['title']
        self.res = items['res']
        self.hres = items['hres']
        self.srv = items['srv']
        self.sTextAuthor = items['sTextAuthor']
        self.sTextPerformer = items['sTextPerformer']
        self.sTextFav = items['sTextFav']
        self.items = items['items']
        self.topic_id = items['topic_id']
        self.titleonly = items['titleonly']
        self.slug = items['slug']
        self.version = items['version']
        self.bookurl = items['bookurl']
        self.preview = items['preview']
        self.author = items['author']
        self.sMsgTitle = items['sMsgTitle']
        self.sMsg = items['sMsg']
        self.bStateError = items['bStateError']
        self.m3u8_url = items['m3u8_url']
        self.chapters = items['chapters']


class AKnigaParser:
    book_url: str
    book_requests: list
    book_data: BookData
    book_folder: Path

    def __init__(self, url, output_folder):
        self.book_url = url
        self.book_requests = self.get_book_requests()
        book_json, m3u8_url = self.analyse_book_requests()
        book_json['m3u8_url'] = m3u8_url
        book_json['title'] = sanitize_filename(book_json['title'])
        book_json['chapters'] = json.loads(book_json['items'])
        self.book_data = BookData(book_json)
        self.create_book_folder(output_folder)

    def get_book_requests(self) -> list:
        print("Getting book requests. Please wait...")
        service = ChromeService(executable_path=ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        with webdriver.Chrome(service=service, options=options) as driver:
            driver.get(self.book_url)
            return driver.requests

    def analyse_book_requests(self) -> tuple:
        print('Analysing book requests...')
        try:
            # find request with book json data
            book_json_requests = [r for r in self.book_requests if r.method == 'POST' and r.path.startswith('/ajax/b/')]
            # assert that we have only 1 request for book data found
            assert len(book_json_requests) == 1, 'Error: Book data not found. Exiting.'
            print('Book data found')
            # find request with m3u8 file
            m3u8_file_requests = [r for r in self.book_requests if 'm3u8' in r.url]
            # assert that we have only 1 request for m3u8 file found
            assert len(m3u8_file_requests) == 1, 'Error: m3u8 file request not found. Exiting.'
            print('m3u8 file found')
            book_json = json.loads(brotli.decompress(book_json_requests[0].response.body))
            return book_json, m3u8_file_requests[0].url
        except AssertionError as message:
            print(message)
            exit()

    def create_book_folder(self, output_folder: str):
        output_path = output_folder if Path(output_folder).is_absolute() else Path(__file__).parent / output_folder
        self.book_folder = Path(output_path) / self.book_data.title
        Path(self.book_folder).mkdir(parents=True, exist_ok=True)

    def separate_into_chapters(self, full_mp3_filepath: Path):
        print('Separating chapters. Please wait...')
        for chapter in self.book_data.chapters:
            chapter_path = self.book_folder / sanitize_filename(chapter['title'])
            ffmpeg_command = ['ffmpeg', '-i', f'{full_mp3_filepath}.mp3', '-acodec', 'copy', '-ss',
                              str(chapter['time_from_start']), '-to', str(chapter['time_finish']),
                              f'{chapter_path}.mp3']
            subprocess.run(ffmpeg_command)

    def download_book(self, single_chapter: bool = False):
        print('Downloading book. Please wait...')
        if single_chapter:
            filepath = self.book_folder / self.book_data.chapters[0]['title']
        else:
            filepath = self.book_folder / self.book_data.title

        requests.get(self.book_data.m3u8_url)
        ffmpeg_command = ['ffmpeg', '-i', self.book_data.m3u8_url, f'{filepath}.mp3']
        subprocess.run(ffmpeg_command)

    def run(self, delete_full_book_folder: bool = False, separate_into_chapters: bool = True):
        if len(self.book_data.chapters) < 1:
            return
        if len(self.book_data.chapters) == 1 or not separate_into_chapters:
            if len(self.book_data.chapters) == 1:
                print("Only 1 chapter found")
            else:
                print("Multiple chapters found")

            print("Downloading full book without chapters separation")
            self.download_book(single_chapter=True)  # download directly in book folder
            return

        print("Multiple chapters found")
        full_book_folder = self.book_folder
        Path(full_book_folder).mkdir(exist_ok=True)

        print(
            f"Downloading full book with chapters separation, {'deleting' if delete_full_book_folder else 'keeping'} full book folder afterwards")

        self.download_book(single_chapter=False)
        self.separate_into_chapters(full_book_folder / self.book_data.title)

        if delete_full_book_folder:
            shutil.rmtree(full_book_folder, ignore_errors=True)

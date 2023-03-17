import subprocess
import sys

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path

url = sys.argv[1]
output_folder = sys.argv[2]

# check command line for original file and track list file
if len(sys.argv) != 3:
    print("usage: python akniga_sep.py <book_url> <output_folder>")
    exit(1)


def get_audio_link(url):
    service = ChromeService(executable_path=ChromeDriverManager().install())
    options = webdriver.ChromeOptions()

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    audio_tag = driver.find_elements(by=By.TAG_NAME, value="audio")[1]
    return audio_tag.get_attribute('src')


def download_audio_file(url, title, folder):
    book_original_title = Path(folder).joinpath(title +'.mp3')

    print(f'Downloading {book_original_title}\nTo: {folder}\nPlease wait...')
    # download full book .mp3 file
    with open(book_original_title, 'wb') as file:
        file.write(requests.get(get_audio_link(url)).content)


def get_book_title(soup):
    return soup.find("h1", {"class": "caption__article-main"}).text


def generate_track_list(soup, folder):
    # get div with classes [bookpage--chapters, player--chapters]
    div_main = soup.find("div", {"class": "bookpage--chapters"})
    chapters = div_main.find_all("div", {"class": "chapter__default"})

    # audio_markup = [(start, end, name)]
    audio_markup = []
    audio_cursor = 0

    for i, chapter in enumerate(chapters[:-1]):
        # define chapter name
        chapter_name = chapter.contents[3].text

        # define chapter length
        chapter_start = audio_cursor
        chapter_end = int(chapters[i + 1].attrs['data-pos'])
        audio_cursor = chapter_end

        # add chapter to markup
        audio_markup.append((chapter_start, chapter_end, chapter_name))

    # add last chapter
    min, sec = chapters[-1].contents[1].text.split(':')

    audio_markup.append((audio_cursor,
                         audio_cursor + int(min) * 60 + int(sec),
                         chapters[-1].contents[3].text))

    track_file = Path(folder).joinpath('track_list.txt')
    with open(track_file, 'w', encoding='utf8') as file:
        for line in audio_markup:
            print(*line, sep=',', file=file)


def separate_audio(temp_folder, title, folder):
    """split a music track into specified sub-tracks by calling ffmpeg from the shell"""

    # read each line of the track list and split into start, end, name
    with open(Path(temp_folder).joinpath('track_list.txt'), "r", encoding='utf8') as track_list_file:
        original_file = Path(temp_folder).joinpath(title + '.mp3')
        for line in track_list_file:
            # skip comment and empty lines
            if line.startswith("#") or len(line) <= 1:
                continue

            # create command string for a given track
            start, end, name = line.strip().split(',')
            out_name = Path(folder).joinpath(name + '.mp3')
            command = f'ffmpeg -i "{original_file}" -acodec copy -ss {start} -to {end} "{out_name}"'

            # use subprocess to execute the command in the shell
            p = subprocess.run(command, shell=True, capture_output=True)
            print(p.stdout.decode())
            print(p.stderr.decode())


if __name__ == '__main__':
    # init session
    session = requests.Session()

    user = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    header = {
        'user-agent': user
    }
    response = session.get(url=url, headers=header)
    soup = BeautifulSoup(response.content, 'html.parser')

    working_folder = Path(output_folder).joinpath(get_book_title(soup))
    temp_folder = working_folder.joinpath('original')
    working_folder.mkdir(exist_ok=True)
    temp_folder.mkdir(exist_ok=True)
    download_audio_file(url=url, title=get_book_title(soup), folder=temp_folder)
    generate_track_list(soup=soup, folder=temp_folder)
    separate_audio(temp_folder=temp_folder, title=get_book_title(soup), folder=working_folder)

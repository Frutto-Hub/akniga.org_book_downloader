# Akniga.org book separator
Akniga.org book separator is a simple python script for splitting akniga.org huge audio file (a whole book) into many audio files (by chapters).
# Requirements:
### Python libs:
1. requests
1. beautifulsoup4 
1. selenium
1. webdriver-manager
1. pathlib

You can install python libs with simple command for terminal:
```
pip install requests beautifulsoup4 selenium webdriver-manager pathlib
```

ffmpeg is also required
* [Here](https://www.youtube.com/watch?v=jZLqNocSQDM) is a tutorial on how to install ffmpeg for Windows users.
* Make sure you've added ffmpeg.exe path to PATH environment variable as on the video

# Usage:
command for terminal:

```
python akniga_sep.py <book_url> <output_folder>
```
Where:
- <book_url> is a url to book you want to download
- <output_folder> is an absolute path to download folder

# Akniga.org book downloader
Akniga.org book downloader is a simple python script for downloading books from akniga.org.

You can install all essential packages with simple command in terminal:
```
pip install -r requirements.txt
```

ffmpeg is also required
* [Here](https://www.youtube.com/watch?v=jZLqNocSQDM) is a tutorial on how to install ffmpeg for Windows users.
* Make sure you've added ffmpeg.exe path to PATH environment variable as on the video

# Usage:
usage: akniga_dl.py [-h] [-f] url output
if you know what to do, you can do easier:
watch commented lines in main.py

Download a book from akniga.org

positional arguments:
  url           Book's url for downloading
  output        Absolute or relative path where book will be downloaded

options:
  -h, --help    show this help message and exit
  -f, --full    Do not separate the book into multiple chapters, if any

Where:
- url is a url to book you want to download
- output is an absolute (or relative to the akniga_dl.py file) path to download folder

import argparse
from akniga_parser import AKnigaParser


def parse_from_console():
    parser = argparse.ArgumentParser(description='Download a book from akniga.org')
    parser.add_argument('url', help='Book\'s url for downloading')
    parser.add_argument('output', help='Absolute or relative path where book will be downloaded')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f', '--full', action='store_true',
                       help='Do not separate the book into multiple chapters, if any')
    args = parser.parse_args()
    AKnigaParser(args.url, args.output).run(not args.f)


if __name__ == "__main__":
    parse_from_console()


# OR
# files = [
#   'https://akniga.org/url1',
#   'https://akniga.org/url2',
# ]
#
# for url in files:
#     AKnigaParser(url, '').run(True)

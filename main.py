import argparse
from AKnigaParser import AKnigaParser


def parse_from_console():
    parser = argparse.ArgumentParser(description='Download a book from akniga.org')
    parser.add_argument('url', help='Book\'s url for downloading')
    parser.add_argument('output', help='Absolute or relative path where book will be downloaded')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--delete', action='store_true',
                       help='Delete full book folder, after chapter separation is done')
    group.add_argument('-f', '--full', action='store_true',
                       help='Do not separate the book into multiple chapters, if any')
    args = parser.parse_args()
    AKnigaParser(args.url, args.output).run(args.d, not args.f)


# if __name__ == "__main__":
#    parse_from_console()

AKnigaParser("https://akniga.org/magonote-rifudzin-tekuschee-polozhenie-1", "./").run(False, True)

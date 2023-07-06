import argparse
import sys
from pprint import pprint

from azlyrics_api.api import AZLyricsAPI
from azlyrics_api.export import export_to_xml


def get_args() -> argparse.Namespace:
    """Parse arguments and return Namespace instance."""
    parser = argparse.ArgumentParser(
        prog="azlyrics_api",
        description="Get song information from AZLyrics.",
        epilog="AZLyrics API - Copyright (C) 2023 Zack Didcott",
    )
    parser.add_argument(
        "query",
        nargs="*",
        type=str,
        help="search query for the song, e.g. title artist",
    )
    parser.add_argument(
        "--xml", type=str, help="file path or directory to export song as XML"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="output debugging information"
    )
    args = parser.parse_args()

    if not args.query:
        parser.error("'query' not specified.")

    return args


def main() -> None:
    """Parse arguments and run interactively."""
    args = get_args()
    api = AZLyricsAPI()
    try:
        song = api.query(args.query[0], args.query[1])
    except Exception:
        query = " ".join(args.query)
        song = api.search(query, interactive=True)
        if not song:
            print("Song not found.")
            sys.exit(1)
    if args.xml:
        export_to_xml(song, args.xml)
    if args.verbose:
        pprint(song)
    else:
        print(song.lyrics)


if __name__ == "__main__":
    main()

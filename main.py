import re
import string
from dataclasses import dataclass
from itertools import count
from pathlib import Path
from typing import Optional

import lxml.builder
import lxml.etree
import requests
from bs4 import BeautifulSoup


@dataclass
class Song:
    """Dataclass to store information about a song."""

    title: str
    artist: str
    lyrics: str
    url: str


class AZLyricsAPI:
    """Class to handle AZLyrics API methods."""

    API_URL = "https://www.azlyrics.com"
    SEARCH_URL = "https://search.azlyrics.com/search.php"
    SEARCH_X = "83e3793dba11c730f7c3ca957a2b7dbfd7150a976ca1359db1f3dd5114a546db"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; rv:114.0) Gecko/20100101 Firefox/114.0"

    @property
    def HTTP_HEADERS(self) -> dict[str, str]:
        """Return HTTP headers."""
        return {"User-Agent": self.USER_AGENT}

    @staticmethod
    def parse_url(url: str) -> dict[str, str]:
        """Return title and artist from URL."""
        artist, title = re.match(r".*\/(.*)\/(.*)\.html", url).groups()
        return {"artist": artist, "title": title}

    def search(
        self, query: str, interactive: bool = False
    ) -> list[Song] | Optional[Song]:
        """Return list of search results from query."""
        results = []
        response = requests.get(
            f"{self.SEARCH_URL}?q={query}&x={self.SEARCH_X}", headers=self.HTTP_HEADERS
        )
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table")
        if not table:
            return results
        for link in table.find_all("a"):
            url = link.get("href")
            if ".html" not in url:
                continue
            results.append(self.query(**self.parse_url(url)))
        if interactive:
            return self._search_interactive(results)
        return results

    def _search_interactive(self, results: list[Song]) -> Optional[Song]:
        """Select song from search results interactively."""
        for n, song in enumerate(results):
            print(f"{n}. {song.title} - {song.artist} | {song.url}")
        try:
            idx = int(input("Select song index: "))
            return results[idx]
        except (Exception, KeyboardInterrupt):
            return None

    def query(self, title: str, artist: str) -> Song:
        """Return song instance from title and artist."""
        stripped_chars = str.maketrans("", "", string.punctuation + " ")
        title = title.lower().translate(stripped_chars)
        artist = artist.lower().translate(stripped_chars)
        url = f"{self.API_URL}/lyrics/{artist}/{title}.html"
        response = requests.get(url, headers=self.HTTP_HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        res_title = (
            soup.select(".col-xs-12 > b:nth-child(5)")[0].getText().replace('"', "")
        )
        try:
            res_artist = soup.select(
                ".lyricsh > h2:nth-child(1) > a:nth-child(1) > b:nth-child(1)"
            )[0]
        except IndexError:
            res_artist = soup.select(".lyricsh > h2:nth-child(1) > b:nth-child(1)")[0]
        res_artist = res_artist.getText().rstrip(" Lyrics")
        lyrics = (
            soup.find_all("div", attrs={"class": None, "id": None})[0]
            .getText()
            .strip("\n\r")
        )
        return Song(title=res_title, artist=res_artist, lyrics=lyrics, url=url)


def export_to_xml(song: Song, path: Optional[str | Path] = None) -> str:
    """Export song to XML."""
    counter = count(2)
    tagged_lyrics = "[V1]\n" + re.sub(
        r"\n\n", lambda x: f"\n\n[V{next(counter)}]\n", song.lyrics
    )
    parsed_lyrics = ""
    for line in tagged_lyrics.splitlines():
        if line and not line.startswith("["):
            parsed_lyrics += f" {line}"
        else:
            parsed_lyrics += line
        parsed_lyrics += "\n"
    E = lxml.builder.ElementMaker()
    tree = E.song(E.title(song.title), E.author(song.artist), E.lyrics(parsed_lyrics))
    xml = lxml.etree.tostring(
        tree, encoding="UTF-8", xml_declaration=True, pretty_print=True
    ).decode()
    if path:
        path = Path(path)
        if path.is_dir():
            path /= f"{song.title} - {song.artist}"
        with open(path, "w") as fd:
            fd.write(xml)
    return xml


if __name__ == "__main__":
    import argparse
    import sys
    from pprint import pprint

    parser = argparse.ArgumentParser(
        description="Get song information from AZLyrics.",
        epilog="AZLyrics API - Copyright (C) 2023 Zack Didcott",
    )
    parser.add_argument(
        "query",
        nargs="*",
        metavar="title | artist",
        type=str,
        help="search query for the song",
    )
    parser.add_argument(
        "--xml", type=str, help="file path or directory to export song as XML"
    )
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

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

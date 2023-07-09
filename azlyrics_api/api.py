import re
import string
from typing import Optional

import requests
from bs4 import BeautifulSoup

from azlyrics_api.models import Song


class AZLyricsAPI:
    """Class to handle AZLyrics API methods."""

    API_URL = "https://www.azlyrics.com"
    SEARCH_URL = "https://search.azlyrics.com/search.php"
    SEARCH_X_URL = "https://www.azlyrics.com/geo.js"
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
            f"{self.SEARCH_URL}?q={query}&x={self._search_get_x()}",
            headers=self.HTTP_HEADERS,
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

    def _search_get_x(self) -> str:
        """Get x value for search URL parameter."""
        js = requests.get(self.SEARCH_X_URL, headers=self.HTTP_HEADERS).text
        x = re.search(r'ep.setAttribute\("value", "(.*)"\);', js).group(1)
        return x

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

import time
import requests
from bs4 import BeautifulSoup
from ScrapeSearchEngine.SearchEngine import Google
from urllib.parse import urlparse

_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'
_sites = [
    "tekstowo.pl",
    "genius.com"
    ]
_sites_query = ' OR '.join(map(lambda s: f'site:{s}', _sites))

class LyricScraperException(Exception):
    """Handles all lyrics extractor exceptions."""

class _ScraperFactory:
    """All scrapers are defined here."""

    source_code = None
    title = None

    def __call__(self, source_code, title):
        self.source_code = source_code
        self.title = title

    def _update_title(self, title):
        self.title = title

    def _genius_scraper_method_1(self):
        extract = self.source_code.select(".lyrics")
        if not extract:
            return None

        lyrics = (extract[0].get_text()).replace('<br>', '\n').strip()
        return lyrics

    def _genius_scraper_method_2(self):
        all_extracts = self.source_code.select(
            'div[class*="Lyrics__Container-sc-"]')
        if not all_extracts:
            return None

        lyrics = ''
        for extract in all_extracts:
            for br in extract.find_all("br"):
                br.replace_with("\n")
            lyrics += extract.get_text()

        return lyrics.strip()

    def genius_scraper(self):
        lyrics = self._genius_scraper_method_1() or self._genius_scraper_method_2()
        self._update_title(self.title[:-16])

        return lyrics

    def tekstowo_scraper(self):
        extract = self.source_code.select(".song-text")
        if not extract:
            return None
        for el in extract[0].find_all(['h2', 'div', 'p', 'a']):
            el.decompose()
        lyrics = (extract[0].get_text()).replace('<br>', '\n').strip()
        return lyrics

class SongLyrics:
    """
        Call get_lyrics function with song_name as args to get started.
        Handle raised LyricScraperException by importing it alongside.
    """

    scraper_factory = _ScraperFactory()
    scrapers = {
        'tekstowo': scraper_factory.tekstowo_scraper,
        'genius': scraper_factory.genius_scraper
    }

    def __handle_search_request(self, song_name: str):
        query = f'{song_name.replace("-", " ")} {_sites_query}'
        titles, links = Google(query, _user_agent)
        if len(links) == 1 and not urlparse(links[0]).path:
            raise LyricScraperException(links[0])
        return list(map(lambda t, l: {'title':t, 'link': l}, titles, links))

    def __extract_lyrics(self, result_url, title):
        page = requests.get(result_url)
        source_code = BeautifulSoup(page.content, 'lxml')

        self.scraper_factory(source_code, title)
        for domain, scraper in self.scrapers.items():
            if domain in result_url:
                lyrics = scraper()
        return lyrics

    def get_lyrics(self, song_name: str) -> dict:

        query_results = self.__handle_search_request(song_name)

        for i in range(len(query_results)):
            result_url = query_results[i]["link"]
            title = query_results[i]["title"]
            try:
                lyrics = self.__extract_lyrics(result_url, title)
            except Exception as err:
                raise LyricScraperException(err)

            if lyrics:
                return {
                    "title": self.scraper_factory.title,
                    "lyrics": lyrics
                }

        raise LyricScraperException({"error": "No results found"})

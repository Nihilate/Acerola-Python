import requests
import logging

from pyquery import PyQuery
from typing import List, Dict

from ..errors import ResponseException
from ..response_types import Anime
from ..enums import DataSource

BASE_URL = 'http://anisearch.outrance.pl/?task=search&query='


class AniDB:
    def __init__(self, config):
        self.source_type = DataSource.ANIDB
        self.timeout = config['Timeout']
        self.logger = logging.getLogger('AcerolaLogger')
        self.session = requests.Session()

    def search_anime(self, search_term) -> List[Anime]:
        try:
            result = self.session.get(BASE_URL + search_term, timeout=int(self.timeout))

            if result.status_code != 200:
                raise ResponseException('Failed to find results for: ' + search_term)

            pq_results = PyQuery(result.content)

            parsed_results = AniDB.parse_anime(pq_results)

            return parsed_results

        except Exception as e:
            # todo log that shit
            self.logger.error('AP error: ' + str(e))
            return []
        finally:
            self.session.close()

    @staticmethod
    def parse_anime(results) -> List[Anime]:
        anime_list = []

        for anime in results('animetitles anime'):
            title_info = AniDB.process_titles(PyQuery(anime).find('title').items())
            anime_list.append(Anime(id=int(anime.attrib['aid']),
                                    urls={DataSource.ANIDB: 'http://anidb.net/a' + anime.attrib['aid']},
                                    title_english=next((title['title'] for title in title_info if title['lang'] == 'en' and title['type'] in ['main', 'official']), None),
                                    title_romaji=next((title['title'] for title in title_info if title['lang'] == 'x-jat' and title['type'] in ['main', 'official']), None),
                                    title_japanese=next((title['title'] for title in title_info if title['lang'] == 'ja' and title['type'] in ['main', 'official']), None),
                                    synonyms=set([title['title'] for title in title_info if title['type'] == 'syn'])))

        return anime_list

    @staticmethod
    def process_titles(title_items) -> List[Dict]:
        titles = []
        for title in title_items:
            title_info = {'title': title.text(), 'lang': title.attr['lang'], 'type': title.attr['type']}
            titles.append(title_info)
        return titles


import requests
import logging

from pyquery import PyQuery
from typing import List, Dict

from ..errors import NoResultsFound, DataSourceTimeoutError, DataSourceUnavailableError, AcerolaError

from ..response_types import Anime
from ..enums import DataSource

BASE_URL = 'http://anisearch.outrance.pl/?task=search&query='


class AniDB:
    source_type = DataSource.ANIDB

    def __init__(self, config):
        self.timeout = int(config['Timeout'])
        self.logger = logging.getLogger('AcerolaLogger')
        self.session = requests.Session()

    # todo logging decorator?
    def anidb_search(self, search_term, parser):
        try:
            response = self.session.get(BASE_URL + search_term, timeout=self.timeout)
            response.raise_for_status()

            results = parser(PyQuery(response.content))

            if not results:
                raise NoResultsFound(AniDB.source_type, search_term)

            return results
        except NoResultsFound:
            raise
        except requests.exceptions.Timeout:
            raise DataSourceTimeoutError(AniDB.source_type)
        except requests.exceptions.RequestException:
            raise DataSourceUnavailableError(AniDB.source_type)
        except Exception as e:
            raise AcerolaError(e)
        finally:
            self.session.close()

    def search_anime(self, search_term):
        return self.anidb_search(search_term, self.parse_anime)

    @staticmethod
    def parse_anime(results):
        anime_list = []

        for anime in results('animetitles anime'):
            title_info = AniDB.process_titles(PyQuery(anime).find('title').items())
            anime_list.append(Anime(id=int(anime.attrib['aid']),
                                    url='http://anidb.net/a' + anime.attrib['aid'],
                                    title_english=next((title['title'] for title in title_info if title['lang'] == 'en' and title['type'] in ['main', 'official']), None),
                                    title_romaji=next((title['title'] for title in title_info if title['lang'] == 'x-jat' and title['type'] in ['main', 'official']), None),
                                    title_japanese=next((title['title'] for title in title_info if title['lang'] == 'ja' and title['type'] in ['main', 'official']), None),
                                    synonyms=set([title['title'] for title in title_info if title['type'] == 'syn'])))

        return anime_list

    @staticmethod
    def process_titles(title_items):
        titles = []
        for title in title_items:
            title_info = {'title': title.text(), 'lang': title.attr['lang'], 'type': title.attr['type']}
            titles.append(title_info)
        return titles


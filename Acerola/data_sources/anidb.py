import logging
import os
import time
from functools import wraps

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from bs4 import BeautifulSoup

from ..errors import NoResultsFound, DataSourceTimeoutError, DataSourceUnavailableError, AcerolaError

from ..response_types import Anime
from ..enums import DataSource

# todo add constants
HOUR = 3600


class AniDB:
    source_type = DataSource.ANIDB

    # todo better handling if there's no config
    def __init__(self, config):
        self.logger = logging.getLogger('AcerolaLogger')
        self.path_to_xml = str(config['path_to_xml'])
        self.path_to_database = str(config['path_to_database'])
        self.auto_refresh_database = config['auto_refresh_database']

        try:
            self.next_time_to_update = os.path.getmtime(self.path_to_database) + (HOUR * 36)
        except FileNotFoundError:
            self.next_time_to_update = int(time.time()) - 1

        self.titles_db = TinyDB(self.path_to_database, storage=CachingMiddleware(JSONStorage))

    def refresh_database(self):
        if int(time.time()) > self.next_time_to_update:
            try:
                with open(self.path_to_xml, 'r', encoding='utf-8') as titles_file:
                    soup = BeautifulSoup(titles_file, 'lxml')

                    titles = []

                    for anime in soup.find_all('anime'):
                        anime_info = {}
                        anime_info['id'] = anime['aid']
                        anime_info['url'] = 'http://anidb.net/perl-bin/animedb.pl?show=anime&aid=' + anime['aid']
                        anime_info['main'] = anime.find('title', {'type': 'main'}).text if anime.find('title', {'type': 'main'}) else None
                        anime_info['english'] = anime.find('title', {'type': 'official', 'xml:lang': 'en'}).text if anime.find('title', {'type': 'official', 'xml:lang': 'en'}) else None
                        anime_info['synonyms'] = set(title.text for title in anime.find_all('title', {'xml:lang': ['en', 'x-jat']}))

                        titles.append(anime_info)

                with self.titles_db as titles_db:
                    titles_db.purge()
                    titles_db.insert_multiple(titles)

                self.next_time_to_update += HOUR * 36

            except FileNotFoundError:
                print('XML file doesn\'t exist')
            except Exception as e:
                print(e)

    # todo logging decorator?
    def search_anime(self, search_term):
        if self.auto_refresh_database:
            self.refresh_database()

        with self.titles_db as database:
            results = database.search(Query().synonyms.test(self.contains_search_term, search_term))
            if results:
                anime_list = []
                for result in results:
                    anime_list.append(Anime(id=result['id'],
                                            url=result['url'],
                                            title_english=result['english'],
                                            title_romaji=result['main'],
                                            synonyms=set(result['synonyms'])))

                return anime_list
            else:
                raise NoResultsFound(self.source_type, search_term)

    def get_anime(self, id):
        if self.auto_refresh_database:
            self.refresh_database()

        with self.titles_db as database:
            results = database.search(Query().id == id)
            if results:
                anime_list = []
                for result in results:
                    anime_list.append(Anime(id=result['id'],
                                            url=result['url'],
                                            title_english=result['english'],
                                            title_romaji=result['main'],
                                            synonyms=set(result['synonyms'])))

                return anime_list
            else:
                raise NoResultsFound(self.source_type, id)


    @staticmethod
    def contains_search_term(synonyms, search_term):
        return True if [synonym for synonym in synonyms if search_term.lower() in synonym.lower()] else False
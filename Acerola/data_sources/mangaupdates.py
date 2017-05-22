import requests
import logging

from pyquery import PyQuery
from typing import List

from ..errors import ResponseException
from ..response_types import Manga, LightNovel
from ..enums import DataSource

BASE_URL = 'https://mangaupdates.com/series.html'


class MangaUpdates:
    def __init__(self, config):
        self.timeout = config['Timeout']
        self.logger = logging.getLogger('AcerolaLogger')
        self.session = requests.Session()

    def get_thing(self, search_term, parser) -> List:
        try:
            result = self.session.get(BASE_URL,
                                      params={'search': search_term},
                                      timeout=int(self.timeout))

            if result.status_code != 200:
                raise ResponseException('Failed to find results for: ' + search_term) # this error message is shit

            parsed_results = parser(PyQuery(result.content))

            return parsed_results

        except Exception as e:
            # todo log that shit
            self.logger.error('MU error: ' + str(e))
            return []
        finally:
            self.session.close()

    # The irony is that get_manga and get_light_novel effectively do the same thing - there's no way to tell the difference from the search page :(
    def get_manga(self, search_term) -> List[Manga]:
        return self.get_thing(search_term, self.parse_manga)

    def get_light_novel(self, search_term) -> List[LightNovel]:
        return self.get_thing(search_term, self.parse_light_novel)

    @staticmethod
    def parse_manga(results) -> List[Manga]:
        manga_list = []

        for thing in results.find('.series_rows_table tr'):
            manga_list.append(Manga(title_english=PyQuery(thing).find('.col1').text(),
                                    urls={DataSource.MANGAUPDATES: PyQuery(thing).find('.col1 a').attr('href')}))

        return manga_list

    @staticmethod
    def parse_light_novel(results) -> List[LightNovel]:
        ln_list = []

        for thing in results.find('.series_rows_table tr'):
            ln_list.append(LightNovel(title_english=PyQuery(thing).find('.col1').text(),
                                      urls={DataSource.MANGAUPDATES: PyQuery(thing).find('.col1 a').attr('href')}))

        return ln_list

import requests
import logging

from pyquery import PyQuery

from ..errors import ResponseException
from ..enums import DataSource, Type

from ..response_types import Anime, Manga, LightNovel

BASE_URL = 'http://www.anime-planet.com'
ANIME_ENDPOINT = '/anime/all?name='
MANGA_ENDPOINT = '/manga/all?name='


class AnimePlanet:
    def __init__(self, config):
        self.timeout = config['Timeout']
        self.logger = logging.getLogger('AcerolaLogger')
        self.session = requests.Session()

    def get_items(self, search_term, endpoint, parser):
        try:
            result = self.session.get(BASE_URL + endpoint + search_term, timeout=int(self.timeout))

            if result.status_code != 200:
                raise ResponseException('Failed to find results for: ' + search_term)

            pq_result = PyQuery(result.text)

            blah = pq_result.find('.error').text().lower()

            if 'no results' in blah:
                return []

            parsed_results = parser(pq_result)

            return parsed_results
        except Exception as e:
            self.logger.error('AP error: ' + str(e))
            return []
        finally:
            self.session.close()

    def get_anime(self, search_term):
        return self.get_items(search_term, ANIME_ENDPOINT, self.parse_anime)

    def get_manga(self, search_term):
        return self.get_items(search_term, MANGA_ENDPOINT, self.parse_manga)

    def get_light_novel(self, search_term):
        return self.get_items(search_term, MANGA_ENDPOINT, self.parse_light_novel)

    # TODO Grab genres as well as build a "recommend me a thing" functionality
    @staticmethod
    def parse_anime(results):
        anime_list = []

        # Have we been taken to the search page or directly to a series?
        if results.find('.cardDeck.pure-g.cd-narrow[data-type="anime"]'):
            for entry in results.find('.card.pure-1-6'):
                try:
                    anime_list.append(Anime(title_english=PyQuery(entry).find('h4').text(),
                                            urls={DataSource.ANIMEPLANET: BASE_URL + PyQuery(entry).find('a').attr('href')}))
                except AttributeError:
                    pass  # todo - logging here
        else:
            try:
                anime = Anime(title_english=results.find('h1[itemprop="name"]').text(),
                              urls={DataSource.ANIMEPLANET: results.find("meta[property='og:url']").attr('content')})

                if 'anime' in [url for url in anime.urls.items()]:
                    anime_list.append(anime)
            except AttributeError:
                pass  # todo - logging here

        return anime_list

    @staticmethod
    def parse_manga(results):
        manga_list = []

        # Have we been taken to the search page or directly to a series?
        if results.find('.cardDeck.pure-g.cd-narrow[data-type="manga"]'):
            for entry in results.find('.card.pure-1-6'):
                try:
                    manga = Manga(title_english=PyQuery(entry).find('h4').text(),
                                  urls={DataSource.ANIMEPLANET: BASE_URL + PyQuery(entry).find('a').attr('href')})

                    if '<li>Light Novel</li>' not in PyQuery(entry).find('a').attr('title'):
                        manga_list.append(manga)
                except AttributeError:
                    pass  # todo - logging here
        else:
            try:
                manga = Manga(title_english=results.find('h1[itemprop="name"]').text(),
                              urls={DataSource.ANIMEPLANET: results.find("meta[property='og:url']").attr('content')})

                if not results.find('a[href="/manga/tags/light-novel"]') and 'anime' not in [url for url in manga.urls.items()]:
                    manga_list.append(manga)
            except AttributeError:
                pass  # todo - logging here

        return manga_list

    @staticmethod
    def parse_light_novel(results):
        ln_list = []

        # Have we been taken to the search page or directly to a series?
        if results.find('.cardDeck.pure-g.cd-narrow[data-type="manga"]'):
            for entry in results.find('.card.pure-1-6'):
                try:
                    ln = LightNovel(title_english=PyQuery(entry).find('h4').text(),
                                    urls={DataSource.ANIMEPLANET: BASE_URL + PyQuery(entry).find('a').attr('href')},
                                    type=Type.LIGHT_NOVEL,
                                    synonyms={PyQuery(entry).find('a').text().replace('(Light Novel)', '').rstrip()})

                    if '<li>Light Novel</li>' in PyQuery(entry).find('a').attr('title'):
                        ln_list.append(ln)
                except AttributeError:
                    pass  # todo - logging here
        else:
            try:

                ln = LightNovel(title_english=results.find('h1[itemprop="name"]').text(),
                                urls={DataSource.ANIMEPLANET: results.find("meta[property='og:url']").attr('content')},
                                type=Type.LIGHT_NOVEL,
                                synonyms={results.find('h1[itemprop="name"]').text().replace('(Light Novel)', '').rstrip()})

                if results.find('a[href="/manga/tags/light-novel"]') and 'anime' not in [url for url in ln.urls.items()]:
                    ln_list.append(ln)
            except AttributeError:
                pass  # todo - logging here

        return ln_list

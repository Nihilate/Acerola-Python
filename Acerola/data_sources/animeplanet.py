import requests
import logging

from pyquery import PyQuery

from ..errors import NoResultsFound, DataSourceTimeoutError, DataSourceUnavailableError, AcerolaError
from ..enums import DataSource, Type

from ..response_types import Anime, Manga, LightNovel

BASE_URL = 'http://www.anime-planet.com'
ANIME_ENDPOINT = '/anime/all?name='
MANGA_ENDPOINT = '/manga/all?name='


class AnimePlanet:
    source_type = DataSource.ANIMEPLANET

    def __init__(self, config):
        self.timeout = int(config['Timeout'])
        self.logger = logging.getLogger('AcerolaLogger')
        self.session = requests.Session()

    # todo logging decorator?
    def ap_search(self, endpoint, search_term, parser):
        try:
            response = self.session.get(BASE_URL + endpoint + search_term, timeout=self.timeout)
            response.raise_for_status()

            xml_response = PyQuery(response.text)
            error_message = xml_response.find('.error').text().lower()

            if 'no results' in error_message:
                raise NoResultsFound(AnimePlanet.source_type, search_term)

            results = parser(xml_response)

            if not results:
                raise NoResultsFound(AnimePlanet.source_type, search_term)

            return results
        except NoResultsFound:
            raise
        except requests.exceptions.Timeout:
            raise DataSourceTimeoutError(AnimePlanet.source_type)
        except requests.exceptions.RequestException:
            raise DataSourceUnavailableError(AnimePlanet.source_type)
        except Exception as e:
            raise AcerolaError(e)
        finally:
            self.session.close()

    def search_anime(self, search_term):
        return self.ap_search(ANIME_ENDPOINT, search_term, self.parse_anime)

    def search_manga(self, search_term):
        return self.ap_search(MANGA_ENDPOINT, search_term, self.parse_manga)

    def search_light_novel(self, search_term):
        return self.ap_search(MANGA_ENDPOINT, search_term, self.parse_light_novel)

    # TODO Grab genres as well as build a "recommend me a thing" functionality, add synonyms
    @staticmethod
    def parse_anime(results):
        anime_list = []

        # Have we been taken to the search page or directly to a series?
        if results.find('.cardDeck.pure-g.cd-narrow[data-type="anime"]'):
            for entry in results.find('.card.pure-1-6'):
                try:
                    anime_list.append(Anime(title_english=PyQuery(entry).find('h4').text(),
                                            url=BASE_URL + PyQuery(entry).find('a').attr('href')))
                except AttributeError:
                    pass  # todo - logging here
        else:
            try:
                anime = Anime(title_english=results.find('h1[itemprop="name"]').text(),
                              url=results.find("meta[property='og:url']").attr('content'))

                if 'anime' in anime.url:
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
                                  url=BASE_URL + PyQuery(entry).find('a').attr('href'))

                    if '<li>Light Novel</li>' not in PyQuery(entry).find('a').attr('title'):
                        manga_list.append(manga)
                except AttributeError:
                    pass  # todo - logging here
        else:
            try:
                manga = Manga(title_english=results.find('h1[itemprop="name"]').text(),
                              url=results.find("meta[property='og:url']").attr('content'))

                if not results.find('a[href="/manga/tags/light-novel"]') and '/anime/' not in manga.url:
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
                                    url=BASE_URL + PyQuery(entry).find('a').attr('href'),
                                    synonyms={PyQuery(entry).find('a').text().replace('(Light Novel)', '').rstrip()})

                    if '<li>Light Novel</li>' in PyQuery(entry).find('a').attr('title'):
                        ln_list.append(ln)
                except AttributeError:
                    pass  # todo - logging here
        else:
            try:

                ln = LightNovel(title_english=results.find('h1[itemprop="name"]').text(),
                                url=results.find("meta[property='og:url']").attr('content'),
                                synonyms={results.find('h1[itemprop="name"]').text().replace('(Light Novel)', '').rstrip()})

                if results.find('a[href="/manga/tags/light-novel"]') and '/anime/' not in ln.url:
                    ln_list.append(ln)
            except AttributeError:
                pass  # todo - logging here

        return ln_list

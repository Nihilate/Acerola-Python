import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt
import logging

from ..errors import NoResultsFound, DataSourceTimeoutError, DataSourceUnavailableError, AccessTokenExpiredError, AcerolaError
from ..enums import Type, Status, DataSource, SeriesSource
from ..util import get_status, get_type, get_series_source

from ..response_types import Anime, Manga, LightNovel

AUTH_URL = 'https://anilist.co/api/auth/access_token'
BASE_URL = 'https://anilist.co/api/'
ANIME_ENDPOINT = 'anime/search/'
MANGA_ENDPOINT = 'manga/search/'

TYPE_MAPPING = (['TV', Type.TV],
                ['TV Short', Type.TV],
                ['Movie', Type.MOVIE],
                ['Special', Type.SPECIAL],
                ['OVA', Type.OVA],
                ['ONA', Type.ONA],
                ['Music', Type.OTHER],
                ['Manga', Type.MANGA],
                ['Novel', Type.LIGHT_NOVEL],
                ['One Shot', Type.ONE_SHOT],
                ['Doujin', Type.DOUJINSHI],
                ['Manhwa', Type.MANHWA],
                ['Manhua', Type.MANHUA])

STATUS_MAPPING = (['finished airing', Status.FINISHED],
                  ['currently airing', Status.ONGOING],
                  ['not yet aired', Status.UPCOMING],
                  ['finished publishing', Status.FINISHED],
                  ['publishing', Status.ONGOING],
                  ['not yet published', Status.UPCOMING],
                  ['cancelled', Status.CANCELLED])

SERIES_SOURCE_MAPPING = (['Original', SeriesSource.ORIGINAL],
                         ['Manga', SeriesSource.MANGA],
                         ['Light Novel', SeriesSource.LIGHT_NOVEL],
                         ['Visual Novel', SeriesSource.VISUAL_NOVEL],
                         ['Video Game', SeriesSource.VIDEO_GAME],
                         ['Other', SeriesSource.OTHER])


class Anilist:
    source_type = DataSource.ANILIST

    def __init__(self, config):
        self.client_id = config['ClientId']
        self.client_secret = config['ClientSecret']
        self.timeout = int(config['Timeout'])

        self.logger = logging.getLogger('AcerolaLogger')

        self.session = requests.Session()
        self.access_token = None

    def refresh_access_token(self):
        try:
            response = self.session.post(AUTH_URL, params={'grant_type': 'client_credentials', 'client_id': self.client_id, 'client_secret': self.client_secret}, timeout=int(self.timeout))

            response.raise_for_status()

            self.access_token = response.json()['access_token']
        except requests.exceptions.Timeout:
            raise DataSourceTimeoutError(Anilist.source_type)
        except requests.exceptions.RequestException:
            raise DataSourceUnavailableError(Anilist.source_type)
        except Exception as e:
            raise AcerolaError(e)
        finally:
            self.session.close()

    # todo logging decorator?
    @retry(retry=retry_if_exception_type(AccessTokenExpiredError), stop=stop_after_attempt(2))
    def anilist_search(self, endpoint, search_term, parser):
        try:
            search_term = self.sanitise_search_term(search_term)
            response = self.session.get(BASE_URL + endpoint + search_term, params={'access_token': self.access_token}, timeout=self.timeout)

            if response.status_code == 401:
                raise AccessTokenExpiredError(Anilist.source_type)

            response.raise_for_status()

            try:
                error_message = response.json()['error']['messages']
            except TypeError:
                error_message = None

            if error_message and 'No Results.' in error_message:
                raise NoResultsFound(Anilist.source_type, search_term)

            results = parser(response.json())

            if not results:
                raise NoResultsFound(Anilist.source_type, search_term)

            return results
        except NoResultsFound:
            raise
        except AccessTokenExpiredError:
            self.refresh_access_token()
            raise
        except requests.exceptions.Timeout:
            raise DataSourceTimeoutError(Anilist.source_type)
        except requests.exceptions.RequestException:
            raise DataSourceUnavailableError(Anilist.source_type)
        except Exception as e:
            raise AcerolaError(e)
        finally:
            self.session.close()

    def search_anime(self, search_term):
        return self.anilist_search(ANIME_ENDPOINT, search_term, self.parse_anime)

    def search_manga(self, search_term):
        return self.anilist_search(MANGA_ENDPOINT, search_term, self.parse_manga)

    def search_light_novel(self, search_term):
        return self.anilist_search(MANGA_ENDPOINT, search_term, self.parse_light_novel)

    @staticmethod
    def parse_anime(results):
        anime_list = []

        for entry in results:
            try:
                anime_list.append(Anime(id=entry['id'],
                                        url='https://anilist.co/anime/' + str(entry['id']),
                                        title_romaji=entry['title_romaji'],
                                        title_english=entry['title_english'],
                                        title_japanese=entry['title_japanese'],
                                        synonyms=set(entry['synonyms']) if entry['synonyms'] else set(),
                                        genres=set(entry['genres']) if entry['genres'] else set(),
                                        episode_count=(int(entry['total_episodes']) if int(entry['total_episodes']) > 0 else None),
                                        status=get_status(STATUS_MAPPING, entry['airing_status']),
                                        type=get_type(TYPE_MAPPING, entry['type']),
                                        description=entry['description'],
                                        source=get_series_source(SERIES_SOURCE_MAPPING, entry['source']),
                                        nsfw=entry['adult']))
            except AttributeError:
                pass

        return anime_list

    @staticmethod
    def parse_manga(results):
        manga_list = []

        for entry in results:
            try:
                manga = Manga(id=entry['id'],
                              url='https://anilist.co/anime/' + str(entry['id']),
                              title_romaji=entry['title_romaji'],
                              title_english=entry['title_english'],
                              title_japanese=entry['title_japanese'],
                              synonyms=set(entry['synonyms']) if entry['synonyms'] else set(),
                              genres=set(entry['genres']) if entry['genres'] else set(),
                              chapter_count=(int(entry['total_chapters']) if int(entry['total_chapters']) > 0 else None),
                              volume_count=(int(entry['total_volumes']) if int(entry['total_volumes']) > 0 else None),
                              status=get_status(STATUS_MAPPING, entry['publishing_status']),
                              type=get_type(TYPE_MAPPING, entry['type']),
                              description=entry['description'],
                              nsfw=entry['adult'])

                if manga.type != Type.LIGHT_NOVEL:
                    manga_list.append(manga)
            except AttributeError:
                pass

        return manga_list

    @staticmethod
    def parse_light_novel(results):
        ln_list = []

        for entry in results:
            try:
                ln = LightNovel(id=entry['id'],
                                url='https://anilist.co/anime/' + str(entry['id']),
                                title_romaji=entry['title_romaji'],
                                title_english=entry['title_english'],
                                title_japanese=entry['title_japanese'],
                                synonyms=set(entry['synonyms']) if entry['synonyms'] else set(),
                                genres=set(entry['genres']) if entry['genres'] else set(),
                                chapter_count=(int(entry['total_chapters']) if int(entry['total_chapters']) > 0 else None),
                                volume_count=(int(entry['total_volumes']) if int(entry['total_volumes']) > 0 else None),
                                status=get_status(STATUS_MAPPING, entry['publishing_status']),
                                type=get_type(TYPE_MAPPING, entry['type']),
                                description=entry['description'],
                                nsfw=entry['adult'])

                if ln.type == Type.LIGHT_NOVEL:
                    ln_list.append(ln)
            except AttributeError:
                pass

        return ln_list

    @staticmethod
    def sanitise_search_term(text):
        return text.replace('/', ' ')

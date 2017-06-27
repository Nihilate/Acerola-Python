import requests
from retrying import retry
import logging

from ..errors import AccessTokenExpiredException, ResponseException
from ..enums import Type, Status, DataSource, SeriesSource
from ..util import get_status, get_type, get_series_source

from ..response_types import Anime, Manga, LightNovel

AUTH_URL = 'https://anilist.co/api/auth/access_token'
BASE_API = 'https://anilist.co/api/'
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


def retry_if_access_token_needs_refreshing(exception):
    return isinstance(exception, AccessTokenExpiredException)


class Anilist:
    def __init__(self, config):
        self.client_id = config['ClientId']
        self.client_secret = config['ClientSecret']
        self.timeout = config['Timeout']

        self.logger = logging.getLogger('AcerolaLogger')

        self.session = requests.Session()
        self.access_token = None

    def refresh_access_token(self):
        token_result = self.session.post(AUTH_URL,
                                         params={'grant_type': 'client_credentials',
                                                 'client_id': self.client_id,
                                                 'client_secret': self.client_secret},
                                         timeout=int(self.timeout))
        self.access_token = token_result.json()['access_token']

    @retry(retry_on_exception=retry_if_access_token_needs_refreshing, stop_max_attempt_number=2)
    def get_items(self, search_term, endpoint, parser):
        try:
            sanitised_search_term = self.sanitise_search_term(search_term)

            result = self.session.get(BASE_API + endpoint + sanitised_search_term,
                                      params={'access_token': self.access_token},
                                      timeout=int(self.timeout))

            if result.status_code == 401:
                raise AccessTokenExpiredException
            elif result.status_code != 200:
                raise ResponseException

            json_results = result.json()

            try:
                if 'No Results.' in json_results["error"]["messages"]:
                    raise ResponseException('Failed to find results for: ' + search_term)
            except TypeError:
                pass

            parsed_results = parser(json_results)

            return parsed_results
        except AccessTokenExpiredException:
            self.refresh_access_token()
            raise
        except Exception as e:
            self.logger.error('ANI error: ' + str(e))
            return []
        finally:
            self.session.close()

    def get_anime(self, search_term):
        return self.get_items(search_term, ANIME_ENDPOINT, self.parse_anime)

    def get_manga(self, search_term):
        return self.get_items(search_term, MANGA_ENDPOINT, self.parse_manga)

    def get_light_novel(self, search_term):
        return self.get_items(search_term, MANGA_ENDPOINT, self.parse_light_novel)

    @staticmethod
    def parse_anime(results):
        anime_list = []

        for entry in results:
            try:
                anime_list.append(Anime(id=entry['id'],
                                        urls={DataSource.ANILIST: 'https://anilist.co/anime/' + str(entry['id'])},
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
                              urls={DataSource.ANILIST: 'https://anilist.co/anime/' + str(entry['id'])},
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
                                urls={DataSource.ANILIST: 'https://anilist.co/anime/' + str(entry['id'])},
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
        '''replacements = (["/", " "],
                        ["&", " "])

        for character, replacement in replacements:
            text = text.replace(character, replacement)

        return text'''
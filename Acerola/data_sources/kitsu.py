from ..errors import ResponseException
from ..enums import Type, DataSource
from ..util import get_type

from ..response_types import Anime, Manga, LightNovel

import requests
import logging

AUTH_URL = 'https://kitsu.io/api/oauth/'
BASE_API = 'https://kitsu.io/api/edge/'
ANIME_FILTER = 'anime?filter[text]='
MANGA_FILTER = 'manga?filter[text]='

TYPE_MAPPING = (['TV', Type.TV],
                ['movie', Type.MOVIE],
                ['OVA', Type.OVA],
                ['ONA', Type.ONA],
                ['special', Type.SPECIAL],
                ['music', Type.OTHER],
                ['manga', Type.MANGA],
                ['novel', Type.LIGHT_NOVEL],
                ['oneshot', Type.ONE_SHOT],
                ['doujin', Type.DOUJINSHI],
                ['manhwa', Type.MANHWA],
                ['manhua', Type.MANHUA])


class Kitsu:
    def __init__(self, config):
        self.session = requests.Session()
        self.session.headers = {'Accept': 'application/vnd.api+json', 'Content-Type': 'application/vnd.api+json'}

        self.logger = logging.getLogger('AcerolaLogger')

        self.config = config

    def get_items(self, search_term, endpoint, parser):
        try:
            result = self.session.get(BASE_API + endpoint + search_term, timeout=int(self.config['Timeout']))

            # todo - better message, give status code in exception
            if result.status_code != 200:
                raise ResponseException('Failed to find results for: ' + search_term)

            # todo - check if there are no results? just raise an exception?

            parsed_results = parser(result.json()['data'])

            return parsed_results
        except Exception as e:
            self.logger.error('KIT Exception: ' + str(e))
            return []
        finally:
            self.session.close()

    def get_anime(self, search_term):
        return self.get_items(search_term, ANIME_FILTER, self.parse_anime)

    def get_manga(self, search_term):
        return self.get_items(search_term, MANGA_FILTER, self.parse_manga)

    def get_light_novel(self, search_term):
        return self.get_items(search_term, MANGA_FILTER, self.parse_light_novel)

    @staticmethod
    def parse_anime(results):
        anime_list = []

        for entry in results:
            try:
                anime_list.append(Anime(id=entry['id'],
                                        urls={DataSource.KITSU: 'https://kitsu.io/anime/' + entry['id']},
                                        title_romaji=entry['attributes']['titles']['en_jp'] if 'en_jp' in entry['attributes']['titles'] else None,
                                        title_english=entry['attributes']['titles']['en'] if 'en' in entry['attributes']['titles'] else None,
                                        title_japanese=entry['attributes']['titles']['ja_jp'] if 'ja_jp' in entry['attributes']['titles'] else None,
                                        synonyms=set(entry['attributes']['abbreviatedTitles']) if entry['attributes']['abbreviatedTitles'] else set(),
                                        episode_count=(int(entry['attributes']['episodeCount']) if int(entry['attributes']['episodeCount']) > 0 else None),
                                        type=get_type(TYPE_MAPPING, entry['attributes']['showType']),
                                        description=entry['attributes']['synopsis'],
                                        nsfw=entry['attributes']['nsfw']))
            except AttributeError:
                pass

        return anime_list

    @staticmethod
    def parse_manga(results):
        manga_list = []

        for entry in results:
            try:

                manga = Manga(id=entry['id'],
                              urls={DataSource.KITSU: 'https://kitsu.io/manga/' + entry['id']},
                              title_romaji=entry['attributes']['titles']['en_jp'] if 'en_jp' in entry['attributes']['titles'] else None,
                              title_english=entry['attributes']['titles']['en'] if 'en' in entry['attributes']['titles'] else None,
                              synonyms=set(entry['attributes']['abbreviatedTitles']) if entry['attributes']['abbreviatedTitles'] else set(),
                              type=get_type(TYPE_MAPPING, entry['attributes']['mangaType']),
                              description=entry['attributes']['synopsis'])

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
                                urls={DataSource.KITSU: 'https://kitsu.io/manga/' + entry['id']},
                                title_romaji=entry['attributes']['titles']['en_jp'] if 'en_jp' in entry['attributes']['titles'] else None,
                                title_english=entry['attributes']['titles']['en'] if 'en' in entry['attributes']['titles'] else None,
                                synonyms=set(entry['attributes']['abbreviatedTitles']) if entry['attributes']['abbreviatedTitles'] else set(),
                                type=get_type(TYPE_MAPPING, entry['attributes']['mangaType']),
                                description=entry['attributes']['synopsis'])

                if ln.type == Type.LIGHT_NOVEL:
                    ln_list.append(ln)
            except AttributeError:
                pass

        return ln_list

from ..enums import Type, DataSource
from ..util import get_type
from ..response_types import Anime, Manga, LightNovel
from ..errors import NoResultsFound, DataSourceTimeoutError, DataSourceUnavailableError, AcerolaError

import requests
import logging

AUTH_URL = 'https://kitsu.io/api/oauth/'
BASE_URL = 'https://kitsu.io/api/edge/'
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


# todo add status, genres, etc
class Kitsu:
    source_type = DataSource.KITSU

    def __init__(self, config):
        self.session = requests.Session()
        self.session.headers = {'Accept': 'application/vnd.api+json', 'Content-Type': 'application/vnd.api+json'}

        self.logger = logging.getLogger('AcerolaLogger')

        self.config = config

    # todo logging decorator?
    def kitsu_search(self, endpoint, search_term, parser):
        try:
            response = self.session.get(BASE_URL + endpoint + search_term, timeout=int(self.config['Timeout']))
            response.raise_for_status()

            results = parser(response.json()['data'])

            if not results:
                raise NoResultsFound(Kitsu.source_type, search_term)

            return results
        except NoResultsFound:
            raise
        except requests.exceptions.Timeout:
            raise DataSourceTimeoutError(Kitsu.source_type)
        except requests.exceptions.RequestException:
            raise DataSourceUnavailableError(Kitsu.source_type)
        except Exception as e:
            raise AcerolaError(e)
        finally:
            self.session.close()

    def search_anime(self, search_term):
        return self.kitsu_search(ANIME_FILTER, search_term, self.parse_anime)

    def search_manga(self, search_term):
        return self.kitsu_search(MANGA_FILTER, search_term, self.parse_manga)

    def search_light_novel(self, search_term):
        return self.kitsu_search(MANGA_FILTER, search_term, self.parse_light_novel)

    @staticmethod
    def parse_anime(results):
        anime_list = []

        for entry in results:
            try:
                anime_list.append(Anime(id=entry['id'],
                                        url='https://kitsu.io/anime/' + entry['id'],
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
                              url='https://kitsu.io/manga/' + entry['id'],
                              title_romaji=entry['attributes']['titles']['en_jp'] if 'en_jp' in entry['attributes']['titles'] else None,
                              title_english=entry['attributes']['titles']['en'] if 'en' in entry['attributes']['titles'] else None,
                              synonyms=set(entry['attributes']['abbreviatedTitles']) if entry['attributes']['abbreviatedTitles'] else set(),
                              volume_count=(int(entry['attributes']['volumeCount']) if entry['attributes']['volumeCount'] else None),
                              chapter_count=(int(entry['attributes']['chapterCount']) if entry['attributes']['chapterCount'] else None),
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
                                url='https://kitsu.io/manga/' + entry['id'],
                                title_romaji=entry['attributes']['titles']['en_jp'] if 'en_jp' in entry['attributes']['titles'] else None,
                                title_english=entry['attributes']['titles']['en'] if 'en' in entry['attributes']['titles'] else None,
                                synonyms=set(entry['attributes']['abbreviatedTitles']) if entry['attributes']['abbreviatedTitles'] else set(),
                                volume_count=(int(entry['attributes']['volumeCount']) if entry['attributes']['volumeCount'] else None),
                                chapter_count=(int(entry['attributes']['chapterCount']) if entry['attributes']['chapterCount'] else None),
                                type=get_type(TYPE_MAPPING, entry['attributes']['mangaType']),
                                description=entry['attributes']['synopsis'])

                if ln.type == Type.LIGHT_NOVEL:
                    ln_list.append(ln)
            except AttributeError:
                pass

        return ln_list

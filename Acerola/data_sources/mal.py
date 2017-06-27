import xml.etree.cElementTree as et
import logging

from ..errors import XmlParseError, ResponseException
from ..enums import Type, DataSource, Status
from ..util import get_status, get_type

from ..response_types import Anime, Manga, LightNovel

import requests
from traceback import print_exc

BASE_API = 'https://myanimelist.net/api/'
ANIME_ENDPOINT = 'anime/search.xml?q='
MANGA_ENDPOINT = 'manga/search.xml?q='

TYPE_MAPPING = (['TV', Type.TV],
                ['Movie', Type.MOVIE],
                ['OVA', Type.OVA],
                ['ONA', Type.ONA],
                ['Special', Type.SPECIAL],
                ['Manga', Type.MANGA],
                ['Novel', Type.LIGHT_NOVEL],
                ['One-shot', Type.ONE_SHOT],
                ['Doujinshi', Type.DOUJINSHI],
                ['Manhwa', Type.MANHWA],
                ['Manhua', Type.MANHUA])

STATUS_MAPPING = (['Not yet aired', Status.UPCOMING],
                  ['Finished Airing', Status.FINISHED],
                  ['Currently Airing', Status.ONGOING],
                  ['Publishing', Status.ONGOING],
                  ['Finished', Status.FINISHED])

# todo - get by id


class Mal:
    # todo better handling of errors inside "get items" call (include requests.timeout)
    def __init__(self, config):
        self.config = config

        self.logger = logging.getLogger('AcerolaLogger')

        self.session = requests.session()
        self.session.headers.update({'Authorization': self.config['Auth'], 'User-Agent': self.config['UserAgent']})

    def get_items(self, search_term, endpoint, parser):
        try:
            result = self.session.get(BASE_API + endpoint + search_term, timeout=int(self.config['Timeout']))

            if result.status_code == 204:
                return []
            elif result.status_code != 200:
                raise ResponseException('Failed to find results for: ' + search_term)

            sanitised_result = self.sanitise_shitty_xml(result.text)
            parsed_results = parser(sanitised_result)

            return parsed_results
        except Exception as e:
            print(search_term)
            print_exc()
            return []
        finally:
            self.session.close()

    # Get normally
    def get_anime(self, search_term):
        return self.get_items(search_term, ANIME_ENDPOINT, self.parse_anime)

    def get_manga(self, search_term):
        return self.get_items(search_term, MANGA_ENDPOINT, self.parse_manga)

    def get_light_novel(self, search_term):
        return self.get_items(search_term, MANGA_ENDPOINT, self.parse_light_novel)

    @staticmethod
    def parse_anime(xml):
        try:
            entries = et.fromstring(xml)
        except et.ParseError:
            raise XmlParseError('The XML is busted.')

        anime_list = []

        for entry in entries:
            try:
                anime_list.append(Anime(id=int(entry.find('id').text),
                                        urls={DataSource.MAL: 'http://myanimelist.net/anime/' + str(entry.find('id').text)},
                                        title_english=entry.find('english').text,
                                        title_romaji=entry.find('title').text,
                                        synonyms=set(entry.find('synonyms').text.split(";"))
                                            if entry.find('synonyms').text else set(),
                                        episode_count=(int(entry.find('episodes').text)
                                                       if int(entry.find('episodes').text) > 0 else None)
                                                       if isinstance(entry.find('episodes').text, int) else None,
                                        type=get_type(TYPE_MAPPING, entry.find('type').text),
                                        status=get_status(STATUS_MAPPING, entry.find('status').text),
                                        description=entry.find('synopsis').text,
                                        score=float(entry.find('score').text)))
            except AttributeError as e:
                print(e)
                # todo - better logging
                continue

        return anime_list

    @staticmethod
    def parse_manga(xml):
        try:
            entries = et.fromstring(xml)
        except et.ParseError:
            raise XmlParseError('The XML is busted.')

        manga_list = []

        for entry in entries:
            try:
                manga = Manga(id=entry.find('id').text,
                              urls={DataSource.MAL: 'http://myanimelist.net/manga/' + str(entry.find('id').text)},
                              title_english=entry.find('english').text,
                              title_romaji=entry.find('title').text,
                              synonyms=set(entry.find('synonyms').text.split(";"))
                                if entry.find('synonyms').text else set(),
                              chapter_count=entry.find('chapters').text,
                              volume_count=entry.find('volumes').text,
                              type=get_type(TYPE_MAPPING, entry.find('type').text),
                              status=get_status(STATUS_MAPPING, entry.find('status').text),
                              description=entry.find('synopsis').text,
                              score=float(entry.find('score').text))

                if manga.type != Type.LIGHT_NOVEL:
                    manga_list.append(manga)

            except AttributeError as e:
                print(e)
                # todo - better logging
                continue

        return manga_list

    @staticmethod
    def parse_light_novel(xml):
        try:
            entries = et.fromstring(xml)
        except et.ParseError:
            raise XmlParseError('The XML is busted.')

        ln_list = []

        for entry in entries:
            try:
                ln = LightNovel(id=entry.find('id').text,
                                urls={DataSource.MAL: 'http://myanimelist.net/manga/' + str(entry.find('id').text)},
                                title_english=entry.find('english').text,
                                title_romaji=entry.find('title').text,
                                synonyms=set(entry.find('synonyms').text.split(";"))
                                    if entry.find('synonyms').text else set(),
                                chapter_count=entry.find('chapters').text,
                                volume_count=entry.find('volumes').text,
                                status=get_status(STATUS_MAPPING, entry.find('status').text),
                                description=entry.find('synopsis').text,
                                score=float(entry.find('score').text))

                if ln.type == Type.LIGHT_NOVEL:
                    ln_list.append(ln)

            except AttributeError as e:
                # todo - better logging
                print(e)
                continue

        return ln_list

    @staticmethod
    def sanitise_shitty_xml(text):
        replacements = (['&amp;', '&'],
                        ['&Eacute;', 'É'],
                        ['&times;', 'x'],
                        ['&rsquo;', "'"],
                        ['&lsquo;', "'"],
                        ['&hellip;', '...'],
                        ['&le;', '<'],
                        ['<;', '; '],
                        ['&hearts;', '♥'],
                        ['&mdash;', '-'],
                        ['&eacute;', 'é'],
                        ['&ndash;', '-'],
                        ['&Aacute;', 'Á'],
                        ['&acute;', 'à'],
                        ['&ldquo;', '"'],
                        ['&rdquo;', '"'],
                        ['&Oslash;', 'Ø'],
                        ['&frac12;', '½'],
                        ['&infin;', '∞'],
                        ['&agrave;', 'à'],
                        ['&egrave;', 'è'],
                        ['&dagger;', '†'],
                        ['&sup2;', '²'],
                        ['&#039;', "'"],
                        ['&', '&amp;'])

        for character, replacement in replacements:
            text = text.replace(character, replacement)

        return text

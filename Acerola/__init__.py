from .data_sources import Mal, Anilist, Kitsu, AnimePlanet, AniDB, MangaUpdates
from .response_types import Anime, Manga, LightNovel

from .enums import DataSource
from .searcher import Searcher

import logging


class Acerola:
    def __init__(self, config, log_level=logging.INFO):
        self._config = config

        self._mal = Mal(self._config['MyAnimeList'])
        self._anilist = Anilist(self._config['Anilist'])
        self._kitsu = Kitsu(self._config['Kitsu'])
        self._animeplanet = AnimePlanet(self._config['AnimePlanet'])
        self._anidb = AniDB(self._config['AniDB'])
        self._mu = MangaUpdates(self._config['MangaUpdates'])

        # todo get a better name
        self.logger = logging.getLogger('AcerolaLogger')
        self.logger.setLevel(log_level)

        self.anime = Searcher({DataSource.MAL: self._mal.get_anime,
                               DataSource.ANILIST: self._anilist.get_anime,
                               DataSource.KITSU: self._kitsu.get_anime,
                               DataSource.ANIMEPLANET: self._animeplanet.get_anime,
                               DataSource.ANIDB: self._anidb.get_anime},
                              Anime.consolidate)

        self.manga = Searcher({DataSource.MAL: self._mal.get_manga,
                               DataSource.ANILIST: self._anilist.get_manga,
                               DataSource.KITSU: self._kitsu.get_manga,
                               DataSource.ANIMEPLANET: self._animeplanet.get_manga,
                               DataSource.MANGAUPDATES: self._mu.get_manga},
                              Manga.consolidate)

        self.light_novel = Searcher({DataSource.MAL: self._mal.get_light_novel,
                                     DataSource.ANILIST: self._anilist.get_light_novel,
                                     DataSource.KITSU: self._kitsu.get_light_novel,
                                     DataSource.ANIMEPLANET: self._animeplanet.get_light_novel,
                                     DataSource.MANGAUPDATES: self._mu.get_light_novel},
                                    LightNovel.consolidate)

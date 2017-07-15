from .data_sources import Mal, Anilist, Kitsu, AnimePlanet, AniDB, MangaUpdates
from .searcher import Searcher, AnimeSearcher, MangaSearcher, LightNovelSearcher
from .enums import DataSource

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

        self.anime = Searcher(AnimeSearcher(self._mal, self._anilist, self._kitsu, self._animeplanet, self._anidb))
        self.manga = Searcher(MangaSearcher(self._mal, self._anilist, self._kitsu, self._animeplanet, self._mu))
        self.light_novel = Searcher(LightNovelSearcher(self._mal, self._anilist, self._kitsu, self._animeplanet, self._mu))

    def refresh_anidb_database(self):
        self._anidb.refresh_database()

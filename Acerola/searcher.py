class Searcher:
    def __init__(self, type_searcher):
        self._type_searcher = type_searcher

    def search(self, source_type, term):
        return self._type_searcher.search(source_type, term)

    def get(self, source_type, id):
        return self._type_searcher.get(source_type, id)


class AnimeSearcher:
    def __init__(self, *sources):
        self._sources = {source.source_type: source for source in sources}

    def search(self, source_type, term):
        try:
            return self._sources[source_type].search_anime(term)
        except KeyError:
            raise ValueError(str(source_type) + ' is not a valid anime source.')
        except AttributeError:
            raise NotImplementedError('anime.search() is not implemented for ' + str(source_type))

    def get(self, source_type, term):
        try:
            return self._sources[source_type].get_anime(term)
        except KeyError:
            raise ValueError(str(source_type) + ' is not a valid anime source.')
        except AttributeError:
            raise NotImplementedError('anime.get() is not implemented for ' + str(source_type))


class MangaSearcher:
    def __init__(self, *sources):
        self._sources = {source.source_type: source for source in sources}

    def search(self, source_type, term):
        try:
            return self._sources[source_type].search_manga(term)
        except KeyError:
            raise ValueError(str(source_type) + ' is not a valid manga source.')
        except AttributeError:
            raise NotImplementedError('manga.search() is not implemented for ' + str(source_type))

    def get(self, source_type, id):
        try:
            return self._sources[source_type].get_manga(id)
        except KeyError:
            raise ValueError(str(source_type) + ' is not a valid manga source.')
        except AttributeError:
            raise NotImplementedError('manga.get() is not implemented for ' + str(source_type))


class LightNovelSearcher:
    def __init__(self, *sources):
        self._sources = {source.source_type: source for source in sources}

    def search(self, source_type, term):
        try:
            return self._sources[source_type].search_light_novel(term)
        except KeyError:
            raise ValueError(str(source_type) + ' is not a valid light novel source.')
        except AttributeError:
            raise NotImplementedError('light_novel.search() is not implemented for ' + str(source_type))

    def get(self, source_type, id):
        try:
            return self._sources[source_type].get_light_novel(id)
        except KeyError:
            raise ValueError(str(source_type) + ' is not a valid light novel source.')
        except AttributeError:
            raise NotImplementedError('light_novel.get() is not implemented for ' + str(source_type))

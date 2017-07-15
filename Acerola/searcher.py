from.errors import InvalidDataSourceForSeriesTypeError, FeatureNotImplementedError


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

    # todo - the exception handling for these classes is too general
    def search(self, source_type, term):
        if source_type not in self._sources:
            raise InvalidDataSourceForSeriesTypeError(source_type)

        if 'search_anime' not in dir(self._sources[source_type]):
            raise FeatureNotImplementedError(source_type, 'search_anime')

        return self._sources[source_type].search_anime(term)

    def get(self, source_type, id):
        if source_type not in self._sources:
            raise InvalidDataSourceForSeriesTypeError(source_type)

        if 'get_anime' not in dir(self._sources[source_type]):
            raise FeatureNotImplementedError(source_type, 'get_anime')

        return self._sources[source_type].get_anime(id)


class MangaSearcher:
    def __init__(self, *sources):
        self._sources = {source.source_type: source for source in sources}

    def search(self, source_type, term):
        if source_type not in self._sources:
            raise InvalidDataSourceForSeriesTypeError(source_type)

        if 'search_manga' not in dir(self._sources[source_type]):
            raise FeatureNotImplementedError(source_type, 'search_manga')

        return self._sources[source_type].search_manga(term)

    def get(self, source_type, id):
        if source_type not in self._sources:
            raise InvalidDataSourceForSeriesTypeError(source_type)

        if 'get_manga' not in dir(self._sources[source_type]):
            raise FeatureNotImplementedError(source_type, 'get_manga')

        return self._sources[source_type].get_manga(id)


class LightNovelSearcher:
    def __init__(self, *sources):
        self._sources = {source.source_type: source for source in sources}

    def search(self, source_type, term):
        if source_type not in self._sources:
            raise InvalidDataSourceForSeriesTypeError(source_type)

        if 'search_light_novel' not in dir(self._sources[source_type]):
            raise FeatureNotImplementedError(source_type, 'search_light_novel')

        return self._sources[source_type].search_light_novel(term)

    def get(self, source_type, id):
        if source_type not in self._sources:
            raise InvalidDataSourceForSeriesTypeError(source_type)

        if 'get_light_novel' not in dir(self._sources[source_type]):
            raise FeatureNotImplementedError(source_type, 'get_light_novel')

        return self._sources[source_type].get_light_novel(id)

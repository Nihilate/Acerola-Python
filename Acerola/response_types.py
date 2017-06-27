class Anime:
    # todo abstract out titles?
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.urls = kwargs.get('urls')

        self.title_romaji = kwargs.get('title_romaji')
        self.title_english = kwargs.get('title_english')
        self.title_japanese = kwargs.get('title_japanese')

        self.synonyms = kwargs.get('synonyms') or set()
        self.genres = kwargs.get('genres') or set()

        self.episode_count = kwargs.get('episode_count')

        self.status = kwargs.get('status')
        self.type = kwargs.get('type')
        self.description = kwargs.get('description')
        self.source = kwargs.get('source')
        self.nsfw = kwargs.get('nsfw')
        self.score = kwargs.get('score')

    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def consolidate(dict_of_anime):
        just_the_results = [result for source_type, result in dict_of_anime.items() if result]

        if any(not isinstance(result, Anime) for result in just_the_results):
            raise TypeError('The dictionary contains objects other than Anime')

        # TODO - Handle the URLs/synonyms better
        flattened_urls = {}
        [flattened_urls.update(url_dict) for url_dict in reversed([result.urls for result in just_the_results])]

        synonyms_list = [synonyms for synonyms in
                         [result.synonyms for result in just_the_results if result.synonyms]]
        return Anime(id=None,
                     urls=flattened_urls,
                     title_romaji=next((result.title_romaji for result in just_the_results if result.title_romaji), None),
                     title_english=next((result.title_english for result in just_the_results if result.title_english), None),
                     title_japanese=next((result.title_japanese for result in just_the_results if result.title_japanese), None),
                     synonyms=set.union(*synonyms_list) if synonyms_list else set(),
                     genres=next((result.genres for result in just_the_results if result.genres), set()),
                     episode_count=next((result.episode_count for result in just_the_results if result.episode_count), None),
                     status=next((result.status for result in just_the_results if result.status), None),
                     type=next((result.type for result in just_the_results if result.type), None),
                     description=next((result.description for result in just_the_results if result.description), None),
                     source=next((result.source for result in just_the_results if result.source), None),
                     nsfw=next((result.nsfw for result in just_the_results if result.nsfw is not None), None),
                     score=next((result.score for result in just_the_results if result.score is not None), None))


class Manga:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.urls = kwargs.get('urls')

        self.title_romaji = kwargs.get('title_romaji')
        self.title_english = kwargs.get('title_english')
        self.title_japanese = kwargs.get('title_japanese')

        self.synonyms = kwargs.get('synonyms') or set()
        self.genres = kwargs.get('genres') or set()

        self.chapter_count = kwargs.get('chapter_count')
        self.volume_count = kwargs.get('volume_count')

        self.status = kwargs.get('status')
        self.type = kwargs.get('type')
        self.description = kwargs.get('description')
        self.nsfw = kwargs.get('nsfw')
        self.score = kwargs.get('score')

    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def consolidate(dict_of_manga):
        just_the_results = [result for source_type, result in dict_of_manga.items() if result]

        if any(not isinstance(result, Manga) for result in just_the_results):
            raise TypeError('The dictionary contains objects other than Manga')

        # TODO - Handle the URLs/synonyms better
        flattened_urls = {}
        [flattened_urls.update(url_dict) for url_dict in reversed([result.urls for result in just_the_results])]

        synonyms_list = [synonyms for synonyms in
                         [result.synonyms for result in just_the_results if result.synonyms]]
        return Manga(id=None,
                     urls=flattened_urls,
                     title_romaji=next((result.title_romaji for result in just_the_results if result.title_romaji), None),
                     title_english=next((result.title_english for result in just_the_results if result.title_english), None),
                     title_japanese=next((result.title_japanese for result in just_the_results if result.title_japanese), None),
                     synonyms=set.union(*synonyms_list) if synonyms_list else set(),
                     genres=next((result.genres for result in just_the_results if result.genres is not None), set()),
                     chapter_count=next((result.chapter_count for result in just_the_results if result.chapter_count), None),
                     volume_count=next((result.volume_count for result in just_the_results if result.volume_count), None),
                     status=next((result.status for result in just_the_results if result.status), None),
                     type=next((result.type for result in just_the_results if result.type), None),
                     description=next((result.description for result in just_the_results if result.description), None),
                     nsfw=next((result.nsfw for result in just_the_results if result.nsfw is not None), None),
                     score=next((result.score for result in just_the_results if result.score is not None), None))


class LightNovel:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.urls = kwargs.get('urls')

        self.title_romaji = kwargs.get('title_romaji')
        self.title_english = kwargs.get('title_english')
        self.title_japanese = kwargs.get('title_japanese')

        self.synonyms = kwargs.get('synonyms') or set()
        self.genres = kwargs.get('genres') or set()

        self.chapter_count = kwargs.get('chapter_count')
        self.volume_count = kwargs.get('volume_count')

        self.status = kwargs.get('status')
        self.type = kwargs.get('type')
        self.description = kwargs.get('description')
        self.nsfw = kwargs.get('nsfw')
        self.score = kwargs.get('score')

    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def consolidate(dict_of_light_novel):
        just_the_results = [result for source_type, result in dict_of_light_novel.items() if result]

        if any(not isinstance(result, LightNovel) for result in just_the_results):
            raise TypeError('The dictionary contains objects other than LightNovel')

        # TODO - Handle the URLs/synonyms better
        flattened_urls = {}
        [flattened_urls.update(url_dict) for url_dict in reversed([result.urls for result in just_the_results])]

        synonyms_list = [synonyms for synonyms in
                         [result.synonyms for result in just_the_results if result.synonyms]]
        return LightNovel(id=None,
                          urls=flattened_urls,
                          title_romaji=next((result.title_romaji for result in just_the_results if result.title_romaji), None),
                          title_english=next((result.title_english for result in just_the_results if result.title_english), None),
                          title_japanese=next((result.title_japanese for result in just_the_results if result.title_japanese), None),
                          synonyms=set.union(*synonyms_list) if synonyms_list else set(),
                          genres=next((result.genres for result in just_the_results if result.genres is not None), set()),
                          chapter_count=next((result.chapter_count for result in just_the_results if result.chapter_count), None),
                          volume_count=next((result.volume_count for result in just_the_results if result.volume_count), None),
                          status=next((result.status for result in just_the_results if result.status), None),
                          type=next((result.type for result in just_the_results if result.type), None),
                          description=next((result.description for result in just_the_results if result.description), None),
                          nsfw=next((result.nsfw for result in just_the_results if result.nsfw is not None), None),
                          score=next((result.score for result in just_the_results if result.score is not None), None))

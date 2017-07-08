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

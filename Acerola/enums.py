from enum import Enum


class Status(Enum):
    UNKNOWN = 0,
    FINISHED = 1,
    ONGOING = 2,
    UPCOMING = 3,
    CANCELLED = 4


class DataSource(Enum):
    MAL = 1,
    ANILIST = 2,
    KITSU = 3,
    ANIMEPLANET = 4,
    ANIDB = 5,
    MANGAUPDATES = 6,
    LNDB = 7
    NOVELUPDATES = 8


class SeriesSource(Enum):
    UNKNOWN = 0,
    ORIGINAL = 1,
    MANGA = 2,
    LIGHT_NOVEL = 3,
    VISUAL_NOVEL = 4,
    VIDEO_GAME = 5,
    OTHER = 6


class Type(Enum):
    UNKNOWN = 0,
    TV = 1,
    MOVIE = 2,
    OVA = 3,
    ONA = 4,
    SPECIAL = 5,
    MANGA = 6,
    ONE_SHOT = 7,
    LIGHT_NOVEL = 8,
    DOUJINSHI = 9
    MANHWA = 10,
    MANHUA = 11,
    OTHER = 12

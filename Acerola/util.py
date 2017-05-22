from Acerola.enums import Type, Status, SeriesSource
from difflib import get_close_matches

def get_type(mapping, series_type):
    for mapped_type, enum_type in mapping:
        if series_type == mapped_type:
            return enum_type

    return Type.UNKNOWN


def get_status(mapping, series_status):
    for status, enum_status in mapping:
        if series_status == status:
            return enum_status

    return Status.UNKNOWN


def get_series_source(mapping, series_source):
    for source, enum_source in mapping:
        if series_source == source:
            return enum_source

    return SeriesSource.UNKNOWN


# needs a better name, too close to the searcher function
def find_closest(term, list_to_search):
    title_list = set()
    all_list = set()

    for entry in list_to_search:
        if entry.title_english:
            title_list.add(entry.title_english.lower())
            all_list.add(entry.title_english.lower())

        if entry.title_romaji:
            title_list.add(entry.title_romaji.lower())
            all_list.add(entry.title_romaji.lower())

        if entry.synonyms:
            for synonym in entry.synonyms:
                all_list.add(synonym.lower())

    list_of_closest = get_close_matches(term.lower(), all_list, 1, 0.90)

    if not list_of_closest:
        return None

    closest = list_of_closest[0]

    for entry in list_to_search:
        if entry.title_romaji:
            if entry.title_romaji.lower() == closest:
                return entry

    for entry in list_to_search:
        if entry.title_english:
            if entry.title_english.lower() == closest:
                return entry

    for entry in list_to_search:
        for synonym in entry.synonyms:
            if synonym.lower() == closest and synonym.lower() not in title_list:
                return entry

    return None
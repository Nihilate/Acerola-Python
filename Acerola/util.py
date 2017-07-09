from Acerola.enums import Type, Status, SeriesSource


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


def clean_description(description):
    # todo - this should remove branding from descriptions
    return description

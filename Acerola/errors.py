# todo - make this class actually useful
# todo - add error for data sources not being configured correctly
# todo - add error for a data source being unavailable (down or timing out)


class AcerolaError(Exception):
    pass


class DataSourceTimeoutError(AcerolaError):
    def __init__(self, data_source):
        self.error_message = '{data_source} timed out.'.format(data_source=data_source)
        super(AcerolaError, self).__init__(self.error_message)


class DataSourceUnavailableError(AcerolaError):
    def __init__(self, data_source):
        self.error_message = '{data_source} is unavailable.'.format(data_source=data_source)
        super(AcerolaError, self).__init__(self.error_message)


class InvalidDataSourceForSeriesTypeError(AcerolaError):
    def __init__(self, data_source):
        self.error_message = '{data_source} is an invalid data source for this series type.'.format(data_source=data_source)
        super(AcerolaError, self).__init__(self.error_message)


class FeatureNotImplementedError(AcerolaError):
    def __init__(self, data_source, function):
        self.error_message = '{function} is not implemented for {data_source}.'.format(data_source=data_source, function=function)
        super(AcerolaError, self).__init__(self.error_message)

class NoResultsFound(AcerolaError):
    def __init__(self, data_source, search_term):
        self.error_message = '{data_source} found no results for \'{search_term}\'.'.format(data_source=data_source, search_term=search_term)
        super(AcerolaError, self).__init__(self.error_message)


class ParserError(AcerolaError):
    def __init__(self, data_source, search_term):
        self.error_message = '{data_source} failed to parse results for \'{search_term}\'.'.format(data_source=data_source, search_term=search_term)
        super(AcerolaError, self).__init__(self.error_message)
    pass


class AccessTokenExpiredError(AcerolaError):
    def __init__(self, data_source):
        self.error_message = 'The access token for {data_source} has expired.'.format(data_source=data_source)
        super(AcerolaError, self).__init__(self.error_message)
    pass

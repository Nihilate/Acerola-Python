# todo - make this class actually useful
# todo - add error for data sources not being configured correctly
# todo - add error for a data source being unavailable (down or timing out)


class AcerolaException(Exception):
    pass


class AttributeParseException(AcerolaException):
    pass


class XmlParseError(AcerolaException):
    pass


class AccessTokenExpiredException(AcerolaException):
    pass


class ResponseException(AcerolaException):
    pass

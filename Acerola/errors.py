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

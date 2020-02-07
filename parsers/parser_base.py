import re
from abc import ABCMeta, abstractmethod
from urllib.parse import urlparse, urlencode, urlunparse, parse_qs


class ParserBase:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def parse(self):
        raise NotImplementedError

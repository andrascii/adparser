import re
from abc import ABCMeta, abstractmethod
from urllib.parse import urlparse, urlencode, urlunparse, parse_qs


class ParserBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def start(self):
        raise NotImplementedError

    @staticmethod
    def _remove_duplicated_hosts(lst: list):
        dictionary = {}
        for item in lst:
            dictionary[item['url']] = item

        return list(dictionary.values())

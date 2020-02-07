from abc import ABCMeta, abstractmethod


class ILoader:
    __metaclass__ = ABCMeta

    @abstractmethod
    def load_page(self, url: str):
        raise NotImplementedError

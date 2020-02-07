from chrome_based_loader import ChromeBasedLoader


class LoaderFactory:
    def __init__(self, requires_js: bool):
        self.__requires_js = requires_js

    def create(self):
        if self.__requires_js:
            return ChromeBasedLoader()

        raise Exception("There is no more loaders")

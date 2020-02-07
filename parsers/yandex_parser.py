from selenium.webdriver import Chrome
from parsers.parser_base import ParserBase


class YandexParser(ParserBase):
    def __init__(self, driver: Chrome, config):
        ParserBase.__init__(self)
        self.__driver: Chrome = driver

    def parse(self):
        try:
            ad_elements = self.__driver.find_elements_by_class_name('serp-item')

            result = {}

            for ad_element in ad_elements:
                organic_path = ad_element.find_element_by_class_name('organic__path')
                url = organic_path.find_element_by_tag_name('b').text.strip()
                text = ad_element.find_element_by_class_name('text-container').text.strip()
                result[url] = text

            return result

        except:
            return None

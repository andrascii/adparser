import json
import psutil
import helpers
from urllib.parse import urlparse
from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException, WebDriverException, InvalidArgumentException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from json import loads
from iloader import ILoader
from parsers.yandex_parser import YandexParser
import codecs


class ChromeBasedLoader(ILoader):
    def __init__(self):
        cap = DesiredCapabilities.CHROME
        cap['loggingPrefs'] = {'performance': 'ALL'}

        self.__driver = None
        self.__parsers = {}
        self.__try_launch_browser()
        self.__init_parsers()

    def load_page(self, url: str):
        max_attempt_number = 3

        while max_attempt_number > 0:
            try:
                return self.__load_page_helper(url)

            except WebDriverException as error:
                if not self.__is_browser_running():
                    self.__try_launch_browser()
                    max_attempt_number -= 1
                    continue

                print(error)
                return None

    def __load_page_helper(self, url: str):
        print('Loading {0}'.format(url))

        self.__driver.execute_script('console.clear()')
        self.__driver.get(url)

        url_data = urlparse(url)

        parser = None

        for parser_id in self.__parsers:
            if parser_id in url_data.hostname:
                parser = self.__parsers[parser_id]

        result = {
            'url': url,
            'ads': None if parser is None else parser.parse()
        }

        return result

    def __try_launch_browser(self):
        print('Starting Google Chrome browser...')

        cap = DesiredCapabilities.CHROME
        cap['loggingPrefs'] = {'performance': 'ALL'}
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless')

        self.__driver = webdriver.Chrome(desired_capabilities=cap, chrome_options=options)

        print('Browser started', end='\n\n')

    @staticmethod
    def __unnecessary_link_scheme(scheme: str):
        return scheme == 'mailto' or scheme == 'tel' or scheme == 'javascript' or not scheme

    def __init_parsers(self):
        path = 'parsers/parse_configurations/'
        parse_configs = helpers.all_files_in_folder(path)

        for parse_config in parse_configs:
            data = json.load(codecs.open(path + parse_config, 'r', 'utf-8-sig'))
            assert 'name' in data
            self.__parsers[data['name']] = YandexParser(self.__driver, data)

    def __is_browser_running(self):
        browser_process = psutil.Process(self.__driver.service.process.pid)

        if browser_process.is_running():
            children = browser_process.children()
            return children and children[0]

        return False

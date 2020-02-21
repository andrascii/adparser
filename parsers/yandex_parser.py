import psutil
import urllib.parse
import logging
import time
import threading
from data_collector import DataCollector
from parsers.parser_base import ParserBase
from selenium.common.exceptions import WebDriverException, NoSuchElementException, NoSuchWindowException
from web_driver_factory import WebDriverFactory


class YandexParser(ParserBase):
    BASE_URL = 'https://yandex.ru/search/ads'
    TEXT_VARIABLE_NAME = 'text'
    CITY_CODE_VARIABLE_NAME = 'lr'

    def __init__(self, phrases, city_codes, ads_count_for_one_key, pause_time_between_requests):
        ParserBase.__init__(self)

        self.__lock = threading.Lock()
        self.__need_to_stop_flag = False

        self.__logger = logging.getLogger(__name__)

        self.__logger.info(
            'Yandex Parser started with: %s, %s, %s, %s' %
            (phrases, city_codes, ads_count_for_one_key, pause_time_between_requests)
        )

        self.__phrases: list = phrases
        self.__city_codes: list = city_codes
        self.__ads_count_for_one_key: int = ads_count_for_one_key
        self.__pause_time_between_requests: int = pause_time_between_requests
        self.__driver = None

    def start(self):
        with self.__lock:
            self.__need_to_stop_flag = False

        self.__run_browser()

        for phrase in self.__phrases:
            result = []

            for city_code in self.__city_codes:
                if self.__need_to_stop():
                    break

                variables = {
                    YandexParser.TEXT_VARIABLE_NAME: phrase,
                    YandexParser.CITY_CODE_VARIABLE_NAME: city_code
                }

                self.__load_url(YandexParser.BASE_URL + '?' + urllib.parse.urlencode(variables))

                def parse_ads_city_phrase_loop():
                    nonlocal result

                    while len(result) < self.__ads_count_for_one_key:
                        result += self.__parse_loaded_page(self.__ads_count_for_one_key - len(result))

                        if len(result) >= self.__ads_count_for_one_key:
                            break
                        else:
                            try:
                                next_page_link = self.__driver.find_element_by_class_name('pager__item_kind_next')
                                time.sleep(self.__pause_time_between_requests / 1000)
                                self.__driver.execute_script('console.clear()')
                                next_page_link.click()
                            except NoSuchElementException as error:
                                self.__logger.warning('There is no more ads for phrase \'%s\'' % phrase)
                                self.__logger.warning(error)
                                break

                parse_ads_city_phrase_loop()
                self.__logger.info(result)

            result = self._remove_duplicated_hosts(result)
            DataCollector.store_ad_search_data('YandexParser', phrase, result)

        self.__driver.quit()
        self.__driver = None

    def stop(self):
        with self.__lock:
            self.__need_to_stop_flag = True
            del self.__driver
            self.__driver = None

    def __need_to_stop(self):
        with self.__lock:
            return self.__need_to_stop_flag

    def __parse_loaded_page(self, parse_count):
        try:
            ad_elements = self.__driver.find_elements_by_class_name('serp-item')

            result = []

            for ad in ad_elements:
                if len(result) >= parse_count:
                    break

                url = ad.find_element_by_class_name('organic__path').find_element_by_tag_name('b').text.strip()
                ad_text = ad.find_element_by_class_name('text-container').text.strip()
                ad_text = self.__replace_special_chars(ad_text)
                ad_header = self.__get_header(ad)

                ad_info = {
                    'url': url,
                    'ad_header': ad_header,
                    'ad_text': ad_text,
                    'phone': self.__try_parse_phone_number(self, ad)
                }

                result.append(ad_info)

            return result

        except Exception as error:
            self.__logger.error(error)
            return []

    def __load_url(self, url):
        max_attempt_number = 3

        while max_attempt_number > 0:
            try:
                return self.__load_page_helper(url)
            except WebDriverException as error:
                if self.__is_browser_running() is False:
                    self.__run_browser()
                    max_attempt_number -= 1
                    continue

                self.__logger.error(error)

    def __load_page_helper(self, url):
        self.__logger.info('Loading {0}'.format(url))
        self.__driver.execute_script('console.clear()')
        self.__driver.get(url)
        self.__logger.info('{0} loaded'.format(url))

    def __is_browser_running(self):
        browser_process = psutil.Process(self.__driver.service.process.pid)

        if browser_process.is_running():
            children = browser_process.children()
            return children and children[0]

        return False

    def __run_browser(self):
        self.__driver = WebDriverFactory.create(driver_type=WebDriverFactory.CHROME, headless=False)

    @staticmethod
    def __get_header(ad):
        ad_lines = ad.text.strip().split('\n')

        if ad_lines:
            return YandexParser.__replace_special_chars(ad_lines[0])

        return None

    @staticmethod
    def __has_contacts(ad):
        ad_lines = ad.text.strip().split('\n')
        return ad_lines[-1].find('Контактная') != -1

    @staticmethod
    def __replace_special_chars(text):
        return text.replace(';', ' ')\
            .replace('\n', ' ')\
            .replace('"', ' ')\
            .replace(',', ' ')

    @staticmethod
    def __prepare_phone_number(phone_number):
        return phone_number.replace('-', '')\
            .replace(' ', '')\
            .replace('(', '')\
            .replace(')', '')\
            .replace('+', '')\
            .replace(',', ' ')

    @staticmethod
    def __try_parse_phone_number(self, ad):
        phone_number = None

        if self.__has_contacts(ad):
            ad_info_elements = ad.find_elements_by_class_name('serp-meta__item')

            for i in range(len(ad_info_elements)):
                if ad_info_elements[i].text.find('Контактная информация') != -1:
                    if i + 1 == len(ad_info_elements):  # out of range (we can't parse phone)
                        break
                    phone_number = self.__prepare_phone_number(ad_info_elements[i + 1].text)
                    break

        return phone_number

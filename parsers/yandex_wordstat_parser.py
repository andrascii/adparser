import psutil
import logging
import time
import random
import threading
from data_collector import DataCollector
from parsers.parser_base import ParserBase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import WebDriverException, TimeoutException
from web_driver_factory import WebDriverFactory
from PySide2 import QtCore


class YandexWordstatParser(QtCore.QObject, ParserBase):
    on_completed = QtCore.Signal()

    BASE_URL = 'https://wordstat.yandex.ru'

    def __init__(self, phrases, login, password):
        super(YandexWordstatParser, self).__init__()
        ParserBase.__init__(self)

        self.__lock = threading.Lock()
        self.__need_to_stop_flag = False

        self.__logger = logging.getLogger(__name__)

        self.__logger.info(
            'Yandex Wordstat Parser started with: %s, %s, %s' %
            (phrases, login, password)
        )

        self.__phrases: list = phrases
        self.__login: str = login
        self.__password: str = password
        self.__driver = None

    def __del__(self):
        if not self.__driver:
            return
        self.__driver.quit()

    def start(self):
        with self.__lock:
            self.__need_to_stop_flag = False

        self.__run_browser()

        once_authorized = False

        self.__load_url(YandexWordstatParser.BASE_URL)

        for phrase in self.__phrases:
            self.__type_in_phrase_to_search_field_and_press_find(phrase)

            if not once_authorized:
                try:
                    self.__authorize_on_redirected_form()
                except TimeoutException:
                    self.__authorize()

                once_authorized = True

            # wait until DOM is not built to avoid selenium.common.exceptions.StaleElementReferenceException
            time.sleep(1)

            DataCollector.store_wordstat_data(self.__extract_keywords(), phrase)
            YandexWordstatParser.__random_wait(3000, 15000)

        self.__driver.quit()
        self.on_completed.emit()

    def stop(self):
        with self.__lock:
            self.__need_to_stop_flag = True

    def __need_to_stop(self):
        with self.__lock:
            return self.__need_to_stop_flag

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

    def __extract_keywords(self):
        similar_keywords_table = self.__get_element_by_xpath(
            '/html/body/div[2]/div/div/table/tbody/tr/td[4]/div/div/div[2]/div[2]/div/table')

        keyword_elements = similar_keywords_table.find_elements_by_tag_name('a')

        found_keywords = []

        for keyword_element in keyword_elements:
            if not keyword_element.text:
                continue

            found_keywords.append(keyword_element.text)

        return found_keywords

    def __run_browser(self):
        self.__driver = WebDriverFactory.create(driver_type=WebDriverFactory.CHROME, headless=False)

    def __authorize_on_redirected_form(self):
        login_element = self.__get_element_by_xpath('//*[@id="login"]')

        if not login_element:
            return

        self.__input(login_element, self.__login)

        password_element = self.__get_element_by_xpath('//*[@id="passwd"]')

        YandexWordstatParser.__random_wait(500, 800)
        self.__input(password_element, self.__password)

        YandexWordstatParser.__random_wait(100, 200)
        self.__get_element_by_xpath('//*[@id="nb-1"]/body/div/div[1]/div[3]/div/div[2]/form/div[4]/div/button').click()

    def __type_in_phrase_to_search_field_and_press_find(self, phrase):
        input_field_element = self.__get_input_field_element()
        input_field_element.clear()

        YandexWordstatParser.__random_wait(100, 200)
        self.__input(input_field_element, phrase)

        YandexWordstatParser.__random_wait(150, 250)
        self.__get_find_button().click()

    def __authorize(self):
        login_element = self.__get_element_by_xpath('//*[@id="b-domik_popup-username"]')

        if not login_element:
            return

        self.__input(login_element, self.__login)

        password_element = self.__get_element_by_xpath('//*[@id="b-domik_popup-password"]')
        self.__input(password_element, self.__password)

        self.__get_element_by_xpath(
            '/html/body/form/table/tbody/tr[2]/td[2]/div/div[5]/span[1]/input').click()

    def __get_input_field_element(self):
        parent_element = self.__get_element_by_css_selector(
            '''
            body > div.b-page__head-wrapper > table > tbody > tr > td.l-head__c > div > div > form > table > tbody > 
            tr:nth-child(1) > td.b-search__col.b-search__input > span > span
            '''
        )

        return parent_element.find_element_by_xpath('*')

    def __get_find_button(self):
        find_button_xpath = '/html/body/div[1]/table/tbody/tr/td[4]/div/div/form/table/tbody/tr[1]/td[2]/span/input'
        return self.__get_element_by_xpath(find_button_xpath)

    def __input(self, element, data):
        for item in data:
            element.send_keys(item)
            YandexWordstatParser.__random_wait(10, 250)

    def __get_element_by_xpath(self, xpath):
        WebDriverWait(self.__driver, 10).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, xpath)
            )
        )

        return self.__driver.find_element_by_xpath(xpath)

    def __get_element_by_css_selector(self, css_selector):
        WebDriverWait(self.__driver, 10).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, css_selector)
            )
        )

        return self.__driver.find_element_by_css_selector(css_selector)

    @staticmethod
    def __random_wait(lower, upper):
        time.sleep(random.randint(lower, upper) / 1000)

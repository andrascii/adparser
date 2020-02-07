import logging
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class WebDriverFactory:
    CHROME = 0
    FIREFOX = 1
    OPERA = 2
    PHANTOM_JS = 3
    IE = 4

    @staticmethod
    def create(driver_type, headless):
        if driver_type == WebDriverFactory.CHROME:
            return WebDriverFactory.__create_chrome_driver(headless)

        raise Exception('This driver type is not supported yet')

    @staticmethod
    def __create_chrome_driver(headless: bool):
        capabilities = DesiredCapabilities.CHROME
        capabilities['loggingPrefs'] = {'performance': 'ALL'}
        options = webdriver.ChromeOptions()

        if headless is True:
            options.add_argument('--headless')

        logger = logging.getLogger(__name__)
        logger.info('Starting Google Chrome browser...')
        driver = webdriver.Chrome(desired_capabilities=capabilities, chrome_options=options)
        logger.info('Browser started')

        return driver

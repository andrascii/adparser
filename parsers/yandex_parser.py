from selenium.webdriver import Chrome
from parsers.parser_base import ParserBase


class YandexParser(ParserBase):
    def __init__(self, driver: Chrome, config):
        ParserBase.__init__(self)
        self.__driver: Chrome = driver

    def parse(self):
        try:
            ad_elements = self.__driver.find_elements_by_class_name('serp-item')

            result = []

            for ad in ad_elements:
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
            print(error)
            return None

    @staticmethod
    def __get_header(ad):
        ad_lines = ad.text.strip().split('\n')

        if ad_lines:
            return ad_lines[0]

        return None

    @staticmethod
    def __has_contacts(ad):
        ad_lines = ad.text.strip().split('\n')
        return ad_lines[-1].find('Контактная') != -1

    @staticmethod
    def __replace_special_chars(text):
        return text.replace(';', ' ').replace('\n', ' ').replace('"', ' ').replace(',', ' ')

    @staticmethod
    def __prepare_phone_number(phone_number):
        return phone_number.replace('-', '').replace(' ', '').replace('(', '').replace(')', '').replace('+', '')

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

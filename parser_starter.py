import threading
from window import Window
from helpers import show_message_box
from parsers.yandex_parser import YandexParser
from parsers.yandex_wordstat_parser import YandexWordstatParser


class ParserStarter:
    def __init__(self, app):
        self.__app = app
        self.__active_parser = None
        self.__active_thread = None

    def on_start_clicked(self, phrases, codes, search_engine_code, ads_count_for_one_key,
                         pause_time_between_requests, login, password):
        if not self.__start_or_inform():
            return

        if search_engine_code == Window.SEARCH_ENGINE_YANDEX:
            self.__active_parser = YandexParser(phrases, codes, ads_count_for_one_key, pause_time_between_requests)
        elif search_engine_code == Window.SEARCH_ENGINE_YANDEX_WORDSTAT:
            self.__active_parser = YandexWordstatParser(phrases, login, password)
        else:
            self.__active_parser = None

        if self.__active_parser:
            self.__active_thread = threading.Thread(target=self.__active_parser.start)
            self.__active_thread.start()

    def on_stop_clicked(self):
        if not self.__active_parser or not self.__active_thread:
            return
        self.__active_parser.stop()
        self.__active_thread.join()
        self.__active_parser = None
        self.__active_thread = None

    def __start_or_inform(self):
        if not self.__active_parser:
            return True

        if self.__active_thread.is_alive():
            show_message_box(self.__app, 'Парсер уже запущен')
            return False

        self.__active_thread = None
        self.__active_thread = None

        return True

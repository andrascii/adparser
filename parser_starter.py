import os
import csv
from window import Window
from helpers import show_message_box
from parsers.yandex_parser import YandexParser
from parsers.yandex_wordstat_parser import YandexWordstatParser
from PySide2 import QtCore


class ParserStarter(QtCore.QObject):
    __start_parser_signal = QtCore.Signal()
    
    def __init__(self, main_window):
        super().__init__()
        
        self.__main_window = main_window
        self.__active_parser = None
        self.__active_thread = None
        self.__phrases = None
        self.__codes = None
        self.__search_engine = None
        self.__ads_count_for_one_key = None
        self.__pause_between_requests = None
        self.__login = None
        self.__password = None

    def __del__(self):
        self.on_stop_clicked()

    def on_start_clicked(self, phrases, codes, search_engine_code, ads_count_for_one_key,
                         pause_time_between_requests, login, password):
        if not self.__start_or_inform():
            return

        self.__phrases = phrases
        self.__codes = codes
        self.__search_engine = search_engine_code
        self.__ads_count_for_one_key = ads_count_for_one_key
        self.__pause_between_requests = pause_time_between_requests
        self.__login = login
        self.__password = password

        self.__create_and_start_parser(
            self.__phrases,
            self.__codes,
            self.__search_engine,
            self.__ads_count_for_one_key,
            self.__pause_between_requests,
            self.__login,
            self.__password)

    def on_stop_clicked(self):
        if not self.__active_parser or not self.__active_thread:
            return
        self.__active_parser.stop()
        self.__active_thread.quit()
        self.__active_thread.wait()
        self.__active_parser = None
        self.__active_thread = None

    def __on_about_parser_completed(self):
        if self.__search_engine != Window.SEARCH_ENGINE_YANDEX_WORDSTAT:
            self.on_stop_clicked()
            return

        self.__search_engine = Window.SEARCH_ENGINE_YANDEX

        print('phrases before')
        print(self.__phrases)

        self.__phrases = ParserStarter.__read_wordstat_phrases()
        self.__remove_folder('data/wordstat/')

        print('phrases before')
        print(self.__phrases)

        self.__create_and_start_parser(
            self.__phrases,
            self.__codes,
            self.__search_engine,
            self.__ads_count_for_one_key,
            self.__pause_between_requests,
            self.__login,
            self.__password)

    def __create_and_start_parser(self, phrases, codes, search_engine_code, ads_count_for_one_key,
                                  pause_time_between_requests, login, password):
        if search_engine_code == Window.SEARCH_ENGINE_YANDEX:
            self.__active_parser = YandexParser(phrases, codes, ads_count_for_one_key, pause_time_between_requests)
        elif search_engine_code == Window.SEARCH_ENGINE_YANDEX_WORDSTAT:
            self.__active_parser = YandexWordstatParser(phrases, login, password)
        else:
            self.__active_parser = None

        if self.__active_parser:
            if not self.__active_thread or not self.__active_thread.isRunning():
                self.__active_thread = QtCore.QThread()

            self.__active_parser.moveToThread(self.__active_thread)
            self.__start_parser_signal.connect(self.__active_parser.start)
            self.__active_parser.on_completed.connect(self.__on_about_parser_completed)
            self.__active_parser.on_completed.connect(self.__active_parser.deleteLater)
            self.__active_thread.start()
            self.__start_parser_signal.emit()

    def __start_or_inform(self):
        if not self.__active_parser:
            return True

        if self.__active_thread.isRunning():
            show_message_box(self.__main_window, 'Парсер уже запущен')
            return False

        self.__active_thread = None
        self.__active_thread = None

        return True

    @staticmethod
    def __read_wordstat_phrases():
        result = []
        with os.scandir('data/wordstat') as entries:
            for entry in entries:
                if entry.is_file():
                    with open('data/wordstat/' + entry.name, 'r', encoding='utf-8') as csv_file:
                        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        for row in csv_reader:
                            result.append(row[0])

        return result

    @staticmethod
    def __remove_folder(folder):
        with os.scandir(folder) as entries:
            for entry in entries:
                if entry.is_file():
                    os.remove(entry)
                elif entry.is_folder():
                    ParserStarter.__remove_folder(entry)

        os.rmdir(folder)

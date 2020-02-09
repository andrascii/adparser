import sys
import json
import logging
import threading
from window import Window
from helpers import show_message_box
from parsers.yandex_parser import YandexParser
from PySide2 import QtWidgets

logging.basicConfig(filename="ad_parser.log", level=logging.INFO)


class Parser:
    def __init__(self):
        self.__active_parser = None
        self.__active_thread = None

    def on_start(self, phrases, codes, search_engine_code, ads_count_for_one_key, pause_time_between_requests):
        if self.__active_parser:
            show_message_box(None, 'Парсер уже запущен')
            return

        if search_engine_code == Window.SEARCH_ENGINE_YANDEX:
            self.__active_parser = YandexParser(phrases, codes, ads_count_for_one_key, pause_time_between_requests)
        else:
            self.__active_parser = None

        if self.__active_parser:
            self.__active_thread = threading.Thread(target=self.__active_parser.start)
            self.__active_thread.start()

    def on_stop(self):
        if not self.__active_parser or not self.__active_thread:
            return
        self.__active_parser.stop()
        self.__active_thread.join()
        self.__active_parser = None
        self.__active_thread = None



def main():
    logger = logging.getLogger(__name__)
    logger.info('AdParser started')

    app = QtWidgets.QApplication([])

    with open('settings.json', 'r', encoding='utf-8') as settings_file:
        settings_map = json.load(settings_file)

    if not settings_map:
        show_message_box(None, 'Не найден файл настроек settings.json или он пуст')
        return

    parser = Parser()

    window = Window(settings_map)
    window.on_about_start.connect(parser.on_start)
    window.on_about_stop.connect(parser.on_stop)
    window.show()
    window.adjustSize()

    exit_code = app.exec_()
    logger.info('AdParser closed')
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

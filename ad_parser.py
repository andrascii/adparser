import sys
import json
import logging
from window import Window
from helpers import show_message_box
from parsers.yandex_parser import YandexParser
from PySide2 import QtWidgets

logging.basicConfig(filename="ad_parser.log", level=logging.INFO)


def on_start(phrases, codes, search_engine_code, ads_count_for_one_key, pause_time_between_requests):
    if search_engine_code == Window.SEARCH_ENGINE_YANDEX:
        ad_parser = YandexParser(phrases, codes, ads_count_for_one_key, pause_time_between_requests)
    else:
        ad_parser = None

    if ad_parser:
        ad_parser.start()


def on_stop():
    pass


def main():
    logger = logging.getLogger(__name__)
    logger.info('AdParser started')

    app = QtWidgets.QApplication([])

    with open('settings.json', 'r') as settings_file:
        settings_map = json.load(settings_file)

    if not settings_map:
        show_message_box(None, 'Не найден файл настроек settings.json или он пуст')
        return

    window = Window(settings_map)
    window.on_about_start.connect(on_start)
    window.on_about_stop.connect(on_stop)
    window.show()
    window.adjustSize()

    exit_code = app.exec_()
    logger.info('AdParser closed')
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

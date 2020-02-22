import sys
import json
import logging
from parser_starter import ParserStarter
from window import Window
from helpers import show_message_box
from PySide2 import QtWidgets

logging.basicConfig(filename="ad_parser.log", level=logging.INFO)


def read_settings_map():
    with open('settings.json', 'r', encoding='utf-8') as settings_file:
        return json.load(settings_file)


def main():
    logger = logging.getLogger(__name__)
    logger.info('AdParser started')

    app = QtWidgets.QApplication([])
    settings_map = read_settings_map()

    if not settings_map:
        show_message_box(None, 'Не найден файл настроек settings.json или он пуст')
        return

    window = Window(settings_map)
    parser = ParserStarter(window)
    window.on_about_start.connect(parser.on_start_clicked)
    window.on_about_stop.connect(parser.on_stop_clicked)
    window.show()
    window.adjustSize()

    exit_code = app.exec_()
    logger.info('AdParser closed')
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

import sys
import json
import urllib.parse
from window import Window
from PySide2 import QtCore, QtWidgets, QtGui
from iloader import ILoader
from loader_factory import LoaderFactory


def on_start(phrases, codes, search_engine_code, ads_count_for_one_key, pause_time_between_requests):
    print(phrases, codes, search_engine_code, ads_count_for_one_key, pause_time_between_requests)
    factory = LoaderFactory(True)
    loader = factory.create()
    result = loader.load_page('https://yandex.ru/search/ads?' + urllib.parse.urlencode({'text': 'авиабилеты', 'lr': 213}))
    print(result)

def on_stop():
    pass


def main():
    app = QtWidgets.QApplication([])

    settings_map = None

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

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

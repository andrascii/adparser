import sys
import json
from PySide2 import QtCore, QtWidgets, QtGui


class AdParserWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # city name => city code
        self.__cities = {}

        # list of check boxes with associated city codes
        self.__cities_check_boxes = {}

        self.__initialize()

    def __initialize(self):
        self.__initialize_cities_map()
        self.__create_ads_count_layout()
        self.__create_pause_time_layout()
        self.__create_cities_widget()
        self.__create_start_stop_layout()
        self.__create_keys_text_edit_layout()
        self.__layout = QtWidgets.QVBoxLayout()
        self.__layout.addLayout(self.__ads_count_layout)
        self.__layout.addLayout(self.__pause_time_layout)
        self.__layout.addWidget(self.__cities_scroll_area)
        self.__layout.addLayout(self.__keys_text_edit_layout)
        self.__layout.addLayout(self.__start_stop_layout)
        self.setLayout(self.__layout)

    def __create_ads_count_layout(self):
        self.__ads_count_layout = QtWidgets.QHBoxLayout()
        ads_count_label = QtWidgets.QLabel('Максимальное количество объявлений с одного ключа:')
        self.__ads_count_spin_box = QtWidgets.QSpinBox(self)
        self.__ads_count_spin_box.setMinimum(0)
        self.__ads_count_spin_box.setMaximum(1000)
        self.__ads_count_spin_box.setValue(10)
        self.__ads_count_layout.addWidget(ads_count_label)
        self.__ads_count_layout.addWidget(self.__ads_count_spin_box)

    def __create_pause_time_layout(self):
        self.__pause_time_layout = QtWidgets.QHBoxLayout()
        pause_time_label = QtWidgets.QLabel('Задержка между запросами в миллисекундах:')
        self.__pause_time_spin_box = QtWidgets.QSpinBox()
        self.__pause_time_spin_box.setMinimum(0)
        self.__pause_time_spin_box.setMaximum(999999999)
        self.__pause_time_spin_box.setValue(2000)
        self.__pause_time_layout.addWidget(pause_time_label)
        self.__pause_time_layout.addWidget(self.__pause_time_spin_box)

    def __create_cities_widget(self):
        self.__cities_widget = QtWidgets.QWidget(self)
        self.__cities_widget_layout = QtWidgets.QVBoxLayout()

        for name, code in self.__cities.items():
            checkbox = QtWidgets.QCheckBox(name, self)
            self.__cities_widget_layout.addWidget(checkbox)
            self.__cities_check_boxes[code] = checkbox

        self.__cities_scroll_area = QtWidgets.QScrollArea()
        self.__cities_widget.setLayout(self.__cities_widget_layout)
        self.__cities_scroll_area.setWidget(self.__cities_widget)

    def __create_start_stop_layout(self):
        self.__start_stop_layout = QtWidgets.QHBoxLayout()
        self.__start_button = QtWidgets.QPushButton('Старт')
        self.__stop_button = QtWidgets.QPushButton('Стоп')
        self.__start_button.clicked.connect(self.__start)
        self.__stop_button.clicked.connect(self.__stop)
        self.__start_stop_layout.addWidget(self.__start_button)
        self.__start_stop_layout.addWidget(self.__stop_button)

    def __create_keys_text_edit_layout(self):
        self.__keys_text_edit_layout = QtWidgets.QVBoxLayout()
        keys_text_edit_label = QtWidgets.QLabel('Ключевые фразы (по одной на каждую строку):')
        self.__keys_text_edit = QtWidgets.QTextEdit()
        self.__keys_text_edit_layout.addWidget(keys_text_edit_label)
        self.__keys_text_edit_layout.addWidget(self.__keys_text_edit)

    def __initialize_cities_map(self):
        with open('settings.json', 'r') as settings_file:
            settings_map = json.load(settings_file)

            for city in settings_map['cities']:
                for name, code in city.items():
                    self.__cities[name] = code

    def __start(self):
        phrases = self.__keys_text_edit.toPlainText().strip()

        if not phrases:
            message_box = QtWidgets.QMessageBox(self)
            message_box.setText('Не задана ни одна ключевая фраза')
            message_box.exec()

        phrases = phrases.split('\n')

        for code, checkbox in self.__cities_check_boxes.items():
            if checkbox.isChecked():
                print(code)

    @staticmethod
    def __stop():
        print('Stop')


def main():
    app = QtWidgets.QApplication([])

    widget = AdParserWindow()
    widget.show()
    widget.adjustSize()

    sys.exit(app.exec_())


def prepare():
    result = {}

    with open('regions.txt', 'r') as regions:
        data = regions.read()
        data = data.split('\n')

        for i in range(len(data) - 1):
            result[int(data[i].encode('utf-8'))] = data[i + 1].strip()

    with open('settings_.json', 'w') as settings:
        json.dump(result, settings)


if __name__ == '__main__':
    main()

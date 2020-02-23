from helpers import show_message_box
from PySide2 import QtCore, QtWidgets


class Window(QtWidgets.QWidget):
    on_about_start = QtCore.Signal(list, list, int, int, int, str, str)
    on_about_stop = QtCore.Signal()

    SEARCH_ENGINE_YANDEX = 0
    SEARCH_ENGINE_YANDEX_WORDSTAT = 1
    SEARCH_ENGINE_GOOGLE = 2

    def __init__(self, settings_map):
        super().__init__()

        # city name => city code
        self.__cities = {}

        # list of check boxes with associated city codes
        self.__cities_check_boxes = {}

        self.__initialize(settings_map)

    def __initialize(self, settings_map):
        self.__initialize_cities_map(settings_map)
        self.__create_ads_count_widget()
        self.__create_pause_time_widget()
        self.__create_cities_widget()
        self.__create_start_stop_layout()
        self.__create_keys_text_edit_layout()
        self.__create_search_engine_selection_layout()
        self.__create_auth_fields_widget()
        self.__layout = QtWidgets.QVBoxLayout()
        self.__layout.addLayout(self.__search_engine_selection_layout)
        self.__layout.addWidget(self.__ads_count_widget)
        self.__layout.addWidget(self.__pause_time_widget)
        self.__layout.addWidget(self.__cities_scroll_area)
        self.__layout.addLayout(self.__keys_text_edit_layout)
        self.__layout.addWidget(self.__auth_fields_widget)
        self.__layout.addLayout(self.__start_stop_layout)
        self.setLayout(self.__layout)

        self.__auth_fields_widget.hide()

    def __create_ads_count_widget(self):
        self.__ads_count_widget = QtWidgets.QWidget(self)
        ads_count_layout = QtWidgets.QHBoxLayout(self.__ads_count_widget)
        ads_count_label = QtWidgets.QLabel('Максимальное количество объявлений с одного ключа:')
        self.__ads_count_spin_box = QtWidgets.QSpinBox(self)
        self.__ads_count_spin_box.setMinimum(0)
        self.__ads_count_spin_box.setMaximum(1000)
        self.__ads_count_spin_box.setValue(10)
        ads_count_layout.addWidget(ads_count_label)
        ads_count_layout.addWidget(self.__ads_count_spin_box)

    def __create_pause_time_widget(self):
        self.__pause_time_widget = QtWidgets.QWidget(self)
        pause_time_layout = QtWidgets.QHBoxLayout(self.__pause_time_widget)
        pause_time_label = QtWidgets.QLabel('Задержка между запросами в миллисекундах:')
        self.__pause_time_spin_box = QtWidgets.QSpinBox()
        self.__pause_time_spin_box.setMinimum(0)
        self.__pause_time_spin_box.setMaximum(999999999)
        self.__pause_time_spin_box.setValue(2000)
        pause_time_layout.addWidget(pause_time_label)
        pause_time_layout.addWidget(self.__pause_time_spin_box)

    def __create_search_engine_selection_layout(self):
        self.__search_engine_selection_layout = QtWidgets.QHBoxLayout()
        text_label = QtWidgets.QLabel('Поисковая система:')
        self.__search_engine_combo_box = QtWidgets.QComboBox()
        self.__search_engine_combo_box.addItem('Яндекс', self.SEARCH_ENGINE_YANDEX)
        self.__search_engine_combo_box.addItem('Яндекс Вордстат', self.SEARCH_ENGINE_YANDEX_WORDSTAT)
        self.__search_engine_combo_box.addItem('Google', self.SEARCH_ENGINE_GOOGLE)
        self.__search_engine_combo_box.currentIndexChanged.connect(self.__search_engine_changed)
        self.__search_engine_selection_layout.addWidget(text_label)
        self.__search_engine_selection_layout.addWidget(self.__search_engine_combo_box)

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
        self.__start_stop_layout.addWidget(self.__start_button)
        self.__start_stop_layout.addWidget(self.__stop_button)
        self.__start_button.clicked.connect(self.__start)
        self.__stop_button.clicked.connect(self.__stop)

    def __create_keys_text_edit_layout(self):
        self.__keys_text_edit_layout = QtWidgets.QVBoxLayout()
        keys_text_edit_label = QtWidgets.QLabel('Ключевые фразы (по одной на каждую строку):')
        self.__keys_text_edit = QtWidgets.QTextEdit()
        self.__keys_text_edit_layout.addWidget(keys_text_edit_label)
        self.__keys_text_edit_layout.addWidget(self.__keys_text_edit)

    def __create_auth_fields_widget(self):
        self.__auth_fields_widget = QtWidgets.QWidget(self)
        auth_fields_layout = QtWidgets.QVBoxLayout(self.__auth_fields_widget)

        login_horizontal_layout = QtWidgets.QHBoxLayout()
        login_label = QtWidgets.QLabel('Логин:')
        self.__login_line_edit = QtWidgets.QLineEdit()
        login_horizontal_layout.addWidget(login_label)
        login_horizontal_layout.addWidget(self.__login_line_edit)

        password_horizontal_layout = QtWidgets.QHBoxLayout()
        password_label = QtWidgets.QLabel('Пароль:')
        self.__password_line_edit = QtWidgets.QLineEdit()
        self.__password_line_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        password_horizontal_layout.addWidget(password_label)
        password_horizontal_layout.addWidget(self.__password_line_edit)

        auth_fields_layout.addLayout(login_horizontal_layout)
        auth_fields_layout.addLayout(password_horizontal_layout)

    def __initialize_cities_map(self, settings_map):
        for city in settings_map['cities']:
            for name, code in city.items():
                self.__cities[name] = code

    def __start(self):
        phrases = self.__keys_text_edit.toPlainText().strip()

        if not phrases:
            show_message_box(self, 'Не задана ни одна ключевая фраза')
            return

        phrases = phrases.split('\n')

        codes = []

        for code, checkbox in self.__cities_check_boxes.items():
            if checkbox.isChecked():
                codes.append(code)

        if not codes and self.__selected_search_engine() != Window.SEARCH_ENGINE_YANDEX_WORDSTAT:
            show_message_box(self, 'Не выбран ни один регион для поиска объявлений')
            return

        ads_count_for_one_key = self.__ads_count_spin_box.value()
        pause_time_between_requests = self.__pause_time_spin_box.value()

        self.on_about_start.emit(
            phrases,
            codes,
            self.__selected_search_engine(),
            ads_count_for_one_key,
            pause_time_between_requests,
            self.__login_line_edit.text(),
            self.__password_line_edit.text()
        )

    def __stop(self):
        self.on_about_stop.emit()

    def __search_engine_changed(self):
        search_engine = self.__selected_search_engine()

        if search_engine == Window.SEARCH_ENGINE_YANDEX_WORDSTAT:
            self.__auth_fields_widget.show()
        else:
            self.__auth_fields_widget.hide()

    def __selected_search_engine(self):
        return self.__search_engine_combo_box.itemData(self.__search_engine_combo_box.currentIndex())

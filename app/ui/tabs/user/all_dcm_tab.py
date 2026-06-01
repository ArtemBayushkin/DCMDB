# team_tab.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QPushButton, QHBoxLayout, QLineEdit)

from app.core.base_tab import BaseTab
from app.db.dcm_manager import DcmManager
from app.ui.components.searchable_table import AdvancedTableView
from app.config.settings_manager import settings


class AllDcmTab(BaseTab):
    def __init__(self, main_window=None):
        super().__init__("Все вопросы в работе", icon="📋", space=0, main_window=main_window)

    def add_content(self):
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.layout.addLayout(self.ctrl_layout())
        self.table = AdvancedTableView()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        self.load_data()

    def load_data(self, force: bool = False):
        print("AllDcmTab.load data -> start")
        if not settings.get_main_db_path():
            print("AllDcmTab.load data -> not settings.get_main_db_path()")
            self.status_bar.show_warning("База данных не настроена. Перейдите в Настройки для подключения БД.")
            return

        if not force and not self._confirm_unsaved("Обновить данные и потерять изменения"):
            print("AllDcmTab.load data -> not force and not self._confirm_unsaved")
            return

        self.table.proxy_model.setSourceModel(None)
        self.model = None
        print("AllDcmTab.load_data -> start _mgr.load_data")
        if self._mgr is None:
            self._mgr = DcmManager()
        with self._mgr as mgr:
            model = mgr.load_data(
                limit=1000,
                in_send=False,
                archive=False,
                columns=[
                    "ID",
                    "Date of meeting",
                    "Urgent/Срочный",
                    "Code of the WD or MD",
                    "Description of problem",
                    "Appendix",
                    "Symbols of decisions under the Protocol",
                    "Текст решения, дата",
                    "Texts of  decisions, date",
                    "Desighner's surname",
                    "Приложение",
                    "Заметка",
                    "Требуется уточнение",
                    "В отправку",
                ]
            )

        if model.rowCount() == 0:
            self._status_info("Нет данных для отображения")
            return

        self.table.proxy_model.setSourceModel(model)
        self.table.apply_column_config(row_height=50)
        self.model = model
        self._status_info(f"Загружено строк: {model.rowCount()}")

    def ctrl_layout(self):
        controls_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Поиск по тексту/зданию...")
        search_button = QPushButton("Поиск")
        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.load_data)
        save_button = QPushButton("Сохранить изменения")
        save_button.clicked.connect(self.save_changes)

        search_input.textChanged.connect(
            lambda text: self.table.proxy_model.setFilterFixedString(text)
        )

        controls_layout.addWidget(search_input)
        controls_layout.addWidget(search_button)
        controls_layout.addWidget(refresh_button)
        controls_layout.addWidget(save_button)

        print(f"Controls layout has {controls_layout.count()} widgets")
        return controls_layout

    def search(self, text=""):
        pass
        try:
            matching_items = self.table.findItems(text, Qt.MatchContains)
            if matching_items:
                for item in matching_items:
                    item.setSelected(True)
        except Exception as e:
            print(f"AllDcmTab.search -> Error: {e}")

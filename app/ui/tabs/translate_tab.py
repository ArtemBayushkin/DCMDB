# team_tab.py
from PyQt6.QtWidgets import (QPushButton, QTableView,
                             QHeaderView, QAbstractItemView,
                             QHBoxLayout, QLineEdit)

from app.core.base_tab import BaseTab
from app.db.dcm_manager import DcmManager
from app.ui.components.editable_table_view import EditablePandasModel


class TranslateTab(BaseTab):
    def __init__(self, main_window=None):
        super().__init__("Проверка перевода", space=0)
        self.model = None
        self.table = None
        self.main_window = main_window

    def add_content(self):
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        self.layout.addLayout(self.ctrl_layout())

        # Таблица
        self.table = QTableView()
        # self.table.setAlternatingRowColors(True)  # зеброобразные строки
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.verticalHeader().setVisible(True)  # можно скрыть номера строк

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setProperty("copyEnabled", True)

        self.load_data()

        self.layout.addWidget(self.table)

        # Кнопки (пример)
        # btn_refresh = QPushButton("Обновить список")
        # btn_refresh.clicked.connect(self.refresh_data)
        # main_layout.addWidget(btn_refresh)

        # Можно добавить поиск, фильтры и т.д. позже
        self.setLayout(self.layout)

    def load_data(self):
        with DcmManager() as mgr:
            df = mgr.get_data(
                limit=50,
                need_clarification=False,
                in_send=True,
                translate=False,
                archive=False,
                columns=[
                    "Перевод проверен",
                    "ID",
                    "Date of meeting",
                    "Code of the WD or MD",
                    "Description of problem",
                    "Appendix",
                    "Текст решения, дата",
                    "Texts of  decisions, date",
                    "Desighner's surname",
                    "Приложение",
                    "Заметка"
                ]
            )

        if not df.empty:
            self.model = EditablePandasModel(df)  # Editable версия!
            self.table.setModel(self.model)
            # self.status_message("Обновлено")
        else:
            self.table.setModel(EditablePandasModel.moke())

    def save_changes(self):
        """Сохранение изменений (отложенное, bulk)"""
        if hasattr(self, 'model') and isinstance(self.model, EditablePandasModel):
            changes = self.model.get_changes()
            with DcmManager() as mgr:
                if mgr.bulk_update(changes):
                    # self.status_bar.info_dialog(parent=self, message="Изменения сохранены успешно!")
                    self.load_data()  # Refresh после сохранения

    def ctrl_layout(self):
        controls_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Поиск по тексту/зданию...")
        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.load_data)
        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.load_data)
        save_button = QPushButton("Сохранить изменения")
        save_button.clicked.connect(self.save_changes)

        controls_layout.addWidget(search_input)
        controls_layout.addWidget(search_button)
        controls_layout.addWidget(refresh_button)
        controls_layout.addWidget(save_button)

        print(f"Controls layout has {controls_layout.count()} widgets")
        return controls_layout

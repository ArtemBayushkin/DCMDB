from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QLineEdit

from app.core.base_tab import BaseTab
from app.db.dcm_manager import DcmManager
from app.ui.components.searchable_table import AdvancedTableView
# from app.excel.excel_manager import ExcelParser


class ArchiveCQTab(BaseTab):
    def __init__(self, main_window=None):
        print("ArchiveCQTab.__init__ -> start")
        super().__init__("Срочные DCM в архив", space=0, main_window=main_window)
        print("ArchiveCQTab.__init__ -> super().__init__ done")

    def add_content(self):
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.layout.addLayout(self.ctrl_layout())
        self.table = AdvancedTableView()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        self.load_data()

    def ctrl_layout(self):
        controls_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Поиск по тексту...")
        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.load_data)
        save_button = QPushButton("Сохранить изменения")
        save_button.clicked.connect(self.save_changes)

        search_input.textChanged.connect(
            lambda text: self.table.proxy_model.setFilterFixedString(text)
        )

        controls_layout.addWidget(search_input)
        controls_layout.addWidget(refresh_button)
        controls_layout.addWidget(save_button)

        print(f"Controls layout has {controls_layout.count()} widgets")
        return controls_layout

    def load_data(self, checked=None, force: bool = False):

        if not force and not self._confirm_unsaved("Обновить данные и потерять изменения"):
            return

        self.table.proxy_model.setSourceModel(None)
        self.model = None
        if self._mgr is None:
            self._mgr = DcmManager()
        with self._mgr as mgr:
            model = mgr.load_data(
                limit=1500,
                archive=False,
                columns=[
                    "Desighner's surname",
                    "Date of meeting",
                    "ID",
                    "Требуется уточнение",
                    "В отправку",
                    "Дата изменения текста ответа",
                    "Отправлен Заказчику",
                    "Дата отправки Заказчику",
                    "В архив",
                ],
                order='[Дата отправки Заказчику]'
            )

        if model.rowCount() == 0:
            self._status_info("Нет данных для отображения")
            return

        self.table.proxy_model.setSourceModel(model)
        self.table.apply_column_config(row_height=50)
        self.model = model
        self._status_info(f"Загружено строк: {model.rowCount()}")

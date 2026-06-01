from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QLineEdit

from app.core.base_tab import BaseTab
from app.db.dcm_manager import DcmManager
from app.ui.components.searchable_table import AdvancedTableView
from app.excel.excel_manager import ExcelParser


class CqClar(BaseTab):
    def __init__(self, main_window=None):
        print("CqClar.__init__ -> start")
        super().__init__("Срочные вопросы DCM на уточнении", space=0, main_window=main_window)
        print("CqClar.__init__ -> super().__init__ done")

    def add_content(self):
        print("TranslateTab.add_content -> start")
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.layout.addLayout(self._build_controls())
        self.table = AdvancedTableView()
        print("TranslateTab.add_content -> AdvancedTableView created")
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        print("TranslateTab.add_content -> layout set, calling load_data...")
        self.load_data()
        print("TranslateTab.add_content -> load_data returned OK")

    def _confirm_unsaved(self, action: str = "продолжить"):
        return True

    def load_data(self, checked=None, force: bool = False):
        columns = [
            "ID", "Date of meeting", "Code of the WD or MD",
            "Description of problem", "Symbols of decisions under the Protocol",
            "Appendix", "Текст решения, дата",
            "Texts of  decisions, date", "Desighner's surname", "Приложение", "В отправку",
            "Требуется уточнение"
        ]

        print("SendCqTab.load_data -> clearing old model...")
        self.table.proxy_model.setSourceModel(None)
        self.model = None
        print("SendCqTab.load_data -> clearing old model success")

        print("SendCqTab.load_data -> calling DcmManager...")
        if self._mgr is None:
            self._mgr = DcmManager()
        with self._mgr as mgr:
            print("SendCqTab.load_data -> calling mgr.load_data...")
            model = mgr.load_data(
                limit=300,
                archive=False,
                in_working=True,
                in_send=False,
                need_clarification=True,
                columns=columns,
            )
            print(f"SendCqTab.load_data -> _mgr.load_data returned | rows={model.rowCount()}")

        if model.rowCount() == 0:
            self._status_info("Нет данных для отображения")
            return

        print("SendCqTab.load_data -> calling setSourceModel...")
        self.table.proxy_model.setSourceModel(model)
        print("SendCqTab.load_data -> setSourceModel OK")

        print("SendCqTab.load_data -> calling apply_column_config...")
        self.table.apply_column_config()
        print("SendCqTab.load_data -> apply_column_config OK")

        self.model = model
        print("SendCqTab.load_data -> COMPLETE")
        print("SendCqTab.load_data -> _mgr.close() COMPLETE")
        self._status_info(f"Загружено строк: {model.rowCount()}")

    def _build_controls(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Поиск по тексту...")
        search_input.setFixedWidth(200)
        upload_btn = QPushButton("Выгрузить в Excel")
        refresh_btn = QPushButton("Обновить")

        search_input.textChanged.connect(
            lambda text: self.table.proxy_model.setFilterFixedString(text)
        )

        upload_btn.clicked.connect(self.upload_excel)
        refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(search_input)
        layout.addWidget(upload_btn)
        layout.addWidget(refresh_btn)
        return layout

    def upload_excel(self):
        if not self.model:
            return self._status_warning("Нет данных для экспорта.")
        if ExcelParser.write_excel(self.model._dataframe):
            print("upload_excel - success")
            return self._status_success("Файл успешно сохранен")
        else:
            return self._status_warning("Ошибка сохранения файла")

from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QLineEdit

from app.core.base_tab import BaseTab
from app.db.dcm_manager import DcmManager
from app.ui.components.searchable_table import AdvancedTableView
from app.excel.excel_manager import ExcelParser


class SendDcmTab(BaseTab):
    def __init__(self, main_window=None):
        print("SendDcmTab.__init__ -> start")
        super().__init__("Основные DCM в отправку", space=0, main_window=main_window)
        print("SendDcmTab.__init__ -> super().__init__ done")

    def add_content(self):
        print("SendDcmTab.add_content -> start")
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.layout.addLayout(self._build_controls())
        self.table = AdvancedTableView()
        print("SendDcmTab.add_content -> AdvancedTableView created")
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        print("SendDcmTab.add_content -> layout set, calling load_data...")
        print("SendDcmTab.add_content -> load_data returned OK")

    def load_data(self, force: bool = False):
        date = self.search_input.text()
        print("SendDcm.load_data -> date = ", date)
        if date is "":
            return self._status_warning("Введите в поле дату!")
        columns = [
            "ID", "Date of meeting", "Code of the WD or MD",
            "Description of problem", "Symbols of decisions under the Protocol",
            "Appendix", "Текст решения, дата", "Перевод проверен",
            "Texts of  decisions, date", "Desighner's surname", "Приложение", "В отправку",
            "Дата изменения текста ответа", "Дата отправки Заказчику", "Отправлен Заказчику"
        ]
        print(f"SendDcmTab.load_data -> start | force={force}")
        if not force and not self._confirm_unsaved("Обновить данные и потерять изменения"):
            print("SendDcmTab.load_data -> data is unsaved and close/refresh")
            return

        print("SendDcmTab.load_data -> clearing old model...")
        self.table.proxy_model.setSourceModel(None)
        self.model = None
        print("SendDcmTab.load_data -> clearing old model success")

        print("SendDcmTab.load_data -> calling DcmManager...")
        if self._mgr is None:
            self._mgr = DcmManager()
        with self._mgr as mgr:
            print("SendDcmTab.load_data -> calling mgr.load_data...")
            model = mgr.load_data(
                limit=1000,
                date_of_meeting=date,
                in_working=False,
                is_urgent=False,
                order='[Код]',
                columns=columns
            )
            print(f"SendDcmTab.load_data -> _mgr.load_data returned | rows={model.rowCount()}")

        if model.rowCount() == 0:
            self._status_info("Нет данных для отображения")
            return

        print("SendDcmTab.load_data -> calling setSourceModel...")
        self.table.proxy_model.setSourceModel(model)
        print("SendDcmTab.load_data -> setSourceModel OK")

        print("SendDcmTab.load_data -> calling apply_column_config...")
        self.table.apply_column_config()
        print("SendDcmTab.load_data -> apply_column_config OK")

        self.model = model
        print("SendDcmTab.load_data -> COMPLETE")
        print("SendDcmTab.load_data -> _mgr.close() COMPLETE")
        self._status_info(f"Загружено строк: {model.rowCount()}")

    def _build_controls(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите дату (ДД.ММ.ГГГГ)")
        self.search_input.setFixedWidth(200)
        search_btn = QPushButton("Поиск")
        upload_btn = QPushButton("Выгрузить в Excel")
        save_btn = QPushButton("Сохранить изменения")

        search_btn.clicked.connect(self.load_data)
        upload_btn.clicked.connect(self.upload_excel)
        save_btn.clicked.connect(self.save_changes)
        layout.addWidget(self.search_input)
        layout.addWidget(search_btn)
        layout.addWidget(upload_btn)
        layout.addWidget(save_btn)
        return layout

    def upload_excel(self):
        if not self.model:
            return self._status_warning("Нет данных для экспорта.")
        if ExcelParser.write_excel(self.model._dataframe):
            print("upload_excel - success")
            return self._status_success("Файл успешно сохранен")
        else:
            return self._status_warning("Ошибка сохранения файла")

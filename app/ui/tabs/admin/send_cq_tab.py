from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QLineEdit

from app.core.base_tab import BaseTab
from app.db.dcm_manager import DcmManager
from app.ui.components.searchable_table import AdvancedTableView
from app.excel.excel_manager import ExcelParser
from datetime import datetime


class SendCqTab(BaseTab):
    def __init__(self, main_window=None):
        print("SendCqTab.__init__ -> start")
        super().__init__("Срочные вопросы DCM в отправку", space=0, main_window=main_window)
        print("SendCqTab.__init__ -> super().__init__ done")

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

    def load_data(self, checked=None, force: bool = False):
        columns = [
            "ID", "Date of meeting", "Code of the WD or MD",
            "Description of problem", "Symbols of decisions under the Protocol",
            "Appendix", "Текст решения, дата", "Перевод проверен",
            "Texts of  decisions, date", "Desighner's surname", "Приложение", "В отправку",
            "Дата изменения текста ответа", "Дата отправки Заказчику", "Отправлен Заказчику", "От кого вопрос",
            "Отдел задавший вопрос",
        ]
        print(f"SendCqTab.load_data -> start | force={force}")
        if not force and not self._confirm_unsaved("Обновить данные и потерять изменения"):
            print("TranslateTab.load_data -> data is unsaved and close/refresh")
            return

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
                in_send=True,
                translate=True,
                archive=False,
                in_working=True,
                in_send_customer=False,
                columns=columns,
                dop=' OR ([В архив] = False AND [Вопрос в рабочем порядке] = True '
                    'AND [Дата изменения текста ответа] > [Дата отправки Заказчику] AND [Перевод проверен] = True)'
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
        send_btn = QPushButton('Проставить "Отправлено"')
        save_btn = QPushButton("Сохранить изменения")

        search_input.textChanged.connect(
            lambda text: self.table.proxy_model.setFilterFixedString(text)
        )

        upload_btn.clicked.connect(self.upload_excel)
        refresh_btn.clicked.connect(self.load_data)
        save_btn.clicked.connect(self.save_changes)
        send_btn.clicked.connect(self.send_data)
        layout.addWidget(search_input)
        layout.addWidget(upload_btn)
        layout.addWidget(refresh_btn)
        layout.addWidget(send_btn)
        layout.addWidget(save_btn)
        return layout


    def send_data(self):
        try:
           self._stamp_send_fields()  # Проставляем дату и флаг
        except Exception as e:
           print(e)

    def upload_excel(self):
        if not self.model:
            return self._status_warning("Нет данных для экспорта.")
        if ExcelParser.write_excel(self.model._dataframe):
            print("upload_excel - success")
            return self.status_bar.show_warning("Файл успешно сохранен")
        else:
            return self._status_warning("Ошибка сохранения файла")


    def _stamp_send_fields(self):
        """
        Перед сохранением проставляет во все строки модели:
          - «Отправлен Заказчику» = True
          - «Дата отправки Заказчику» = сегодняшняя дата (datetime)
        чтобы изменения попали в _change_log и ушли в БД.
        """
        if not self.model or not self.table:
            return

        current_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        # Находим индексы колонок
        df = self.model._dataframe
        columns = df.columns.tolist()

        try:
            col_sent_idx = columns.index("Отправлен Заказчику")
            col_date_idx = columns.index("Дата отправки Заказчику")
        except ValueError as e:
            print(f"Не найдена нужная колонка: {e}")
            return

        # Проходим по всем строкам и обновляем через setData
        for row in range(self.model.rowCount()):
            # Обновляем флаг "Отправлен Заказчику" (checkbox)
            sent_index = self.model.index(row, col_sent_idx)
            self.model.setData(
                sent_index,
                Qt.CheckState.Checked.value,  # True = Checked
                Qt.ItemDataRole.CheckStateRole
            )

            # Обновляем дату отправки
            date_index = self.model.index(row, col_date_idx)
            self.model.setData(
                date_index,
                current_date,
                Qt.ItemDataRole.EditRole
            )
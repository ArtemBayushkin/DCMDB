from PyQt6.QtWidgets import QPushButton, QLineEdit, QGridLayout, QLabel

from app.core.base_tab import BaseTab
from app.db.dcm_manager import DcmManager
from app.ui.components.pandas_model import PandasModel
from app.ui.components.searchable_table import AdvancedTableView
from app.excel.excel_manager import ExcelParser


class ArchiveTab(BaseTab):
    def __init__(self, main_window=None):
        print("ArchiveTab.__init__ -> start")
        super().__init__("Архив DCM", space=0, main_window=main_window)
        print("ArchiveTab.__init__ -> super().__init__ done")

    def add_content(self):
        print("ArchiveTab.add_content -> start")
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        print("ArchiveTab.add_content -> try to add _build_controls")
        self.layout.addLayout(self._build_controls())
        print("ArchiveTab.add_content -> controls added")
        self.table = AdvancedTableView()
        print("ArchiveTab.add_content -> AdvancedTableView created")
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        print("ArchiveTab.add_content -> layout set, calling load_data...")
        #self.load_data()
        print("ArchiveTab.add_content -> load_data returned OK")

    def _build_controls(self) -> QGridLayout:
        layout = QGridLayout()

        data_label = QLabel("Date of meeting")
        self.data_line = QLineEdit()
        self.data_line.setPlaceholderText("ДД.ММ.ГГГГ-ДД.ММ.ГГГГ")

        id_label = QLabel("ID")
        self.id_line = QLineEdit()
        self.id_line.setPlaceholderText("Поиск по номеру вопроса")

        question_label = QLabel("Description of problem")
        self.question_line = QLineEdit()
        self.question_line.setPlaceholderText("Поиск по тексту вопроса")

        answer_label = QLabel("Texts of  decisions, date")
        self.answer_line = QLineEdit()
        self.answer_line.setPlaceholderText("Поиск по тексту ответа (англ)")

        spec_label = QLabel("Текст решения, дата")
        self.spec_line = QLineEdit()
        self.spec_line.setPlaceholderText("Поиск по тексту ответа (рус)")

        designer_label = QLabel("Desighner's surname")
        self.designer_line = QLineEdit()
        self.designer_line.setPlaceholderText("Поиск по фамилии сотрудника")

        doc_label = QLabel("Code of the WD or MD")
        self.doc_line = QLineEdit()
        self.doc_line.setPlaceholderText("Поиск по коду документа")

        print("ArchiveTab._build_controls -> data success, next button...")
        search_btn = QPushButton("Поиск")
        print("Create button success, then create connect")
        search_btn.clicked.connect(self.load_data)
        excel_bt = QPushButton("Выгрузить в Excel")
        excel_bt.clicked.connect(self.upload_excel)

        layout.addWidget(data_label, 0, 0)
        layout.addWidget(self.data_line, 0, 1)
        layout.addWidget(id_label, 1, 0)
        layout.addWidget(self.id_line, 1, 1)
        layout.addWidget(question_label, 2, 0)
        layout.addWidget(self.question_line, 2, 1)
        layout.addWidget(doc_label, 3, 0)
        layout.addWidget(self.doc_line, 3, 1)
        layout.addWidget(answer_label, 0, 3)
        layout.addWidget(self.answer_line, 0, 4)
        layout.addWidget(spec_label, 1, 3)
        layout.addWidget(self.spec_line, 1, 4)
        layout.addWidget(designer_label, 2, 3)
        layout.addWidget(self.designer_line, 2, 4)
        layout.addWidget(search_btn, 3, 3)
        layout.addWidget(excel_bt, 3, 4)

        return layout

    def load_data(self, force=None):
        if not self.settings.get_main_db_path():
            self.status_bar.show_warning("База данных не настроена. Перейдите в Настройки для подключения БД.")
            return

        self.table.proxy_model.setSourceModel(None)
        self.model = None
        print("ArchiveTab.load_data -> start _mgr.load_data")

        spisok = self.on_button_clicked()
        conditions = []

        for key, value in spisok.items():
            if not value:
                continue

            # Специальная обработка для поля с датой
            if key == "[Date of meeting]":
                date_condition = self._build_date_condition(value)
                if date_condition:
                    conditions.append(date_condition)
                else:
                    # Если не дата, ищем как обычный текст
                    conditions.append(f"{key} LIKE '%{value}%'")
            else:
                # Обычный поиск по LIKE для всех остальных полей
                conditions.append(f"{key} LIKE '%{value}%'")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = "SELECT [Date of meeting], [ID], [Code of the WD or MD], [Description of problem], " \
                "[Symbols of decisions under the Protocol], [Texts of  decisions, date], [Текст решения, дата], " \
                f"[Desighner's surname], [Appendix], [Приложение], [Заметка] FROM DCM WHERE [В отправку] = Yes " \
                f"AND {where_clause} "
        query += "ORDER BY [Date of meeting]"

        print(query)
        with DcmManager() as mgr:
            model = PandasModel(mgr._fetch_df(query, []))
        if model.rowCount() == 0:
            self._status_info("Нет данных для отображения")
            return
        self.table.proxy_model.setSourceModel(model)
        self.table.apply_column_config()
        self.model = model
        self._status_info(f"Загружено строк: {model.rowCount()}")

    def _convert_to_access_date(self, date_str: str) -> str:
        """
        Преобразует дату из формата ДД.ММ.ГГГГ в формат Access #ММ/ДД/ГГГГ#
        Пример: "05.05.2025" -> "#05/05/2025#"
        """
        try:
            day, month, year = date_str.split('.')
            print("_convert_to_access_date отработала")
            return f"#{year}/{month}/{day}#"
        except (ValueError, AttributeError):
            return date_str

    def _build_date_condition(self, date_string: str) -> str:
        """
        Строит условие для поиска по дате в формате Access.
        Поддерживает форматы:
        - "14.04.2026" - точная дата
        - "14.04.2026-15.05.2026" - диапазон
        - "14.04.2026 - 15.05.2026" - диапазон с пробелами
        """
        date_string = date_string.strip()

        # Проверяем на диапазон с разделителями
        for separator in ['-', '—']:
            if separator in date_string:
                parts = date_string.split(separator)
                if len(parts) == 2:
                    start_date = parts[0].strip()
                    end_date = parts[1].strip()

                    if self._is_valid_date_format(start_date) and self._is_valid_date_format(end_date):
                        start_access = self._convert_to_access_date(start_date)
                        end_access = self._convert_to_access_date(end_date)
                        return f"[Date of meeting] BETWEEN {start_access} AND {end_access}"
                break

        # Если не диапазон, проверяем на одиночную дату
        if self._is_valid_date_format(date_string):
            access_date = self._convert_to_access_date(date_string)
            return f"[Date of meeting] = {access_date}"

        return None  # Не удалось распарсить как дату

    def _is_valid_date_format(self, date_str: str) -> bool:
        """Проверяет, соответствует ли строка формату ДД.ММ.ГГГГ"""
        import re
        pattern = r'^\d{2}\.\d{2}\.\d{4}$'
        if not re.match(pattern, date_str):
            return False

        try:
            day, month, year = map(int, date_str.split('.'))
            if month < 1 or month > 12:
                return False
            if day < 1 or day > 31:
                return False
            if month in [4, 6, 9, 11] and day > 30:
                return False
            if month == 2:
                is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
                if day > (29 if is_leap else 28):
                    return False
            return True
        except ValueError:
            return False

    def on_button_clicked(self):
        dict_ = {
            "[Date of meeting]": self.data_line.text(),
            "[ID]": self.id_line.text(),
            "[Description of problem]": self.question_line.text(),
            "[Texts of  decisions, date]": self.answer_line.text(),
            "[Текст решения, дата]": self.spec_line.text(),
            "[Desighner's surname]": self.designer_line.text(),
            "[Code of the WD or MD]": self.doc_line.text(),
        }
        return dict_

    def _confirm_unsaved(self, action: str = "продолжить"):
        return True

    def upload_excel(self):
        if not self.model:
            return self._status_warning("Нет данных для экспорта.")
        if ExcelParser.write_excel(self.model._dataframe):
            print("upload_excel - success")
            return self.status_bar.show_warning("Файл успешно сохранен")
        else:
            return self._status_warning("Ошибка сохранения файла")
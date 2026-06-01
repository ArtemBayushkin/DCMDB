from urllib.parse import unquote
from pathlib import Path

from PyQt6.QtWidgets import QTableView, QHeaderView, QAbstractItemView, QMessageBox, QApplication
from PyQt6.QtCore import Qt, QSortFilterProxyModel, QModelIndex, QUrl
from PyQt6.QtGui import QDesktopServices

from app.config.settings_manager import settings
from app.ui.components.combo_delegate import (CheckBoxDelegate, HyperlinkDelegate,
                                              ComboBoxDelegate, MultilineTextDelegate)




class AdvancedTableView(QTableView):
    def __init__(self, parent=None):
        self._combo_delegates: dict[int, ComboBoxDelegate] = {}
        super().__init__(parent)
        self.setSortingEnabled(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(True)
        self.setWordWrap(True)

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked |
                             QAbstractItemView.EditTrigger.EditKeyPressed)

        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setDynamicSortFilter(False)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)
        self.setModel(self.proxy_model)

        self._checkbox_delegate = CheckBoxDelegate(self)
        self._hyperlink_delegate = HyperlinkDelegate(self)
        self._multiline_delegate = MultilineTextDelegate(self)

        self.horizontalHeader().sectionClicked.connect(self._handle_header_click)
        self.clicked.connect(self._on_cell_clicked)

    # ──────────────────────────────────────────────────────────────
    # Настройка ширины столбцов, высоты строк и делегатов
    # ──────────────────────────────────────────────────────────────

    def apply_column_config(
        self,
        column_widths: dict[str, int] | None = None,
        min_width: int = 5,
        row_height: int = 70,
        combo_choices: dict[str, list[str]] | None = None,
    ) -> None:
        """
        Применяет начальную конфигурацию ширины столбцов, высоты строк
        и автоматически назначает делегаты для checkbox/hyperlink колонок.

        Вызывать ПОСЛЕ установки модели через proxy_model.setSourceModel().

        :param combo_choices: Словарь {название столбца: [выпадающий список элементов]}.
        :param column_widths: Словарь {название_столбца: ширина_в_пикселях}.
                              Столбцы без явной настройки получат min_width.
        :param min_width: Ширина по умолчанию для столбцов не из словаря.
        :param row_height: Высота каждой строки в пикселях.

        Пример:
            self.table.proxy_model.setSourceModel(model)
            self.table.apply_column_config(
                column_widths={
                    "ID": 50,
                    "Description of problem": 300,
                },
                row_height=28,
            )
        """
        if column_widths is None:
            column_widths = {
                            'ID': 100,
                            'Date of meeting': 100,
                            'Code of the WD or MD': 250,
                            'Description of problem': 550,
                            'Symbols of decisions under the Protocol': 60,
                            'Texts of  decisions, date': 200,
                            "Desighner's surname": 150,
                            'От кого вопрос': 100,
                            'Отдел задавший вопрос': 40,
                            'Urgent/Срочный': 100,
                            'Appendix': 200,
                            'Приложение': 200,
                            'Текст решения, дата': 200,
                            'Заметка': 200,
                            'В отправку': 70,
                            'Отправлен Заказчику': 150,
                            'Дата отправки Заказчику': 175,
                            'Требуется уточнение': 150,
                            'Аннулирован': 30,
                            'Документ': 30,
                            'Дата аннулирования': 50,
                            'Соисполнитель': 100,
                            'Код': 10,
                            'Дата изменения текста ответа': 210,
                            'В архив': 50,
                            'Вопрос в рабочем порядке': 30,
                            'Перевод проверен': 120,
                            'В списке комплектов поставки Поставщика': 30,
                            'Ответ забрали': 100,
                            'Дата забора ответа': 50,
                            'Обязательство выполнено': 30,
                            'Телефон': 60,
                            'ФИО': 250,
                            'Специальность': 150,
                            'Код специальности': 150,
                            'Перечень систем по всем зданиям': 150,
                            'Перечень зданий': 150
                            }
        if combo_choices is None:
            combo_choices = {
                "Symbols of decisions under the Protocol": ["", "CA", "CD(C)", "CD(S)", "CN", "CR", "Rev", "Protocol"]}
        source_model = self.proxy_model.sourceModel()
        if source_model is None:
            return

        column_widths = column_widths or {}

        for col_idx in range(source_model.columnCount()):
            col_name = source_model._dataframe.columns[col_idx]
            ctype = source_model.column_types.get(col_name, "text")

            width = column_widths.get(col_name, min_width)
            self.setColumnWidth(col_idx, width)

            if ctype == "checkbox":
                self.setItemDelegateForColumn(col_idx, self._checkbox_delegate)
            elif ctype == "hyperlink":
                self.setItemDelegateForColumn(col_idx, self._hyperlink_delegate)
            elif ctype == "combo" or col_name in combo_choices:
                choices = combo_choices.get(col_name, [])
                delegate = ComboBoxDelegate(choices, self)
                self._combo_delegates[col_idx] = delegate
                self.setItemDelegateForColumn(col_idx, delegate)
            elif ctype == "text":
                self.setItemDelegateForColumn(col_idx, self._multiline_delegate)

        self.verticalHeader().setDefaultSectionSize(row_height)

    # ──────────────────────────────────────────────────────────────
    # Сортировка
    # ──────────────────────────────────────────────────────────────

    def _handle_header_click(self, logical_index: int):
        order = self.horizontalHeader().sortIndicatorOrder()
        source_model = self.proxy_model.sourceModel()
        if source_model and hasattr(source_model, 'sort'):
            source_model.sort(logical_index, order)
            self.proxy_model.invalidate()
            self.horizontalHeader().setSortIndicator(logical_index, order)

    # ──────────────────────────────────────────────────────────────
    # Обработка кликов по гиперссылкам
    # ──────────────────────────────────────────────────────────────

    def _on_cell_clicked(self, index: QModelIndex):
        if not index.isValid():
            return

        source_index = self.proxy_model.mapToSource(index)
        source_model = self.proxy_model.sourceModel()
        if source_model is None:
            return

        col_name = source_model._dataframe.columns[source_index.column()]
        ctype = source_model.column_types.get(col_name, "text")

        if ctype == "combo":
            self.edit(index)
            return
        if ctype != "hyperlink":
            return

        raw_url = source_index.data(Qt.ItemDataRole.UserRole)
        if not raw_url or not isinstance(raw_url, str):
            return

        url_str = raw_url.strip().strip('#')

        if url_str.startswith("file:///"):
            url_str = url_str[8:]

        url_str = unquote(url_str).replace('\\', '/')
        path = Path(url_str)

        if path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(url_str))
        else:
            QMessageBox.warning(
                self,
                "Файл не найден",
                "Файл перемещён, удалён или путь записан некорректно."
            )

    def keyPressEvent(self, event):
        """Обработка клавиш: копирование выделенных данных при Ctrl+C и Ctrl+Shift+C"""
        if event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Обычное копирование
            include_headers = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
            self.copy_selection_to_clipboard(include_headers=include_headers)
        else:
            super().keyPressEvent(event)

    def copy_selection_to_clipboard(self, include_headers: bool = False):
        """Копирует выделенные ячейки в буфер обмена

        :param include_headers: Если True, всегда добавляет заголовки столбцов
        """
        if not self.selectionModel().hasSelection():
            return

        selected_indexes = self.selectionModel().selectedIndexes()
        if not selected_indexes:
            return

        source_model = self.proxy_model.sourceModel()
        if source_model is None:
            return

        # Сортируем индексы по строкам и столбцам
        selected_indexes.sort(key=lambda idx: (idx.row(), idx.column()))

        # Определяем диапазон строк и столбцов
        rows = sorted(set(idx.row() for idx in selected_indexes))
        cols = sorted(set(idx.column() for idx in selected_indexes))

        # Получаем общее количество строк в модели
        total_rows = source_model.rowCount()

        # Решаем, добавлять ли заголовки
        add_headers = include_headers or (len(rows) == total_rows and len(rows) > 1)

        # Создаем словарь для быстрого доступа к данным
        data = {}
        for idx in selected_indexes:
            row = idx.row()
            col = idx.column()
            value = idx.data(Qt.ItemDataRole.DisplayRole) or ""
            data[(row, col)] = str(value)

        rows_data = []

        # Добавляем заголовки столбцов, если нужно
        if add_headers:
            headers = []
            for col in cols:
                col_name = source_model._dataframe.columns[col]
                headers.append(col_name)
            rows_data.append('\t'.join(headers))

        # Формируем данные строк
        for row in rows:
            row_data = []
            for col in cols:
                value = data.get((row, col), "")
                # Экранируем табуляции и переносы строк для корректного копирования
                value = value.replace('\t', ' ').replace('\r\n', ' ').replace('\n', ' ')
                row_data.append(value)
            rows_data.append('\t'.join(row_data))

        clipboard_text = '\n'.join(rows_data)

        # Копируем в буфер обмена
        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_text)

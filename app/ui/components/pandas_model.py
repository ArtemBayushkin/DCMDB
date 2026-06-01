from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt6.QtGui import QColor
import pandas as pd
from app.config.settings_manager import settings
from app.core.current_user import CurrentUser


class PandasModel(QAbstractTableModel):
    def __init__(self, dataframe: pd.DataFrame, column_types: dict = None, parent=None):
        print(f"PandasModel.__init__ -> start | shape={dataframe.shape}")
        super().__init__(parent)
        print("PandasModel.__init__ -> super().__init__ OK")
        self._dataframe = dataframe.copy()
        print("PandasModel.__init__ -> _dataframe.copy() OK")
        self._original = dataframe.copy()
        print("PandasModel.__init__ -> _original.copy() OK")
        self._change_log: dict = {}
        print("PandasModel.__init__ -> _change_log OK")
        is_admin = CurrentUser().is_admin
        self._editable_columns = set(settings.get_editable_columns(admin=is_admin))

        print("PandasModel.__init__ -> assigning column_types...")
        self.column_types = column_types or {
            "Перевод проверен": "checkbox",
            "Urgent/Срочный": "checkbox",
            "В отправку": "checkbox",
            "Отправлен Заказчику": "checkbox",
            "Требуется уточнение": "checkbox",
            "В архив": "checkbox",
            "Вопрос в рабочем порядке": "checkbox",
            "Ответ забрали": "checkbox",
            "Обязательство выполнено": "checkbox",
            "Appendix": "hyperlink",
            "Приложение": "hyperlink",
            "Date of meeting": "date_short",
            "Дата отправки Заказчику": "date_short",
            "Дата аннулирования": "date_short",
            "Дата изменения текста ответа": "date_short",
            "Symbols of decisions under the Protocol": "combo",
            "Код": "pk"
        }
        print(f"PandasModel.__init__ -> column_types OK | {len(self.column_types)} types defined")

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._dataframe)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._dataframe.columns)

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return str(self._dataframe.columns[section])
        if orientation == Qt.Orientation.Vertical:
            return str(section + 1)
        return None

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        col_name = self._dataframe.columns[index.column()]
        value = self._dataframe.iloc[index.row(), index.column()]
        ctype = self.column_types.get(col_name, "text")

        if role == Qt.ItemDataRole.BackgroundRole:
            row_color = self.get_row_color(index.row())
            if row_color:
                return row_color
            return None

        if pd.isna(value):
            return "" if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole) else None

        if ctype == "checkbox":
            if role == Qt.ItemDataRole.CheckStateRole:
                return Qt.CheckState.Checked if value else Qt.CheckState.Unchecked
            return None

        if ctype == "date_short" and role == Qt.ItemDataRole.DisplayRole:
            return value.strftime("%d.%m.%Y") if hasattr(value, "strftime") else str(value)

        if ctype == "hyperlink":
            if role == Qt.ItemDataRole.DisplayRole:
                return str(value)
            if role == Qt.ItemDataRole.UserRole:
                return str(value)
            if role == Qt.ItemDataRole.ForegroundRole:
                return QColor("#0066cc")
        if ctype == "pk":
            pass

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return str(value)

        return None

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        col_name = self._dataframe.columns[index.column()]
        ctype = self.column_types.get(col_name, "text")

        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

        can_edit = col_name in self._editable_columns

        if ctype == "checkbox" and can_edit:
            flags |= Qt.ItemFlag.ItemIsUserCheckable
        elif ctype in ("text", "date_short", "combo") and can_edit:
            flags |= Qt.ItemFlag.ItemIsEditable

        return flags

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False

        row = index.row()
        col_name = self._dataframe.columns[index.column()]
        ctype = self.column_types.get(col_name, "text")

        if ctype == "checkbox" and role == Qt.ItemDataRole.CheckStateRole:
            bool_value = bool(value == Qt.CheckState.Checked.value)
            self._dataframe.iloc[row, index.column()] = bool_value
            self._log_change(row, col_name, bool_value)
            self.dataChanged.emit(index, index)
            return True

        if role == Qt.ItemDataRole.EditRole:
            self._dataframe.iloc[row, index.column()] = value
            self._log_change(row, col_name, value)
            self.dataChanged.emit(index, index)
            return True

        return False

    def _log_change(self, row: int, col_name: str, value) -> None:
        """Записывает изменение в лог. Вызывается только из setData."""
        if row not in self._change_log:
            self._change_log[row] = {}
        self._change_log[row][col_name] = self._to_python(value)

    def sort(self, column: int, order: Qt.SortOrder):
        if column < 0 or column >= len(self._dataframe.columns):
            return
        col_name = self._dataframe.columns[column]
        self.layoutAboutToBeChanged.emit()
        self._dataframe = self._dataframe.sort_values(
            by=col_name,
            ascending=(order == Qt.SortOrder.AscendingOrder),
            na_position="last"
        ).reset_index(drop=True)
        self.layoutChanged.emit()

    def get_changes(self) -> list[dict]:
        """
        Возвращает список изменений для DcmManager.bulk_update().

        :return: [{"id": int, "columns": [...], "values": [...]}, ...]
        """

        print("PandasModel.get_changes -> start")
        if not self._change_log:
            print("PandasModel.get_changes -> _change_log is None")
            return []

        if "Код" not in self._dataframe.columns:
            print("get_changes: нет колонки Код, отслеживание невозможно")
            return []

        changes = []
        for row_idx, col_changes in self._change_log.items():
            print(f"PandasModel.get_changes -> row_idx: {row_idx}, col_changes: {col_changes}")
            if row_idx >= len(self._dataframe) or not col_changes:
                print("PandasModel.get_changes -> row_idx >= len(self._dataframe)")
                continue
            row_pk = self._dataframe.loc[row_idx, "Код"]
            print("row_idx - row_idx =", row_idx)
            print("row_pk - row_pk =", row_pk)
            changes.append({
                "id": row_pk,
                "columns": list(col_changes.keys()),
                "values": list(col_changes.values()),
            })

            print(f"get_changes: row_idx={row_idx}, id={row_pk!r}, cols={list(col_changes.keys())}")

        print(f"get_changes: найдено изменений в {len(changes)} строках")
        return changes

    def has_changes(self) -> bool:
        """Быстрая проверка — есть ли несохранённые изменения."""
        return bool(self._change_log)

    def reset_change_log(self) -> None:
        """Сбрасывает лог изменений после успешного сохранения."""
        self._change_log.clear()

    @staticmethod
    def _to_python(value):
        """
        Конвертирует numpy-типы в чистые Python-типы.
        pyodbc не умеет работать с numpy.bool_, numpy.int64 и т.д.
        """
        if isinstance(value, bool):
            return value
        # numpy.bool_ → bool (проверяем через имя типа, чтобы не импортировать numpy)
        type_name = type(value).__name__
        if type_name == 'bool_':
            return bool(value)
        if type_name in ('int64', 'int32', 'int16', 'int8'):
            return int(value)
        if type_name in ('float64', 'float32'):
            return float(value)
        return value

    def get_row_color(self, row: int) -> QColor | None:
        """
        Определяет цвет строки на основе данных.
        Возвращает QColor или None для стандартного цвета.
        """
        # Проверяем колонку "В отправку"
        if "В отправку" in self._dataframe.columns:
            in_send = self._dataframe.iloc[row][self._dataframe.columns.get_loc("В отправку")]
            if in_send:
                return QColor(200, 230, 200)  # Светло-зеленый

        # Проверяем колонку "Требуется уточнение"
        if "Требуется уточнение" in self._dataframe.columns:
            need_clarification = self._dataframe.iloc[row][self._dataframe.columns.get_loc("Требуется уточнение")]
            if need_clarification:
                return QColor(255, 255, 200)  # Светло-желтый

        return None  # Стандартный цвет

    def insert_data(self, col1_name, col2_name, value1, value2):
        self._dataframe[col1_name] = value1
        self._dataframe[col2_name] = value2
        return self._dataframe


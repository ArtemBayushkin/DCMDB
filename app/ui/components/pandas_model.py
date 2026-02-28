from typing import List, Dict, Any

from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt6.QtGui import QColor
import pandas as pd


class PandasModel(QAbstractTableModel):
    """Модель для отображения pandas DataFrame в QTableView"""

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        super().__init__(parent)
        self._dataframe = dataframe
        self.date_columns = ["Date of meeting", "Дата отправки Заказчику",
                             "Дата аннулирования", "Дата изменения текста ответа"]
        self.bool_columns = ["Urgent/Срочный", "В отправку",
                             "Отправлен Заказчику", "Требуется уточнение",
                             "В архив", "Вопрос в рабочем порядке",
                             "Перевод проверен", "В списке комплектов поставки Поставщика",
                             "Ответ забрали", "Дата забора ответа", "Обязательство выполнено"]

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._dataframe)

    def columnCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._dataframe.columns)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        value = self._dataframe.iloc[index.row(), index.column()]

        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            # Преобразуем в строку, но можно кастомизировать
            if pd.isna(value):
                return ""
            if isinstance(value, (int, float)):
                return str(value)  # или форматировать числа
            return str(value)

        # Можно добавить условное форматирование
        # if role == Qt.ItemDataRole.BackgroundRole:
        #     if index.column() == 3 and value == "Уволен":
        #         return QColor(255, 220, 220)  # светло-красный

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return str(self._dataframe.columns[section])

        if orientation == Qt.Orientation.Vertical:
            return str(self._dataframe.index[section])  # или можно просто номера строк

        return None

    def flags(self, index: QModelIndex):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable  # пока только просмотр

    @staticmethod
    def moke():
        return pd.DataFrame(columns=["Нет данных"])

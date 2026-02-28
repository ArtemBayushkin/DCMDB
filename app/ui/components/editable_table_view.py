from typing import List, Dict, Any
from PyQt6.QtCore import Qt, QModelIndex
import pandas as pd
from app.ui.components.pandas_model import PandasModel


class EditablePandasModel(PandasModel):
    """Расширенная модель для редактирования (наследует от PandasModel).
    Добавляет setData, editable flags и get_changes для отложенного сохранения.
    """
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        super().__init__(dataframe, parent)
        self._original = dataframe.copy()  # Для трекинга изменений

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False

        col_name = self._dataframe.columns[index.column()]

        if role == Qt.ItemDataRole.EditRole:
            # Для дат: парсим строку обратно в datetime
            if col_name in self.date_columns:
                try:
                    value = pd.to_datetime(value, format='%d.%m.%Y')
                except ValueError:
                    return False  # Если неверный формат, не сохраняем
            self._dataframe.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True

        elif role == Qt.ItemDataRole.CheckStateRole and col_name in self.bool_columns:
            self._dataframe.iloc[index.row(), index.column()] = (value == Qt.CheckState.Checked.value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index: QModelIndex):
        base_flags = super().flags(index)
        col_name = self._dataframe.columns[index.column()]
        if col_name in self.bool_columns:
            return base_flags | Qt.ItemFlag.ItemIsUserCheckable
        return base_flags | Qt.ItemFlag.ItemIsEditable

    def get_changes(self) -> List[Dict[str, Any]]:
        """Возвращает список изменений для bulk_update в DcmManager.
        Только изменённые поля, с ID как ключом.
        """
        changes = []
        for i in range(len(self._dataframe)):
            changed_cols = []
            values = []
            for col in self._dataframe.columns:
                current = self._dataframe.iloc[i][col]
                original = self._original.iloc[i][col]
                if pd.notna(current) and (pd.isna(original) or current != original):
                    changed_cols.append(col)
                    values.append(current)

            if changed_cols and "ID" in self._dataframe.columns:
                changes.append({
                    "id": int(self._dataframe.iloc[i]["ID"]),
                    "columns": changed_cols,
                    "values": values
                })
        return changes

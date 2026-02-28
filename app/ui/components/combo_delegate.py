from typing import List

from PyQt6.QtWidgets import QItemDelegate, QComboBox
from PyQt6.QtCore import Qt


class ComboBoxDelegate(QItemDelegate):
    """Делегат для отображения/редактирования как QComboBox."""

    def __init__(self, options: List[str], parent=None):
        super().__init__(parent)
        self.options = options  # Список возможных значений

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.options)
        return editor

    def setEditorData(self, editor: QComboBox, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        editor.setCurrentText(str(value))

    def setModelData(self, editor: QComboBox, model, index):
        model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
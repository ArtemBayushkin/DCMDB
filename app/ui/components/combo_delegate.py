# app/ui/components/delegates.py
from PyQt6.QtWidgets import QStyledItemDelegate, QMessageBox, QStyleOptionButton, QStyle, QApplication, QTextEdit
from PyQt6.QtCore import Qt, QEvent, QUrl, QRect
from PyQt6.QtGui import QDesktopServices, QColor
from pathlib import Path


class CheckBoxDelegate(QStyledItemDelegate):
    """
    Делегат для булевых колонок.
    Рисует чекбокс по центру ячейки и обрабатывает клики.
    Текстовый редактор не открывается никогда.
    """

    def paint(self, painter, option, index):
        value = index.data(Qt.ItemDataRole.CheckStateRole)
        if value is None:
            super().paint(painter, option, index)
            return

        # Рисуем фон (выделение, зебра и т.д.) стандартным способом
        self.initStyleOption(option, index)
        option.text = ""            # убираем текст
        option.checkState = value   # передаём состояние чекбокса

        style = option.widget.style() if option.widget else QApplication.style()

        # Считаем размер чекбокса и центрируем его в ячейке
        cb_rect = style.subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, option, option.widget)
        x = option.rect.x() + (option.rect.width() - cb_rect.width()) // 2
        y = option.rect.y() + (option.rect.height() - cb_rect.height()) // 2

        cb_option = QStyleOptionButton()
        cb_option.rect = QRect(x, y, cb_rect.width(), cb_rect.height())
        cb_option.state = option.state

        if value == Qt.CheckState.Checked:
            cb_option.state |= QStyle.StateFlag.State_On
        else:
            cb_option.state |= QStyle.StateFlag.State_Off

        # Рисуем фон строки
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)
        # Рисуем чекбокс
        style.drawControl(QStyle.ControlElement.CE_CheckBox, cb_option, painter, option.widget)

    def editorEvent(self, event, model, option, index):
        """Переключаем чекбокс по клику или Space."""
        if not (index.flags() & Qt.ItemFlag.ItemIsUserCheckable):
            return False

        if event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
            current = index.data(Qt.ItemDataRole.CheckStateRole)
            new_state = Qt.CheckState.Unchecked if current == Qt.CheckState.Checked else Qt.CheckState.Checked
            return model.setData(index, new_state.value, Qt.ItemDataRole.CheckStateRole)

        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Space:
            current = index.data(Qt.ItemDataRole.CheckStateRole)
            new_state = Qt.CheckState.Unchecked if current == Qt.CheckState.Checked else Qt.CheckState.Checked
            return model.setData(index, new_state.value, Qt.ItemDataRole.CheckStateRole)

        return False

    def createEditor(self, parent, option, index):
        # Никогда не открываем текстовый редактор
        return None


class HyperlinkDelegate(QStyledItemDelegate):
    """Кликабельные гиперссылки + обработка несуществующих файлов."""

    def paint(self, painter, option, index):
        url = index.data(Qt.ItemDataRole.UserRole)
        if url:
            painter.save()
            font = painter.font()
            font.setUnderline(True)
            #painter.setFont(font)
            painter.setPen(QColor("#0066cc"))
            painter.drawText(
                option.rect,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                str(url)
            )
            painter.restore()
        else:
            super().paint(painter, option, index)

    def editorEvent(self, event, model, option, index):
        if (event.type() == QEvent.Type.MouseButtonRelease and
                event.button() == Qt.MouseButton.LeftButton):

            url_str = index.data(Qt.ItemDataRole.UserRole)
            if not url_str:
                return False

            path = Path(url_str)

            if path.is_absolute() or str(path).startswith(("/", "C:", "D:", "E:")):
                if path.exists():
                    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
                else:
                    QMessageBox.warning(
                        None,
                        "Файл не найден",
                        f"Путь не существует:\n{url_str}\n\n"
                        "Проверьте, что файл не был перемещён или удалён."
                    )
                return True

            elif str(url_str).startswith(("http://", "https://")):
                QDesktopServices.openUrl(QUrl(url_str))
                return True

            else:
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
                return True

        return super().editorEvent(event, model, option, index)


class ComboBoxDelegate(QStyledItemDelegate):
    """Делегат с выпадающим списком для столбцов с фиксированным набором значений"""

    def __init__(self, choices: list[str], parent=None):
        super().__init__(parent)
        self.choices = choices

    def createEditor(self, parent, option, index):
        from PyQt6.QtWidgets import QComboBox
        combo = QComboBox(parent)
        combo.addItems(self.choices)
        return combo

    def setEditorData(self, editor, index):
        value = index.data(Qt.ItemDataRole.EditRole) or ""
        idx = editor.findText(value)
        if idx >= 0:
            editor.setCurrentIndex(idx)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, rect):
        editor.setGeometry(option.rect)


class MultilineTextDelegate(QStyledItemDelegate):
    """Делегат для редактирования многострочного текста"""

    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QTextEdit(parent)
        editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        editor.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        if value is not None:
            editor.setPlainText(str(value))

    def setModelData(self, editor, model, index):
        value = editor.toPlainText()
        model.setData(index, value, Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

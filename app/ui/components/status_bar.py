"""
Статус-бар PyQt6.
Предоставляет класс StatusBar с методами для отображения временных
сообщений различных уровней (информация, успех, предупреждение, ошибка)
с иконками, а также статические методы для показа стандартных диалоговых окон.
"""

from typing import Optional\

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QStatusBar,
    QLabel,
    QWidget,
    QMessageBox,
    QStyle,
    QApplication,
)


class StatusBar(QStatusBar):
    """
    Расширенная версия QStatusBar с поддержкой временных сообщений,
    иконок для разных уровней событий и удобными методами для вызова диалогов.
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        display_duration: int = 5000,
        icon_size: int = 16,
    ) -> None:
        """
        Инициализация расширенного статус-бара.

        Args:
            parent: Родительский виджет.
            display_duration: Время отображения временных сообщений в мс (0 = бесконечно).
            icon_size: Размер иконки в пикселях.
        """
        super().__init__(parent)
        self._display_duration = display_duration
        self._icon_size = icon_size

        # Таймер для автоматического скрытия временного сообщения
        self._message_timer = QTimer(self)
        self._message_timer.setSingleShot(True)
        self._message_timer.timeout.connect(self._clear_temporary_message)

        # Виджет, который сейчас отображается как временное сообщение
        self._temporary_widget: Optional[QLabel] = None

        # Устанавливаем политику размера, чтобы статус-бар не схлопывался
        self.setSizeGripEnabled(True)

    # ----------------------------------------------------------------------
    # Публичные методы для отображения сообщений в статус-баре
    # ----------------------------------------------------------------------

    def show_info(self, text: str, duration: Optional[int] = None) -> None:
        """
        Показать информационное сообщение с иконкой.
        """
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
        self._show_temporary_message(text, icon, duration)

    def show_success(self, text: str, duration: Optional[int] = None) -> None:
        """
        Показать сообщение об успешном выполнении с иконкой.
        """
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        self._show_temporary_message(text, icon, duration)

    def show_plain_message(self, text: str, duration: Optional[int] = None) -> None:
        """
        Показать обычное текстовое сообщение без иконки (использует встроенный метод).
        """
        self._clear_temporary_message()
        self.showMessage(text, duration or self._display_duration)
        if (duration or self._display_duration) > 0:
            self._message_timer.start(duration or self._display_duration)

    def clear_temporary(self) -> None:
        """Принудительно очистить текущее временное сообщение."""
        self._clear_temporary_message()

    # ----------------------------------------------------------------------
    # Статические методы для вызова стандартных диалоговых окон
    # ----------------------------------------------------------------------

    @staticmethod
    def warning_dialog(
        parent: Optional[QWidget],
        message: str,
        title: str = "Внимание",
        buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
    ) -> QMessageBox.StandardButton:
        """
        Показать модальное диалоговое окно с предупреждением.
        Возвращает нажатую кнопку.
        """
        return QMessageBox.warning(parent, title, message, buttons)

    @staticmethod
    def error_dialog(
        parent: Optional[QWidget],
        message: str,
        title: str = "Ошибка",
        buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
    ) -> QMessageBox.StandardButton:
        """
        Показать модальное диалоговое окно с ошибкой.
        Возвращает нажатую кнопку.
        """
        return QMessageBox.critical(parent, title, message, buttons)

    @staticmethod
    def info_dialog(
        parent: Optional[QWidget],
        message: str,
        title: str = "Информация",
        buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
    ) -> QMessageBox.StandardButton:
        """
        Показать модальное информационное диалоговое окно.
        Возвращает нажатую кнопку.
        """
        return QMessageBox.information(parent, title, message, buttons)

    @staticmethod
    def question_dialog(
        parent: Optional[QWidget],
        title: str,
        message: str,
        buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        default_button: QMessageBox.StandardButton = QMessageBox.StandardButton.No,
    ) -> QMessageBox.StandardButton:
        """
        Показать модальное диалоговое окно с вопросом.
        Возвращает нажатую кнопку.
        """
        return QMessageBox.question(parent, title, message, buttons, default_button)

    # ----------------------------------------------------------------------
    # Приватные вспомогательные методы
    # ----------------------------------------------------------------------
    def show_error(self, message):
        return self.error_dialog(self, message)

    def show_warning(self, message):
        return self.warning_dialog(self, message)

    def _show_temporary_message(
        self, text: str, icon: QIcon, duration: Optional[int] = None
    ) -> None:
        """
        Отображает временное сообщение с иконкой в левой части статус-бара.
        """
        self._clear_temporary_message()

        # Создаём QLabel с иконкой и текстом
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Устанавливаем иконку
        if not icon.isNull():
            pixmap = icon.pixmap(self._icon_size, self._icon_size)
            label.setPixmap(pixmap)

        # Добавляем текст с отступом
        label.setText(f" {text}")

        # Добавляем виджет в статус-бар
        self.addWidget(label)
        self._temporary_widget = label

        # Запускаем таймер автоматического скрытия
        timeout = duration if duration is not None else self._display_duration
        if timeout > 0:
            self._message_timer.start(timeout)

    def _clear_temporary_message(self) -> None:
        """Удаляет временный виджет и останавливает таймер."""
        self._message_timer.stop()

        if self._temporary_widget is not None:
            self.removeWidget(self._temporary_widget)
            self._temporary_widget.deleteLater()
            self._temporary_widget = None

        # Также очищаем встроенное сообщение (на случай, если использовали showMessage)
        self.clearMessage()


# --------------------------------------------------------------------------
# Пример использования модуля
# --------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("EnhancedStatusBar Example")
            self.setGeometry(100, 100, 600, 400)

            # Создаём и устанавливаем наш улучшенный статус-бар
            self.status_bar = StatusBar(self, display_duration=3000, icon_size=20)
            self.setStatusBar(self.status_bar)

            # Центральный виджет с кнопками для демонстрации
            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)

            btn_info = QPushButton("Show Info")
            btn_info.clicked.connect(lambda: self.status_bar.show_info("Информационное сообщение"))
            layout.addWidget(btn_info)

            btn_success = QPushButton("Show Success")
            btn_success.clicked.connect(lambda: self.status_bar.show_success("Операция выполнена успешно"))
            layout.addWidget(btn_success)

            btn_warning = QPushButton("Show Warning")
            btn_warning.clicked.connect(lambda: self.status_bar.show_warning("Это предупреждение"))
            layout.addWidget(btn_warning)

            btn_error = QPushButton("Show Error")
            btn_error.clicked.connect(lambda: self.status_bar.show_error("Произошла ошибка"))
            layout.addWidget(btn_error)

            btn_dialog = QPushButton("Warning Dialog")
            btn_dialog.clicked.connect(
                lambda: self.status_bar.warning_dialog(self, "Диалог", "Текст предупреждения")
            )
            layout.addWidget(btn_dialog)

        def closeEvent(self, event):
            """Пример использования диалога подтверждения при закрытии."""
            reply = self.status_bar.question_dialog(
                self,
                "Подтверждение",
                "Вы действительно хотите выйти?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

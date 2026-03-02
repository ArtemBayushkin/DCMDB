# Абстрактный базовый класс всех вкладок
# core/base_tab.py
from abc import abstractmethod
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.ui.components.status_bar import StatusBar


class BaseTab(QWidget):
    """
    Базовый класс для всех вкладок приложения
    """

    def __init__(self, title: str = "", icon: str = "", space: int = 60, parent=None):
        super().__init__(parent)
        self.title = title
        self.icon = icon
        self.space = space
        self.layout = QVBoxLayout()
        self.init_ui()
        self.setLayout(self.layout)
        self.status_bar = StatusBar(self, display_duration=3000, icon_size=18)

    def init_ui(self):
        """Общий код интерфейса"""
        # Заголовок
        self.layout.addSpacing(self.space)
        title_label = QLabel(f"{self.icon} {self.title}")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title_label)
        self.layout.addSpacing(self.space)

        # Здесь дочерние классы добавляют свой контент
        self.add_content()

    @abstractmethod
    def add_content(self):
        """Здесь реализуется основной контент вкладки"""
        pass

    # def status_message(self, text: str, timeout_ms: int = 4000):
    #     """Удобный способ отправить сообщение в статус-бар главного окна"""
    #     if hasattr(self.window(), 'statusBar'):
    #         self.status_bar.show_plain_message(text, timeout_ms)

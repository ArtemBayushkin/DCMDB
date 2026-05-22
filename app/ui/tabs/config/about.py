# app/ui/tabs/config/about.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QTabWidget, QTextBrowser, QWidget)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap


class AboutDialog(QDialog):
    """
    Диалоговое окно "О программе"
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе")
        self.setModal(True)
        screen = self.screen().availableGeometry()
        width = min(int(screen.width() * 0.7), 800)
        height = min(int(screen.height() * 0.7), 600)
        self.resize(width, height)

        # Устанавливаем минимальный размер
        self.setMinimumSize(400, 350)

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса окна"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # Заголовок с иконкой (можно добавить иконку позже)
        title_layout = QHBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("📋 DCMDB")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title)
        layout.addLayout(title_layout)

        # Версия
        version = QLabel("Версия 2.0.0")
        version.setFont(QFont("Arial", 11))
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: #555;")
        layout.addWidget(version)

        # Дата сборки
        build_date = QLabel("Сборка: май 2026")
        build_date.setFont(QFont("Arial", 9))
        build_date.setAlignment(Qt.AlignmentFlag.AlignCenter)
        build_date.setStyleSheet("color: #888;")
        layout.addWidget(build_date)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # Вкладки с информацией
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
            }
            QTabBar::tab {
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0078d7;
                color: white;
            }
        """)

        # Вкладка "О программе"
        about_tab = self._create_about_tab()
        tab_widget.addTab(about_tab, "📌 О программе")

        # Вкладка "Разработчики"
        dev_tab = self._create_developers_tab()
        tab_widget.addTab(dev_tab, "👨‍💻 Разработчики")

        # Вкладка "Лицензия"
        license_tab = self._create_license_tab()
        tab_widget.addTab(license_tab, "📜 Лицензия")

        layout.addWidget(tab_widget)

        # Кнопка закрытия
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Закрыть")
        close_btn.setMinimumWidth(120)
        close_btn.setMinimumHeight(35)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _create_about_tab(self) -> QWidget:
        """Создает вкладку с основной информацией о программе"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # Описание программы
        description = QLabel(
            "DCMDB — управление рабочими вопросами DCM и срочными вопросами CQ: "
            "отслеживание статуса, перевода, отправки заказчику, архивирования. "
        )
        description.setWordWrap(True)
        description.setFont(QFont("Arial", 10))
        description.setAlignment(Qt.AlignmentFlag.AlignJustify)
        layout.addWidget(description)

        layout.addSpacing(10)

        layout.addStretch()

        return widget

    def _create_developers_tab(self) -> QWidget:
        """Создает вкладку с информацией о разработчиках"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Основной разработчик
        dev1_frame = QFrame()
        dev1_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                background-color: #fafafa;
            }
        """)
        dev1_layout = QVBoxLayout(dev1_frame)

        dev1_name = QLabel("Разработчик")
        dev1_name.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        dev1_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dev1_layout.addWidget(dev1_name)

        dev1_info = QLabel(
            "<b>Артем Баюшкин</b><br>"
            "Архитектура приложения, бэкенд, база данных"
        )
        dev1_info.setWordWrap(True)
        dev1_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dev1_info.setFont(QFont("Arial", 10))
        dev1_layout.addWidget(dev1_info)

        layout.addWidget(dev1_frame)

        layout.addStretch()

        return widget

    def _create_license_tab(self) -> QWidget:
        """Создает вкладку с лицензией"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        license_text = QTextBrowser()
        license_text.setOpenExternalLinks(True)
        license_text.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: #fafafa;
            }
        """)

        license_content = """
        <h3 align="center">ЛИЦЕНЗИОННОЕ СОГЛАШЕНИЕ</h3>

        <p align="center"><b>DCMDB</b><br>
        Версия 2.0.0<br>
        © 2026 DCMDB</p>

        <h4>1. Права на использование</h4>
        <p>Программное обеспечение предоставляется для внутреннего использования в организации.
        Запрещается распространение, копирование или модификация без письменного разрешения разработчиков.</p>

        <h4>2. Ограничение ответственности</h4>
        <p>Разработчики не несут ответственности за любые прямые или косвенные убытки,
        возникшие в результате использования или невозможности использования программного обеспечения.</p>

        <h4>3. Обновления</h4>
        <p>Разработчики оставляют за собой право выпускать обновления, исправлять ошибки
        и изменять функциональность программы без предварительного уведомления.</p>

        <h4>4. Конфиденциальность</h4>
        <p>Все данные, обрабатываемые программой, остаются конфиденциальными и не передаются
        третьим лицам. Программа не собирает и не передает личную информацию пользователей.</p>

        <h4>5. Поддержка</h4>
        <p>Техническая поддержка предоставляется по электронной почте в рабочие дни.</p>

        <hr>
        <p align="center"><font color="#888">Используя данное программное обеспечение, вы соглашаетесь с условиями лицензии.</font></p>
        """

        license_text.setHtml(license_content)
        layout.addWidget(license_text)

        return widget


# Для обратной совместимости с существующим импортом
AboutTab = AboutDialog
from PyQt6.QtWidgets import (
    QPushButton, QLabel, QVBoxLayout, QTableView, QHeaderView, QAbstractItemView, QHBoxLayout, QLineEdit, QGroupBox,
    QFormLayout, QCheckBox, QSpinBox, QWidget, QTabWidget, QComboBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from app.core.base_tab import BaseTab
from app.config.settings_manager import SettingsManager


class SettingsTab(BaseTab):
    def __init__(self, main_window=None):
        super().__init__("Настройки программы", icon="⚙", space=5)
        self.main_window = main_window

    def add_content(self):
        self.tabs = QTabWidget()
        # Вкладка 1: Базы данных
        self.create_database_tab()

        # Вкладка 2: Внешний вид
        self.create_appearance_tab()

        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("💾 Сохранить все настройки")
        self.save_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        #self.save_btn.clicked.connect(self.save_all_settings)
        self.save_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        padding: 8px;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)

        self.apply_btn = QPushButton("🔄 Применить")
        #self.apply_btn.clicked.connect(self.apply_settings)
        self.apply_btn.setEnabled(False)

        self.reset_btn = QPushButton("🔄 Сбросить")
        #self.reset_btn.clicked.connect(self.reset_settings)

        self.test_btn = QPushButton("🧪 Проверить подключения")
        #self.test_btn.clicked.connect(self.test_connections)

        self.layout.addWidget(self.tabs)

    def create_database_tab(self):
        """Создать вкладку настроек баз данных"""
        db_tab = QWidget()
        db_layout = QVBoxLayout(db_tab)

        # Группа: Основная база DCM
        main_db_group = QGroupBox("📊 Основная база DCM")
        main_db_layout = QFormLayout()

        self.db_path_edit = QLineEdit(SettingsManager().get('database.main_path'))
        self.db_path_edit.textChanged.connect(self.on_settings_changed)
        db_browse_btn = QPushButton("Обзор...")
        #db_browse_btn.clicked.connect(lambda: self.browse_file(self.db_path_edit, "Выберите основную базу данных"))

        db_path_layout = QHBoxLayout()
        db_path_layout.addWidget(self.db_path_edit)
        db_path_layout.addWidget(db_browse_btn)
        main_db_layout.addRow("Путь к файлу:", db_path_layout)

        # Статус файла
        self.db_status_label = QLabel()
        main_db_layout.addRow("Статус:", self.db_status_label)

        main_db_group.setLayout(main_db_layout)
        db_layout.addWidget(main_db_group)

        # Группа: База сотрудников
        emp_db_group = QGroupBox("👥 База сотрудников")
        emp_db_layout = QFormLayout()

        self.emp_path_edit = QLineEdit()
        #self.emp_path_edit.textChanged.connect(self.on_settings_changed)
        emp_browse_btn = QPushButton("Обзор...")
        #emp_browse_btn.clicked.connect(lambda: self.browse_file(self.emp_path_edit, "Выберите базу сотрудников"))

        emp_path_layout = QHBoxLayout()
        emp_path_layout.addWidget(self.emp_path_edit)
        emp_path_layout.addWidget(emp_browse_btn)
        emp_db_layout.addRow("Путь к файлу:", emp_path_layout)

        # Статус файла
        self.emp_status_label = QLabel()
        emp_db_layout.addRow("Статус:", self.emp_status_label)

        emp_db_group.setLayout(emp_db_layout)
        db_layout.addWidget(emp_db_group)

        # Группа: Настройки подключения
        conn_group = QGroupBox("🔌 Настройки подключения")
        conn_layout = QFormLayout()

        self.auto_refresh_check = QCheckBox("Автоматическое обновление данных")
        #self.auto_refresh_check.stateChanged.connect(self.on_settings_changed)
        conn_layout.addRow(self.auto_refresh_check)

        self.refresh_interval_spin = QSpinBox()
        self.refresh_interval_spin.setRange(5, 300)
        self.refresh_interval_spin.setSuffix(" сек")
        #self.refresh_interval_spin.valueChanged.connect(self.on_settings_changed)
        conn_layout.addRow("Интервал обновления:", self.refresh_interval_spin)

        conn_group.setLayout(conn_layout)
        db_layout.addWidget(conn_group)

        db_layout.addStretch()
        self.tabs.addTab(db_tab, "📁 Базы данных")

    def create_appearance_tab(self):
        """Создать вкладку настроек внешнего вида"""
        appear_tab = QWidget()
        appear_layout = QVBoxLayout(appear_tab)

        # Группа: Тема
        theme_group = QGroupBox("🎨 Тема интерфейса")
        theme_layout = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Системная", "Светлая", "Темная"])
        #self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addRow("Тема:", self.theme_combo)

        # Предпросмотр тем
        preview_widget = QWidget()
        preview_layout = QHBoxLayout(preview_widget)

        themes_preview = [
            ("💻", "Системная", "Использовать тему операционной системы"),
            ("🔆", "Светлая", "Классическая светлая тема"),
            ("🌙", "Темная", "Темная тема для работы в ночное время")
        ]



        preview_layout.addStretch()
        theme_layout.addRow("Предпросмотр:", preview_widget)

        theme_group.setLayout(theme_layout)
        appear_layout.addWidget(theme_group)

        # Группа: Шрифты и размеры
        font_group = QGroupBox("🔤 Шрифты и размеры")
        font_layout = QFormLayout()

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 20)
        self.font_size_spin.setSuffix(" px")
        #self.font_size_spin.valueChanged.connect(self.on_settings_changed)
        font_layout.addRow("Размер шрифта:", self.font_size_spin)

        self.show_icons_check = QCheckBox("Показывать иконки")
        #self.show_icons_check.stateChanged.connect(self.on_settings_changed)
        font_layout.addRow(self.show_icons_check)

        font_group.setLayout(font_layout)
        appear_layout.addWidget(font_group)

        appear_layout.addStretch()
        self.tabs.addTab(appear_tab, "🎨 Внешний вид")

    def on_settings_changed(self):
        """Обработчик изменения любых настроек"""
        self.apply_btn.setEnabled(True)
        #self.status_label.setText("Есть несохраненные изменения")
        #self.status_label.setStyleSheet("color: orange; font-weight: bold;")




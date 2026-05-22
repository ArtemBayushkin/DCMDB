from pathlib import Path

from PyQt6.QtWidgets import (
    QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QGroupBox,
    QFormLayout, QCheckBox, QSpinBox, QWidget, QTabWidget, QComboBox, QFileDialog, QMessageBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from app.core.base_tab import BaseTab
from app.config.settings_manager import settings


class SettingsTab(BaseTab):
    def __init__(self, main_window=None):
        super().__init__("Настройки программы", icon="⚙", space=5)
        self.main_window = main_window

    def add_content(self):
        self.tabs = QTabWidget()
        self.create_database_tab()
        self.create_appearance_tab()
        self.layout.addWidget(self.tabs)

        self.save_btn = QPushButton("Сохранить настройки")
        self.save_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #aaaaaa; }
        """)
        self.save_btn.clicked.connect(self.save_all_settings)
        self.layout.addWidget(self.save_btn)

    # ── Вкладка: Базы данных ─────────────────────────────────────────────────

    def create_database_tab(self):
        db_tab = QWidget()
        db_layout = QVBoxLayout(db_tab)

        # Основная база DCM
        main_db_group = QGroupBox("Основная база DCM")
        main_db_layout = QFormLayout()

        self.db_path_edit = QLineEdit(settings.get_main_db_path())
        self.db_path_edit.textChanged.connect(self._on_settings_changed)
        self.db_path_edit.textChanged.connect(lambda: self._update_file_status(
            self.db_path_edit, self.db_status_label))

        db_browse_btn = QPushButton("Обзор...")
        db_browse_btn.clicked.connect(lambda: self._browse_file(
            self.db_path_edit, "Выберите основную базу данных"))

        db_path_layout = QHBoxLayout()
        db_path_layout.addWidget(self.db_path_edit)
        db_path_layout.addWidget(db_browse_btn)
        main_db_layout.addRow("Путь к файлу:", db_path_layout)

        self.db_status_label = QLabel()
        main_db_layout.addRow("Статус:", self.db_status_label)

        main_db_group.setLayout(main_db_layout)
        db_layout.addWidget(main_db_group)

        # База сотрудников
        emp_db_group = QGroupBox("База сотрудников")
        emp_db_layout = QFormLayout()

        self.emp_path_edit = QLineEdit(settings.get_employees_db_path())
        self.emp_path_edit.textChanged.connect(self._on_settings_changed)
        self.emp_path_edit.textChanged.connect(lambda: self._update_file_status(
            self.emp_path_edit, self.emp_status_label))

        emp_browse_btn = QPushButton("Обзор...")
        emp_browse_btn.clicked.connect(lambda: self._browse_file(
            self.emp_path_edit, "Выберите базу сотрудников"))

        emp_path_layout = QHBoxLayout()
        emp_path_layout.addWidget(self.emp_path_edit)
        emp_path_layout.addWidget(emp_browse_btn)
        emp_db_layout.addRow("Путь к файлу:", emp_path_layout)

        self.emp_status_label = QLabel()
        emp_db_layout.addRow("Статус:", self.emp_status_label)

        emp_db_group.setLayout(emp_db_layout)
        db_layout.addWidget(emp_db_group)

        db_layout.addStretch()
        self.tabs.addTab(db_tab, "Базы данных")

        # Обновляем статусы при открытии
        self._update_file_status(self.db_path_edit, self.db_status_label)
        self._update_file_status(self.emp_path_edit, self.emp_status_label)

    # ── Вкладка: Внешний вид ─────────────────────────────────────────────────

    def create_appearance_tab(self):
        appear_tab = QWidget()
        appear_layout = QVBoxLayout(appear_tab)

        theme_group = QGroupBox("Тема интерфейса")
        theme_layout = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Системная", "Светлая", "Темная"])
        theme_map = {"system": 0, "light": 1, "dark": 2}
        self.theme_combo.setCurrentIndex(
            theme_map.get(settings.get_theme(), 0))
        self.theme_combo.currentTextChanged.connect(self._on_settings_changed)
        theme_layout.addRow("Тема:", self.theme_combo)

        theme_group.setLayout(theme_layout)
        appear_layout.addWidget(theme_group)

        font_group = QGroupBox("Шрифты и размеры")
        font_layout = QFormLayout()

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 20)
        self.font_size_spin.setSuffix(" px")
        self.font_size_spin.setValue(settings.get_font_size())
        self.font_size_spin.valueChanged.connect(self._on_settings_changed)
        font_layout.addRow("Размер шрифта:", self.font_size_spin)

        font_group.setLayout(font_layout)
        appear_layout.addWidget(font_group)

        appear_layout.addStretch()
        self.tabs.addTab(appear_tab, "Внешний вид")

    # ── Логика ───────────────────────────────────────────────────────────────

    def _browse_file(self, line_edit: QLineEdit, caption: str):
        """Открыть диалог выбора <.accdb> файла и вставить путь в поле."""
        current_path = line_edit.text().strip()
        start_dir = str(Path(current_path).parent) if current_path else ""

        path, _ = QFileDialog.getOpenFileName(
            self,
            caption,
            start_dir,
            "Access Databases (*.accdb *.mdb);;All Files (*)"
        )
        if path:
            line_edit.setText(path)

    def _update_file_status(self, line_edit: QLineEdit, label: QLabel):
        """Обновить метку статуса — существует файл или нет."""
        path = line_edit.text().strip()
        if not path:
            label.setText("Файл не указан")
            label.setStyleSheet("color: blue;")
        elif Path(path).exists():
            label.setText("Файл найден")
            label.setStyleSheet("color: green;")
        else:
            label.setText("Файл не найден")
            label.setStyleSheet("color: red;")

    def _on_settings_changed(self):
        self.save_btn.setEnabled(True)

    def save_all_settings(self):
        """Сохранить все настройки в SettingsManager."""

        db_path = self.db_path_edit.text().strip()
        emp_path = self.emp_path_edit.text().strip()

        # Предупреждение если пути не существуют
        missing = []
        if db_path and not Path(db_path).exists():
            missing.append(f"• Основная база: {db_path}")
        if emp_path and not Path(emp_path).exists():
            missing.append(f"• База сотрудников: {emp_path}")

        if missing:
            reply = QMessageBox.warning(
                self,
                "Файлы не найдены",
                "Следующие файлы не существуют:\n\n" + "\n".join(missing) +
                "\n\nВсё равно сохранить?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        settings.set_main_db_path(db_path)
        settings.set_employees_db_path(emp_path)

        theme_map = {"Системная": "system", "Светлая": "light", "Темная": "dark"}
        settings.set("ui.theme", theme_map.get(self.theme_combo.currentText(), "system"))
        settings.set("ui.font_size", self.font_size_spin.value())

        self.save_btn.setEnabled(False)
        self.status_bar.show_success("Настройки сохранены")

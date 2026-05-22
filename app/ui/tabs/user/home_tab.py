# home.py
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QFont
from app.core.base_tab import BaseTab


class HomeTab(BaseTab):
    def __init__(self, main_window=None):
        self.main_window = main_window
        super().__init__("Главная панель управления", icon="🏠")

    def add_content(self):
        # Все основные DCM в работе
        dcm_button = QPushButton("📋 Все основные DCM в работе")
        dcm_button.setToolTip("Открыть базу с основными DCM в работе")
        dcm_button.setMinimumHeight(60)
        dcm_button.setFont(QFont("Arial", 12))
        dcm_button.clicked.connect(lambda: self.main_window.open_or_switch_tab('dcm'))
        self.layout.addWidget(dcm_button)

        # Все срочные DCM в работе
        cq_button = QPushButton("🚨 Все срочные DCM в работе")
        cq_button.setToolTip("Открыть базу со срочными DCM в работе")
        cq_button.setMinimumHeight(60)
        cq_button.setFont(QFont("Arial", 12))
        cq_button.clicked.connect(lambda: self.main_window.open_or_switch_tab('cq'))
        self.layout.addWidget(cq_button)

        # Все вопросы в работе
        all_dmc_button = QPushButton("📦 Все вопросы в работе")
        all_dmc_button.setToolTip("Открыть все вопросы в работе")
        all_dmc_button.setMinimumHeight(60)
        all_dmc_button.setFont(QFont("Arial", 12))
        all_dmc_button.clicked.connect(lambda: self.main_window.open_or_switch_tab('all_dcm'))
        self.layout.addWidget(all_dmc_button)

        # Архив DCM
        button = QPushButton("📦 Архив DCM")
        button.setToolTip("Открыть вопросы DCM в архиве")
        button.setMinimumHeight(60)
        button.setFont(QFont("Arial", 12))
        button.clicked.connect(lambda: self.main_window.open_or_switch_tab('archive'))
        self.layout.addWidget(button)

        # Добавляем растягивающийся элемент внизу
        self.layout.addStretch()
        self.setLayout(self.layout)

from PyQt6.QtWidgets import QPushButton, QLabel, QGridLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from app.core.base_tab import BaseTab
from app.core.current_user import CurrentUser


class AdminTab(BaseTab):
    def __init__(self, main_window=None):
        self.main_window = main_window
        super().__init__("Панель администрирования", icon="🔧")

    def add_content(self):
        # Переопределение структуры окна с QVBoxLayout на сетку QGridLayout
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Добавление заголовка окна
        title_label = QLabel(f"{self.icon} {self.title}")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.layout.addWidget(title_label, 0, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        dcm_text = QLabel('Вопросы DCM')
        dcm_text.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.layout.addWidget(dcm_text, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        cq_text = QLabel('Срочные вопросы DCM')
        cq_text.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.layout.addWidget(cq_text, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        # Загрузить основные вопросы DCM
        upload_dcm_button = QPushButton("Загрузить основные вопросы DCM")
        upload_dcm_button.setToolTip("Загрузить в базу основные вопросы DCM")
        upload_dcm_button.setMinimumHeight(60)
        upload_dcm_button.setFont(QFont("Arial", 12))
        upload_dcm_button.clicked.connect(lambda: self.connect_admin('dcm_upload'))
        self.layout.addWidget(upload_dcm_button, 2, 0)

        # Вопросы DCM в отправку
        all_dmc_button = QPushButton("Вопросы DCM в отправку")
        all_dmc_button.setToolTip("Выгрузить вопросы DCM, готовые к отправке")
        all_dmc_button.setMinimumHeight(60)
        all_dmc_button.setFont(QFont("Arial", 12))
        all_dmc_button.clicked.connect(lambda: self.main_window.open_or_switch_tab('send_dcm'))
        self.layout.addWidget(all_dmc_button, 3, 0)

        # Вопросы DCM на уточнение
        all_dmc_button = QPushButton("Срочные DCM в архив")
        all_dmc_button.setToolTip("Срочные вопросы DCM для отправки в архив")
        all_dmc_button.setMinimumHeight(60)
        all_dmc_button.setFont(QFont("Arial", 12))
        all_dmc_button.clicked.connect(lambda: self.main_window.open_or_switch_tab("archive_cq"))
        self.layout.addWidget(all_dmc_button, 4, 0)

        # Загрузить срочные вопросы DCM
        upload_cq_button = QPushButton("Загрузить срочные вопросы DCM")
        upload_cq_button.setToolTip("Загрузить в базу срочные вопросы DCM (CQ)")
        upload_cq_button.setMinimumHeight(60)
        upload_cq_button.setFont(QFont("Arial", 12))
        upload_cq_button.clicked.connect(lambda: self.connect_admin('cq_upload'))
        self.layout.addWidget(upload_cq_button, 2, 1)

        # Срочные вопросы DCM в отправку
        button = QPushButton("Срочные вопросы DCM в отправку")
        button.setToolTip("Выгрузить срочные вопросы DCM, готовые к отправке")
        button.setMinimumHeight(60)
        button.setFont(QFont("Arial", 12))
        button.clicked.connect(lambda: self.connect_admin("send_cq"))
        self.layout.addWidget(button, 3, 1)

        # Срочные вопросы DCM в отправку
        button = QPushButton("Срочные вопросы DCM на уточнении")
        button.setToolTip("Выгрузить срочные вопросы DCM, необходимые для уточнения")
        button.setMinimumHeight(60)
        button.setFont(QFont("Arial", 12))
        button.clicked.connect(lambda: self.main_window.open_or_switch_tab("cq_clar"))
        self.layout.addWidget(button, 4, 1)

        # Проверка перевода
        translate_button = QPushButton("Проверка перевода")
        translate_button.setToolTip("Открыть строки с непроверенными переводами ответов")
        translate_button.setMinimumHeight(60)
        translate_button.setFont(QFont("Arial", 12))
        translate_button.clicked.connect(lambda: self.main_window.open_or_switch_tab('translate')
                                         if CurrentUser().is_admin else
                                         self.status_bar.show_warning("Эта функция доступна только администраторам"))
        self.layout.addWidget(translate_button, 5, 0, 1, 2)

        # Информационное сообщение для админки
        info_label = QLabel("⚠️ Внимание: Эти функции доступны только администраторам системы")
        info_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        info_label.setStyleSheet(
            "background-color: #FFF3CD; color: #856404; padding: 15px; border: 3px solid #FFEEBA; border-radius: 10px;")
        self.layout.addWidget(info_label, 6, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)

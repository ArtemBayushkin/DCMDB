from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QLineEdit

from app.core.base_tab import BaseTab
from app.db.dcm_manager import DcmManager
from app.ui.components.searchable_table import AdvancedTableView


class DcmTab(BaseTab):
    def __init__(self, main_window=None):
        self._last_checked = False
        super().__init__("Все основные DCM в работе", icon="📊", space=0, main_window=main_window)

    def add_content(self):
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.layout.addLayout(self.ctrl_layout())
        self.table = AdvancedTableView()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        self.load_data(checked=False)

    def load_data(self, checked=None, force: bool = False):
        designer = self.main_window.current_user.surname_eng

        if not force and not self._confirm_unsaved("Обновить данные и потерять изменения"):
            return
        if checked is None:
            checked = self._last_checked
        else:
            self._last_checked = checked
        if checked is True:
            print("checked -> TRUE")
            in_send = None
            need_clar = None
        else:
            print("checked -> FALSE")
            in_send = False
            need_clar = False
        print("checked is already, next state...")

        self.table.proxy_model.setSourceModel(None)
        self.model = None

        if self._mgr is None:
            self._mgr = DcmManager()
        with self._mgr as mgr:
            model = mgr.load_data(
                designer=designer,
                limit=100,
                need_clarification=need_clar,
                archive=False,
                in_working=False,
                in_send=in_send,
                columns=[
                    "Desighner's surname",
                    "Date of meeting",
                    "ID",
                    "От кого вопрос",
                    "Code of the WD or MD",
                    "Description of problem",
                    "Appendix",
                    "Symbols of decisions under the Protocol",
                    "Текст решения, дата",
                    "Texts of  decisions, date",
                    "Приложение",
                    "Заметка",
                    "Требуется уточнение",
                    "В отправку"
                    ]
                )

        if model.rowCount() == 0:
            self._status_info("Нет данных для отображения")
            return

        self.table.proxy_model.setSourceModel(model)
        self.table.apply_column_config(row_height=50)
        self.model = model
        self._status_info(f"Загружено строк: {model.rowCount()}")

    def ctrl_layout(self):
        controls_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Поиск по тексту...")
        search_button = QPushButton("Показать вопросы в отправку и на уточнении")
        search_button.setCheckable(True)
        search_button.setStyleSheet("QPushButton:checked { background-color: lightgreen; }")
        search_button.clicked.connect(self.load_data)
        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.load_data)
        save_button = QPushButton("Сохранить изменения")
        save_button.clicked.connect(self.save_changes)

        search_input.textChanged.connect(
            lambda text: self.table.proxy_model.setFilterFixedString(text)
        )

        controls_layout.addWidget(search_input)
        controls_layout.addWidget(search_button)
        controls_layout.addWidget(refresh_button)
        controls_layout.addWidget(save_button)

        print(f"Controls layout has {controls_layout.count()} widgets")
        return controls_layout

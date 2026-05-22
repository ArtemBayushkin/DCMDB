from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QLineEdit

from app.core.base_tab import BaseTab
from app.db.dcm_manager import DcmManager
from app.ui.components.searchable_table import AdvancedTableView


class TranslateTab(BaseTab):
    def __init__(self, main_window=None):
        print("TranslateTab.__init__ -> start")
        super().__init__("Проверка перевода", space=0, main_window=main_window)
        print("TranslateTab.__init__ -> super().__init__ done")

    def add_content(self):
        print("TranslateTab.add_content -> start")
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.layout.addLayout(self._build_controls())
        print("TranslateTab.add_content -> controls added")
        self.table = AdvancedTableView()
        print("TranslateTab.add_content -> AdvancedTableView created")
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        print("TranslateTab.add_content -> layout set, calling load_data...")
        self.load_data()
        print("TranslateTab.add_content -> load_data returned OK")

    def load_data(self, force: bool = False):
        columns = [
            "Перевод проверен", "ID", "Date of meeting", "Code of the WD or MD",
            "Description of problem", "Appendix", "Текст решения, дата",
            "Texts of  decisions, date", "Desighner's surname", "Приложение", "Заметка"
        ]
        print(f"TranslateTab.load_data -> start | force={force}")
        if not force and not self._confirm_unsaved("Обновить данные и потерять изменения"):
            print("TranslateTab.load_data -> data is unsaved and close/refresh")
            return

        print("TranslateTab.load_data -> clearing old model...")
        self.table.proxy_model.setSourceModel(None)
        self.model = None
        print("TranslateTab.load_data -> clearing old model success")

        print("TranslateTab.load_data -> calling DcmManager...")
        with DcmManager() as mgr:
            print("TranslateTab.load_data -> calling mgr.load_data...")
            model = mgr.load_data(
                limit=500,
                need_clarification=False,
                in_send=True,
                translate=False,
                archive=False,
                columns=columns,
            )
            print(f"TranslateTab.load_data -> _mgr.load_data returned | rows={model.rowCount()}")

        if model.rowCount() == 0:
            self._status_info("Нет данных для отображения")
            return

        print("TranslateTab.load_data -> calling setSourceModel...")
        self.table.proxy_model.setSourceModel(model)
        print("TranslateTab.load_data -> setSourceModel OK")

        print("TranslateTab.load_data -> calling apply_column_config...")
        self.table.apply_column_config(row_height=70)
        print("TranslateTab.load_data -> apply_column_config OK")

        self.model = model
        print("TranslateTab.load_data -> COMPLETE")
        print("TranslateTab.load_data -> _mgr.close() COMPLETE")
        self._status_info(f"Загружено строк: {model.rowCount()}")

    def save_changes(self):
        print("TranslateTab.save_changes -> start")
        if self.model is None:
            self._status_info("Нет активной модели — обновите вкладку")
            return

        print("TranslateTab.save_changes -> calling DcmManager...")
        with DcmManager() as mgr:
            print("TranslateTab.save_changes -> calling mgr.save_changes...")
            success, count = mgr.save_changes(self.model)
        print(f"TranslateTab.save_changes -> result: success={success}, count={count}")

        if success and count == 0:
            self._status_info("Нет изменений для сохранения")
        elif success:
            self._status_success(f"Сохранено: {count} строк")
            self.load_data(force=True)
        else:
            self._status_error("Ошибка при сохранении — проверьте консоль")

    def has_unsaved_changes(self) -> bool:
        return self.model is not None and self.model.has_changes()

    def _build_controls(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Поиск по тексту...")
        search_btn = QPushButton("Поиск")
        refresh_btn = QPushButton("Обновить")
        save_btn = QPushButton("Сохранить изменения")
        search_btn.clicked.connect(self.load_data)
        refresh_btn.clicked.connect(self.load_data)
        save_btn.clicked.connect(self.save_changes)

        search_input.textChanged.connect(
            lambda text: self.table.proxy_model.setFilterFixedString(text)
        )

        layout.addWidget(search_input)
        layout.addWidget(search_btn)
        layout.addWidget(refresh_btn)
        layout.addWidget(save_btn)
        return layout

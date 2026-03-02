# team_tab.py
from PyQt6.QtWidgets import (
    QPushButton, QLabel, QVBoxLayout, QTableView, QHeaderView, QAbstractItemView
)
import pandas as pd
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from app.core.base_tab import BaseTab
from app.db.employee_manager import EmployeeDatabaseManager
from app.ui.components.pandas_model import PandasModel   # ← подключаем модель
from app.ui.components.status_bar import StatusBar


class TeamTab(BaseTab):
    def __init__(self, main_window=None):
        super().__init__("Список сотрудников", icon="👥")
        self.main_window = main_window
        #self.status_bar = StatusBar(self, display_duration=3000, icon_size=18)

    def add_content(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Заголовок (опционально)
        title = QLabel(f"{self.icon} {self.title}")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Таблица
        self.table = QTableView()
        self.table.setAlternatingRowColors(True)          # зеброобразные строки
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.verticalHeader().selectedIndexes()

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setProperty("copyEnabled", True)

        self.load_data()

        main_layout.addWidget(self.table)

        # Кнопки (пример)
        #btn_refresh = QPushButton("Обновить список")
        #btn_refresh.clicked.connect(self.refresh_data)
        #main_layout.addWidget(btn_refresh)

        # Можно добавить поиск, фильтры и т.д. позже
        self.setLayout(main_layout)

    def load_data(self):
        # Загружаем данные
        with EmployeeDatabaseManager() as mgr:
            df = mgr.get_all_employees()

        # Опционально: отбираем только нужные колонки и красиво переименовываем
        if not df.empty:
            # Пример: выбираем только важные поля и даём заголовки
            display_columns = {
                "ФИО": "ФИО",
                "Телефон": "Телефон",
                "Специальность": "Специальность",
                "Код_специальности": "Код специальности",
                "Перечень_систем_по_всем_зданиям": "Перечень систем по всем зданиям",
                "Перечень_зданий": "Перечень зданий",
                # добавь другие нужные поля
            }
            if set(display_columns.keys()).issubset(df.columns):
                df_display = df[list(display_columns.keys())].rename(columns=display_columns)
            else:
                df_display = df  # fallback — все колонки

            model = PandasModel(df_display)
            self.table.setModel(model)
        else:
            # Пустая таблица или сообщение
            #self.table.setModel(PandasModel(pd.DataFrame(columns=["Нет данных"])))
            StatusBar.warning_dialog(self, message=f"База данных сотрудников не подключена. "
                                                   f"Перейдите в Сервис -> Настройки для добавления базы")

    def refresh_data(self):
        """Обновление данных по кнопке"""
        #with EmployeeDatabaseManager() as mgr:
        #    df = mgr.get_all_employees()
            # здесь та же логика, что выше
        #if not df.empty:
        #    display_columns = {
        #        "ФИО": "ФИО",
        #        "Учетка": "Учётная запись",
        #        "Admin": "Админ",
        #    }
        #    df_display = df[list(display_columns.keys())].rename(columns=display_columns)
        #    model = PandasModel(df_display)
        #    self.table.setModel(model)
        #else:
        #    self.table.setModel(PandasModel(pd.DataFrame(columns=["Нет данных"])))


def main():
    from PyQt6.QtWidgets import QApplication
    import sys
    from app.ui.main_window import AdvancedMainWindow
    # current_user уже полностью готов, connect выполнен в "чистом" окружении
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    AdvancedMainWindow.open_or_switch_tab(key='team')
    window = TeamTab()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

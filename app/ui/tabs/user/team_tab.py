from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QTableView, QHeaderView, QAbstractItemView  # , QPushButton
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from app.core.base_tab import BaseTab
from app.db.employee_manager import EmployeeDatabaseManager
from app.ui.components.pandas_model import PandasModel
from app.ui.components.searchable_table import AdvancedTableView
from app.ui.components.status_bar import StatusBar


class TeamTab(BaseTab):
    def __init__(self, main_window=None):
        super().__init__("Список сотрудников", icon="👥")
        self.main_window = main_window

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
        self.table = AdvancedTableView()

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setProperty("copyEnabled", True)

        self.load_data()

        main_layout.addWidget(self.table)

        # Кнопки
        # btn_refresh = QPushButton("Выгрузить список")
        # btn_refresh.clicked.connect(self.export_data)
        # main_layout.addWidget(btn_refresh)

        # Можно добавить поиск, фильтры и т.д. позже
        self.setLayout(main_layout)

    def load_data(self):
        with EmployeeDatabaseManager() as mgr:
            df = mgr.get_all_employees()
        if not df.empty:
            display_columns = {
                "ФИО": "ФИО",
                "Телефон": "Телефон",
                "Специальность": "Специальность",
                "Код_специальности": "Код специальности",
                "Перечень_систем_по_всем_зданиям": "Перечень систем по всем зданиям",
                "Перечень_зданий": "Перечень зданий",
            }
            if set(display_columns.keys()).issubset(df.columns):
                df_display = df[list(display_columns.keys())].rename(columns=display_columns)
            else:
                df_display = df

            model = PandasModel(df_display)
            self.table.proxy_model.setSourceModel(model)
        else:
            StatusBar.warning_dialog(self, message=f"База данных сотрудников не подключена. "
                                                   f"Перейдите в Сервис -> Настройки для добавления базы")


def main():
    from PyQt6.QtWidgets import QApplication
    import sys
    from app.ui.main_window import AdvancedMainWindow
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    AdvancedMainWindow().open_or_switch_tab(key='team')
    window = TeamTab()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

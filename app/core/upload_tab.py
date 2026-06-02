"""
Вкладки загрузки данных из Excel в базу.

Иерархия:
    UploadTab          — базовый класс (общий UI + логика)
    ├── CqUploadTab    — срочные вопросы (CQ / Urgent)
    └── DcmUploadTab   — обычные вопросы (DCM / Regular)

Каждый наследник переопределяет:
    COLUMN_MAP    — маппинг колонок Excel → UPLOAD_COLUMNS
    FIXED_VALUES  — фиксированные значения (например Urgent=True для CQ)
    _SPECIALIST_COL_IDX — индекс колонки с шифром для подбора специалиста
    title / icon  — заголовок вкладки
"""

import pandas as pd
from PyQt6.QtWidgets import QPushButton, QHBoxLayout

from app.core.base_tab import BaseTab
from app.ui.components.searchable_table import AdvancedTableView
from app.db.employee_manager import EmployeeDatabaseManager
from app.excel.excel_manager import (
    ExcelParser,
    CQ_COLUMN_MAP, CQ_FIXED_VALUES,
    DCM_COLUMN_MAP, DCM_FIXED_VALUES,
)
from app.ui.components.pandas_model import PandasModel
from app.db.dcm_manager import DcmManager
from PyQt6.QtWidgets import QMessageBox


# Целевые колонки — порядок соответствует базе данных
UPLOAD_COLUMNS: list[str] = [
    "ID",
    "Date of meeting",
    "Code of the WD or MD",
    "Description of problem",
    "Symbols of decisions under the Protocol",
    "Texts of  decisions, date",
    "Desighner's surname",
    "От кого вопрос",
    "Отдел задавший вопрос",
    "Urgent/Срочный",
    "Вопрос в рабочем порядке",
    "Appendix",
    "Приложение",
    "В отправку",
]


# ──────────────────────────────────────────────────────────────────────────────
# Базовый класс
# ──────────────────────────────────────────────────────────────────────────────

class UploadTab(BaseTab):
    """
    Базовый класс для вкладок загрузки.
    Содержит общий UI (таблица + панель управления) и логику
    загрузки / нормализации / сохранения.

    Наследники ДОЛЖНЫ переопределить:
        COLUMN_MAP           — словарь переименования колонок
        FIXED_VALUES         — фиксированные значения (может быть пустым dict)
        _SPECIALIST_COL_IDX  — индекс колонки шифра для create_multiple_specialists_df
    """

    # ── Переопределяются в наследниках ───────────────────────────────────────
    COLUMN_MAP: dict[str, str] = {}
    FIXED_VALUES: dict[str, object] = {}
    _SPECIALIST_COL_IDX: int = 1        # индекс колонки с шифром документа
    _HYPERLINK_MODE: str | None = None   # "cq" | "dcm" | None — режим формирования гиперссылок
    _CHECK_DUPLICATE_ID: bool = False    # True только для CQ — там ID уникален

    def __init__(self, title: str, icon: str = "📂", main_window=None):
        self.excel = ExcelParser()       # создаём ДО super().__init__,
        self._emp_df = None              # т.к. super вызывает add_content
        self.model = None
        self.table = None
        super().__init__(title, icon=icon, space=0)
        self.main_window = main_window

    def _confirm_unsaved(self, action: str = "продолжить"):
        return True

    # ── UI ───────────────────────────────────────────────────────────────────

    def add_content(self):
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.layout.addLayout(self._ctrl_layout())

        self.table = AdvancedTableView()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        self._init_empty_table()

    def _ctrl_layout(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        load_btn = QPushButton("📂 Выберите файл для загрузки")
        load_btn.setToolTip(
            "Выберите один или несколько Excel-файлов для загрузки вопросов"
        )
        load_btn.clicked.connect(self.load_data)

        add_row_btn = QPushButton("➕ Добавить строку")
        add_row_btn.setToolTip("Добавить пустую строку для ручного ввода")
        add_row_btn.clicked.connect(self._add_empty_row)

        save_btn = QPushButton("💾 Сохранить в базу")
        save_btn.clicked.connect(self.save_changes)

        layout.addWidget(load_btn)
        layout.addWidget(add_row_btn)
        layout.addWidget(save_btn)
        return layout

    # ── Управление таблицей ──────────────────────────────────────────────────

    def _init_empty_table(self):
        """Одна пустая строка для ручного ввода при первом открытии вкладки."""
        df = pd.DataFrame({col: [None] for col in UPLOAD_COLUMNS})
        self._set_model(df)

    def _add_empty_row(self):
        """Добавляет пустую строку в конец таблицы."""
        if self.model is None:
            self._init_empty_table()
            return
        empty = pd.DataFrame({col: [None] for col in self.model._dataframe.columns})
        new_df = pd.concat([self.model._dataframe, empty], ignore_index=True)
        self._set_model(new_df)

    def _set_model(self, df: pd.DataFrame):
        """Устанавливает PandasModel в proxy → table и назначает делегаты."""
        model = PandasModel(df)
        self.table.proxy_model.setSourceModel(model)
        self.table.apply_column_config()   # ← назначает CheckBoxDelegate, HyperlinkDelegate, ComboBoxDelegate
        self.model = model

    # ── Загрузка из Excel ────────────────────────────────────────────────────

    def load_data(self, force=None):
        """
        Полный цикл загрузки:
        1. Диалог выбора Excel-файлов
        2. Диалог выбора папки приложений (Appendix / Приложение)
        3. Чтение Excel (двухстрочный заголовок)
        4. Подбор специалистов
        5. Нормализация колонок под UPLOAD_COLUMNS
        6. Формирование гиперссылок (если папка выбрана)
        7. Отображение в таблице
        """
        # ── 1. Выбор Excel-файлов ───────────────────────────────────────────
        result = self.excel.open_file()
        if not result:
            self.status_bar.show_info("Файлы не выбраны")
            return
        file_list, _ = result

        # ── 2. Выбор папки приложений ────────────────────────────────────────
        folder_path: str | None = None
        if self._HYPERLINK_MODE:
            folder_path = self.excel.open_folder()
            if not folder_path:
                self.status_bar.show_warning(
                    "Папка не выбрана — колонки Appendix и Приложение будут пустыми"
                )

        # ── 3. Чтение Excel ──────────────────────────────────────────────────
        raw_df = self.excel.read_two_row_header_excel(file_list)
        if raw_df.empty:
            self.status_bar.show_warning("Файлы пустые или не удалось прочитать")
            return

        # ── 4. Подбор специалистов ───────────────────────────────────────────
        emp_df = self._get_emp_df()
        if emp_df is None:
            return

        processed_df = self.excel.create_multiple_specialists_df(
            df=raw_df,
            emp=emp_df,
            num=self._SPECIALIST_COL_IDX,
        )

        # ── 5. Нормализация колонок ──────────────────────────────────────────
        result_df = ExcelParser.normalize_dataframe(
            df=processed_df,
            column_map=self.COLUMN_MAP,
            fixed_values=self.FIXED_VALUES,
            target_columns=UPLOAD_COLUMNS,
        )

        # ── 6. Гиперссылки ───────────────────────────────────────────────────
        if folder_path and self._HYPERLINK_MODE:
            result_df = ExcelParser.build_hyperlinks(
                df=result_df,
                folder_path=folder_path,
                mode=self._HYPERLINK_MODE,
            )

        # ── 7. Отображение ───────────────────────────────────────────────────
        self._set_model(result_df)
        self.status_bar.show_success(f"Загружено {len(result_df)} строк")

    def _get_emp_df(self) -> pd.DataFrame | None:
        """Ленивая загрузка сотрудников — один раз за время жизни вкладки."""
        if self._emp_df is None:
            try:
                with EmployeeDatabaseManager() as mgr:
                    self._emp_df = mgr.get_all_employees()
            except Exception as e:
                self.status_bar.show_error(f"Не удалось загрузить базу сотрудников: {e}")
                return None
        return self._emp_df

    # ── Сохранение ───────────────────────────────────────────────────────────

    def save_changes(self):
        """
        Сохраняет текущий DataFrame в таблицу DCM.

        Шаги:
        1. Проверяет наличие данных
        2. Показывает диалог подтверждения с количеством строк
        3. Вызывает DcmManager.bulk_insert
        4. Показывает итог: вставлено / пропущено дублей / ошибка
        """
        if self.model is None or self.model.rowCount() == 0:
            self.status_bar.show_warning("Нет данных для сохранения")
            return

        df = self.model._dataframe

        # Считаем строки с непустым ID
        valid_rows = df[df["ID"].notna() & (df["ID"].astype(str).str.strip() != "")]
        total = len(valid_rows)

        if total == 0:
            self.status_bar.show_warning("Нет строк с заполненным ID")
            return

        # Диалог подтверждения
        reply = QMessageBox.question(
            self,
            "Подтверждение сохранения",
            f"Будет выполнена попытка вставки {total} строк в базу данных.\n\n"
            "Строки с уже существующим ID будут пропущены.\n\n"
            "Продолжить?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            with DcmManager() as mgr:
                success, inserted, skipped = mgr.insert_record(df, check_duplicate_id=self._CHECK_DUPLICATE_ID)
        except Exception as e:
            self.status_bar.show_error(f"Ошибка подключения к базе: {e}")
            return

        if not success:
            self.status_bar.show_error("Ошибка при вставке данных — проверьте консоль")
            return

        # Итоговое сообщение
        msg_parts = [f"Вставлено строк: {inserted}"]
        if skipped:
            skipped_display = ", ".join(str(s) for s in skipped[:10])
            if len(skipped) > 10:
                skipped_display += f" ... и ещё {len(skipped) - 10}"
            msg_parts.append(f"Пропущено дублей ({len(skipped)}): {skipped_display}")
        self.status_bar.show_warning(" | ".join(msg_parts))


# ──────────────────────────────────────────────────────────────────────────────
# Срочные вопросы (CQ / Urgent)
# ──────────────────────────────────────────────────────────────────────────────

class CqUploadTab(UploadTab):
    """
    Вкладка загрузки **срочных** вопросов (CQ).

    Особенности структуры Excel:
    - Двухстрочный заголовок (skiprows=1 уже применён в read_excel)
    - Колонка шифра документа стоит 3-й (индекс 2)
    - Поле «Urgent/Срочный» всегда True — задаётся через FIXED_VALUES
    - Дата вопроса присутствует («Date of meeting»)
    - Китайская колонка «提出人» → «От кого вопрос»
    """

    COLUMN_MAP = CQ_COLUMN_MAP
    FIXED_VALUES = CQ_FIXED_VALUES
    _SPECIALIST_COL_IDX = 2
    _HYPERLINK_MODE = "cq"
    _CHECK_DUPLICATE_ID = True   # CQ-ID уникален — проверяем дубли     # «Code of the working document» — 3-я колонка

    def __init__(self, main_window=None):
        super().__init__(
            title="Загрузка срочных вопросов (CQ)",
            icon="🚨",
            main_window=main_window,
        )


# ──────────────────────────────────────────────────────────────────────────────
# Обычные вопросы (DCM / Regular)
# ──────────────────────────────────────────────────────────────────────────────

class DcmUploadTab(UploadTab):
    """
    Вкладка загрузки обычных вопросов (DCM).

    Особенности структуры Excel:
    - Колонка шифра документа стоит 2-й (индекс 1)
    - Поле «Urgent» берётся из колонки «Whether it is urgent (Yes or No)»
    - Дата вопроса отсутствует — колонка «Date of meeting» будет пустой
    - Китайская колонка «问题提出者» → «От кого вопрос»
    """

    COLUMN_MAP = DCM_COLUMN_MAP
    FIXED_VALUES = DCM_FIXED_VALUES
    _SPECIALIST_COL_IDX = 1
    _HYPERLINK_MODE = "dcm"
    _CHECK_DUPLICATE_ID = False  # DCM-ID повторяется — дубли не проверяем     # «Code of the DDD/MD...» — 2-я колонка

    def __init__(self, main_window=None):
        super().__init__(
            title="Загрузка обычных вопросов (DCM)",
            icon="📥",
            main_window=main_window,
        )

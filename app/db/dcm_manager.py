# app/db/dcm_manager.py
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from PyQt6.QtWidgets import QMessageBox

from app.db.access_manager import AccessManager
from app.ui.components.pandas_model import PandasModel
from datetime import datetime


class DcmManager(AccessManager):
    """Специфичный менеджер для DCM-базы (наследует от AccessManager)."""

    def __init__(self, db_path: str | None = None):
        super().__init__(db_path)

    # ====================== Получение данных ======================

    def _fetch_df(self, query: str, params: list | None = None) -> pd.DataFrame:
        """
        Безопасное чтение через cursor построчно
        """
        print("_fetch_df -> start")
        try:
            conn = self._get_connection()
            print("_fetch_df -> got connection")
            cursor = conn.cursor()
            print("_fetch_df -> got cursor")
            if params:
                print("_fetch_df -> execute start with (query, params)")
                cursor.execute(query, params)
                print("_fetch_df -> execute OK with (query, params)")
            else:
                print("_fetch_df -> execute start with (query)")
                cursor.execute(query)
                print("_fetch_df -> execute OK with (query)")
            columns = [desc[0] for desc in cursor.description]
            print(f"_fetch_df -> columns={columns}")
            time1 = datetime.now()
            rows = []
            while True:
                batch = cursor.fetchmany(100)
                if not batch:
                    break
                for row in batch:
                    clean_row = []
                    for val in row:
                        try:
                            if isinstance(val, str):
                                val.encode('utf-8')
                            clean_row.append(val)
                        except (UnicodeDecodeError, UnicodeEncodeError):
                            print(f"_fetch_df -> битая ячейка пропущена")
                            clean_row.append(None)
                    rows.append(clean_row)
            time2 = datetime.now()
            print(time2)
            print("Время работы fetch составляет", time2 - time1)
            print(f"_fetch_df -> fetchmany loop done | total rows={len(rows)}")
            df = pd.DataFrame.from_records(rows, columns=columns)
            print(f"_fetch_df -> DataFrame created | shape={df.shape}")
            return df
        except Exception as e:
            print(f"_fetch_df error: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    @staticmethod
    def _build_query(
            ids=None, date_of_meeting=None, code_of_the_wd_or_md=None,
            description_of_problem=None, symbols_of_decisions_under_the_protocol=None,
            texts_of_decisions=None, texts_of_decisions_rus=None,
            designer=None, limit=100, columns=None,
            archive=None, is_urgent=None, in_working=None,
            need_clarification=None, in_send=None, in_send_customer=None,
            translate=None, dop=None, order='[Date of meeting]'
    ) -> Tuple[str, list]:
        """
        Основной запрос получения данных.

        :param ids: ID вопроса (CQ или номер DCM)
        :param date_of_meeting: Дата вопроса
        :param code_of_the_wd_or_md: Код документа
        :param description_of_problem: Описание проблемы
        :param symbols_of_decisions_under_the_protocol: Символ решения (CA, CD, CN, CR, Rev, Protocol)
        :param texts_of_decisions: Текст решения на английском
        :param texts_of_decisions_rus: Текст решения на русском
        :param designer: ФИО сотрудника (по умолчанию = текущий пользователь)
        :param limit: ограничение количества строк (TOP N)
        :param columns: если передан список — берём только эти поля
        :param archive: В архиве
        :param is_urgent: только срочные (Urgent/Срочный)
        :param in_working: в рабочем порядке
        :param need_clarification: только те, где Требуется уточнение = True
        :param in_send: В отправку
        :param in_send_customer: Отправлен Заказчику
        :param translate: Перевод проверен

        :return: DataFrame с записями рабочих вопросов, соответствующих критериям фильтрации.
        """
        conditions = []
        params = []

        if ids is not None:
            conditions.append(f"[ID] = {ids}")
        if date_of_meeting is not None:
            conditions.append(f"[Date of meeting] LIKE '%{date_of_meeting}%'")
        if code_of_the_wd_or_md is not None:
            conditions.append(f"[Code of the WD or MD] LIKE '%{code_of_the_wd_or_md}%'")
        if description_of_problem is not None:
            conditions.append(f"[Description of problem] LIKE '%{description_of_problem}%'")
        if symbols_of_decisions_under_the_protocol is not None:
            conditions.append(
                f"[Symbols of decisions under the Protocol] LIKE '%{symbols_of_decisions_under_the_protocol}%'")
        if texts_of_decisions is not None:
            conditions.append(f"[Texts of  decisions, date] LIKE '%{texts_of_decisions}%'")
        if texts_of_decisions_rus is not None:
            conditions.append(f"[Текст решения, дата] LIKE '%{texts_of_decisions_rus}%'")
        if designer is not None:
            conditions.append("[Desighner's surname] LIKE ?")
            params.append(f'%{designer}%')
        if archive is not None:
            conditions.append(f"[В архив] = {archive}")
        if is_urgent is not None:
            conditions.append(f"[Urgent/Срочный] = {is_urgent}")
        if in_working is not None:
            conditions.append(f"[Вопрос в рабочем порядке] = {in_working}")
        if need_clarification is not None:
            conditions.append(f"[Требуется уточнение] = {need_clarification}")
        if in_send is not None:
            conditions.append(f"[В отправку] = {in_send}")
        if in_send_customer is not None:
            conditions.append(f"[Отправлен Заказчику] = {in_send_customer}")
        if translate is not None:
            conditions.append(f"[Перевод проверен] = {translate}")

        select_fields = ", ".join(f"[{c}]" for c in columns) if columns else "*"
        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"SELECT TOP {limit} [Код], {select_fields} FROM [DCM] WHERE {where_clause}"
        if dop:
            query += dop
        query += f" ORDER BY {order}"

        print(query)
        print(params)
        return query, params

    def load_data(self, column_types: dict = None, **kwargs) -> PandasModel:
        """
        Загружает данные и возвращает готовую PandasModel.
        Принимает все те же параметры фильтрации, что и get_data().

        :param column_types: Опциональный словарь типов колонок для PandasModel.
                             Если не передан — используются дефолтные типы модели.
        :param kwargs: Параметры фильтрации (limit, columns, archive, translate и т.д.)
        :return: PandasModel с загруженными данными (может быть пустой).

        Пример использования во вкладке:
            with DcmManager() as mgr:
                self.model = mgr.load_data(limit=100, translate=False, in_send=True)
        """
        print("DcmManager -> load_data -> start")
        query, params = self._build_query(**kwargs)
        self.model = PandasModel(self._fetch_df(query, params or None),
                            column_types=column_types)
        print("DcmManager -> load_data -> end and return model success")
        return self.model

    # ====================== Сохранение изменений ======================

    def save_changes(self, model: PandasModel) -> Tuple[bool, int]:
        """
        Сохраняет изменения из модели в базу данных.

        :param model: PandasModel с отредактированными данными.
        :return: (success: bool, saved_count: int)
                 saved_count = 0 если изменений не было.

        Пример использования во вкладке:
            with DcmManager() as mgr:
                success, count = mgr.save_changes(self.model)
        """
        print("DcmManager.save_changes -> start")
        changes = model.get_changes()
        print(f"DcmManager.save_changes -> changes: {changes}")
        success = self.update_record(changes)
        print(f"DcmManager.save_changes -> success: {success}")
        if success:
            model.reset_change_log()
        return success, len(changes)

    @staticmethod
    def _to_python(value):
        """Конвертирует numpy-типы в нативные Python для pyodbc"""
        if isinstance(value, (np.bool_,)):
            return bool(value)
        if isinstance(value, (np.integer, np.int64,)):
            return int(value)
        if isinstance(value, (np.floating,)):
            return float(value)
        if value is pd.NaT or (isinstance(value, float) and np.isnan(value)):
            return None
        return value

    # ====================== Переопределения базовых методов ======================

    def get_table_data(self, table_name: str = "DCM", limit: int = 1000, where: str = None) -> pd.DataFrame:
        return super().get_table_data(table_name, limit, where)

    def update_record(self, changes: List[Dict[str, Any]], **kwargs) -> bool:
        """
                Применяет список изменений к таблице DCM.

                :param changes: [{"id": int, "columns": [...], "values": [...]}, ...]
                :return: True если всё прошло успешно, False при ошибке.
                """


        if not changes:
            print("DcmManager.save_changes -> changes is None")
            return True

        current_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        try:
            print("DcmManager.update_record -> start")
            conn = self._get_connection()
            cursor = conn.cursor()
            print("update_record - changes:", changes)
            for idx, change in enumerate(changes, 1):
                print("idx =", idx)
                print("change:", change)
                if not change.get("columns"):
                    print(f"DcmManager.update_record: пропуск изменения #{idx}: нет изменённых колонок")
                    continue

                columns = change["columns"].copy()
                values = change["values"].copy()
                if "В отправку" in columns or "Texts of  decisions, date" in columns:
                    columns.append("Дата изменения текста ответа")
                    values.append(current_date)
                    columns.append("Перевод проверен")
                    values.append(False)

                set_parts = []
                for col in columns:
                    if "'" in col:
                        set_parts.append(f'"{col}" = ?')
                    else:
                        set_parts.append(f"[{col}] = ?")
                sql = f"UPDATE [DCM] SET {', '.join(set_parts)} WHERE [Код] = ?"
                params = [self._to_python(v) for v in values] + [self._to_python(change["id"])]

                print(f"DcmManager.update_record #{idx}: {sql} | params: {params}")
                cursor.execute(sql, params)

            QMessageBox.information(None, "Успех", f"Успешно обновлено {len(changes)} строк")
            print(f"DcmManager.update_record: успешно применено {len(changes)} изменений")
            return True

        except Exception as e:
            print(f"DcmManager.update_record -> error: {e}")
            return False

    def insert_record(self,
                      df: pd.DataFrame,
                      check_duplicate_id: bool = False,
                      ) -> tuple[bool, int, list[str]]:
        """
        Вставляет строки DataFrame в таблицу DCM.

        Первичный ключ таблицы — AutoNumber (генерируется Access автоматически),
        поэтому колонка ID из Excel НЕ является ключом БД.

        Имена колонок DataFrame должны совпадать с именами полей в таблице DCM.

        :param df: DataFrame, колонки которого соответствуют полям таблицы DCM.
        :param check_duplicate_id: если True — перед вставкой проверяет,
               нет ли уже строки с таким же значением [Код] в таблице.
               Используется для CQ (срочных вопросов), где ID уникален.
               Для обычных вопросов (DCM) передавайте False —
               там один и тот же номер вопроса может встречаться многократно.
        :return: (success, inserted_count, skipped_ids)
                 success        — True если не было критических ошибок
                 inserted_count — количество реально вставленных строк
                 skipped_ids    — список ID, пропущенных как дубли (только при check_duplicate_id=True)
        """
        if df.empty:
            print("insert_record: DataFrame пустой")
            return True, 0, []

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            db_cols = list(df.columns)
            placeholders = ", ".join(["?"] * len(db_cols))
            col_list = ", ".join(f'"{c}"' for c in db_cols)
            sql = f"INSERT INTO [DCM] ({col_list}) VALUES ({placeholders})"
            print(sql)

            inserted = 0
            skipped = []

            for _, row in df.iterrows():
                id_val = row.get("ID")

                # Строки без ID пропускаем всегда
                if pd.isna(id_val) or str(id_val).strip() == "":
                    print("insert_record: строка без ID — пропускаем")
                    skipped.append("<empty>")
                    continue

                id_str = str(id_val).strip()

                # Проверка дубля — только для CQ
                if check_duplicate_id:
                    cursor.execute(
                        "SELECT COUNT(*) FROM [DCM] WHERE [ID] = ?", (id_str,)
                    )
                    if cursor.fetchone()[0] > 0:
                        print(f"insert_record: ID={id_str!r} уже существует — пропускаем")
                        skipped.append(id_str)
                        continue

                values = [self._to_python(row[col]) for col in db_cols]
                print(f"insert_record: INSERT ID={id_str!r}")
                cursor.execute(sql, values)
                inserted += 1

            conn.commit()
            print(f"insert_record: вставлено={inserted}, пропущено={len(skipped)}")
            return True, inserted, skipped

        except Exception as e:
            print(f"insert_record error: {e}")
            return False, 0, []

    def _df_to_pd(self, df):
        return PandasModel(dataframe=df)

    def insert_send(self, df):
        print("start insert_send")
        current_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        return PandasModel(df).insert_data('Дата отправки Заказчику', 'Отправлен Заказчику', current_date, True)

    def delete_record(self, table_name: str, record_id: Any) -> bool:
        print("delete_record: не поддерживается")
        return False

    def _stamp_send_fields(self):
        """
        Перед сохранением проставляет во все строки модели:
          - «Отправлен Заказчику» = True
          - «Дата отправки Заказчику» = сегодняшняя дата (datetime)
        """
        if not self.model:
            return

        current_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        df = self.model._dataframe

        # Проставляем значения
        df['Отправлен Заказчику'] = True
        df['Дата отправки Заказчику'] = current_date

        # Сигнализируем об обновлении
        top_left = self.model.index(0, 0)
        bottom_right = self.model.index(self.model.rowCount() - 1, self.model.columnCount() - 1)
        self.model.dataChanged.emit(top_left, bottom_right)
# app/db/dcm_manager.py
import pandas as pd
from typing import Dict, Any, List, Optional
from app.db.access_manager import AccessManager
from app.ui.components.status_bar import StatusBar


class DcmManager(AccessManager):
    """Специфичный менеджер для DCM-базы (наследует от AccessManager).
    : фильтры в SQL, bulk-обновления.
    """

    def __init__(self, db_path: str | None = None):
        super().__init__(db_path)  # Вызываем базовый init для connection_string

    # ====================== Оптимизированные методы для DCM ======================

    def get_data(
        self,
        ids: Optional[str] = None,
        date_of_meeting: Optional[str] = None,
        code_of_the_wd_or_md: Optional[str] = None,
        description_of_problem: Optional[str] = None,
        symbols_of_decisions_under_the_protocol: Optional[str] = None,
        texts_of_decisions: Optional[str] = None,
        texts_of_decisions_rus: Optional[str] = None,
        designer: Optional[str] = None,
        limit: int = 100,
        columns: Optional[List[str]] = None,
        archive: bool = None,
        is_urgent: bool = None,
        in_working: bool = None,
        need_clarification: bool = None,
        in_send: bool = None,
        in_send_customer: bool = None,
        translate: bool = None,
    ) -> pd.DataFrame:
        """
        Основной метод получения рабочих вопросов.

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

        :notes:
            - По умолчанию архивные записи (В архив = True) исключаются из выборки
            - Все текстовые фильтры поддерживают поиск по частичному совпадению (LIKE)
            - Параметры со значением None не участвуют в фильтрации
        """

        conditions = []

        if ids is not None:
            conditions.append(f"[ID] = {ids}")

        if date_of_meeting is not None and not "":
            conditions.append(f"[Date of meeting] LIKE '%{date_of_meeting}%'")

        if code_of_the_wd_or_md is not None and not "":
            conditions.append(f"[Code of the WD or MD] LIKE '%{code_of_the_wd_or_md}%'")

        if description_of_problem is not None and not "":
            conditions.append(f"[Description of problem] LIKE '%{description_of_problem}%'")

        if symbols_of_decisions_under_the_protocol is not None and not "":
            conditions.append(f"[Symbols of decisions under the Protocol] LIKE '%{symbols_of_decisions_under_the_protocol}%'")

        if texts_of_decisions is not None and not "":
            conditions.append(f"[Texts of  decisions, date] LIKE '%{texts_of_decisions}%'")

        if texts_of_decisions_rus is not None and not "":
            conditions.append(f"[Текст решения, дата] LIKE '%{texts_of_decisions_rus}%'")

        if designer is not None:
            conditions.append("[Desighner's surname] LIKE ?")
            params = [f'%{designer}%']
        else:
            params = []

        # Какие поля брать
        if columns:
            select_fields = ", ".join(f"[{c}]" for c in columns)
        else:
            select_fields = "*"

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

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
            SELECT TOP {limit} {select_fields}
            FROM [DCM]
            WHERE {where_clause}
        """
            # ORDER BY [Дата изменения текста ответа] DESC, [Дата и время] DESC, [ID] DESC
        print(query)
        try:
            conn = self._get_connection()
            df = pd.read_sql_query(query, conn, params=params)
            return df
        except Exception as e:
            print(f"get_active_for_user error: {e}")
            return pd.DataFrame()

    def bulk_update(self, changes: List[Dict[str, Any]]) -> bool:
        conn = None
        if not changes:
            print("bulk_update: изменений нет")
            return True

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            for idx, change in enumerate(changes, 1):
                if not change.get("columns"):
                    print(f"Пропуск изменения #{idx}: нет изменённых колонок")
                    continue

                set_parts = []
                for col in change["columns"]:
                    if col == "Desighner's surname":
                        set_parts.append("\"Desighner's surname\" = ?")  # двойной апостроф внутри имени
                    else:
                        set_parts.append(f"[{col}] = ?")
                sql = f"UPDATE [DCM] SET {', '.join(set_parts)} WHERE [ID] = ?"
                params = change["values"] + [change["id"]]

                print(f"Изменение #{idx}:")
                print("  SQL  :", sql)
                print("  params:", params)
                print("  ID   :", change["id"])
                print("  поля :", change["columns"])

                cursor.execute(sql, params)

            conn.commit()
            print(f"Успешно применено {len(changes)} изменений")
            StatusBar().show_info("Изменения сохранены успешно!")
            return True

        except Exception as e:
            print("DcmManager.bulk_update error:", e)
            StatusBar().show_error(f'Ошибка вставки данных:, {e}')
            if conn:
                conn.rollback()
            return False

    # ====================== Переопределения базовых методов, если нужно ======================
    # Например, get_table_data можно переопределить для DCM по умолчанию
    def get_table_data(self, table_name: str = "DCM", limit: int = 1000, where: str = None) -> pd.DataFrame:
        return super().get_table_data(table_name, limit, where)  # Или кастомизируй

    # ───────────────────────────────────────────────
    # CRUD-операции (если в будущем понадобится редактировать сотрудников)
    # ───────────────────────────────────────────────

    def update_record(self, table_name: str, record_id: Any, updates: Dict[str, Any]) -> bool:
        # Пока заглушка / можно реализовать позже
        print("Обновление записей в базе пока не поддерживается")
        return False

    def insert_record(self, table_name: str, data: Dict[str, Any]) -> bool:
        print("Добавление записей в базу пока не поддерживается")
        return False

    def delete_record(self, table_name: str, record_id: Any) -> bool:
        print("Удаление записей в базе пока не поддерживается")
        return False

# db/employee_manager.py
import pyodbc
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from app.core.base_db_manager import BaseDatabaseManager
from app.config.settings_manager import settings


class EmployeeDatabaseManager(BaseDatabaseManager):
    """
    Менеджер для базы данных сотрудников (List_of_employees.accdb)

    Основные особенности:
    - Чтение списка сотрудников, администраторов
    - Проверка подключения
    - Поддержка большинства стандартных операций из базового интерфейса
    """

    def __init__(self, db_path: str | Path | None = None):

        if db_path is None:
            db_path = settings.get_employees_db_path()
        self.db_path = Path(db_path).resolve()

        if not self.db_path.exists():
            raise FileNotFoundError(f"EmployeeDatabaseManager -> Файл базы данных не найден: {self.db_path}")
        # print('EmployeeDatabaseManager -> start self.connection_string')
        # print(f'EmployeeDatabaseManager -> Path {self.db_path}')
        self.connection_string = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={self.db_path};'
            r'ReadOnly=0;'  # можно менять на 1, если нужна только чтение
        )
        # print('EmployeeDatabaseManager -> end self.connection_string')
        self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _get_connection(self) -> pyodbc.Connection:
        """Ленивое подключение + проверка живого соединения"""
        print('EmployeeDatabaseManager -> _get_connection -> start')
        if self._conn is None or self._conn.closed:
            try:
                print('EmployeeDatabaseManager -> _get_connection -> start pyodbc.connect')
                self._conn = pyodbc.connect(self.connection_string, autocommit=True)
                print(f"EmployeeDatabaseManager -> _get_connection -> Подключено к базе сотрудников: {self.db_path.name}")
            except pyodbc.Error as e:
                raise ConnectionError(f"EmployeeDatabaseManager -> _get_connection -> Не удалось подключиться к {self.db_path}: {e}")
        return self._conn

    def close(self) -> None:
        """Закрыть соединение явно"""
        if self._conn and not self._conn.closed:
            self._conn.close()
            self._conn = None
            print("EmployeeDatabaseManager -> close -> Соединение с базой сотрудников закрыто")

    # ───────────────────────────────────────────────
    # Реализация абстрактных методов
    # ───────────────────────────────────────────────

    def get_tables(self) -> List[str]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            tables = cursor.tables(tableType='TABLE')
            return [t.table_name for t in tables if t.table_name and not t.table_name.startswith('MSys')]
        except pyodbc.Error as e:
            print(f"EmployeeDatabaseManager -> get_tables -> Ошибка при получении списка таблиц: {e}")
            return []

    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT TOP 1 * FROM [{table_name}]")
            columns = []
            for col in cursor.description:
                columns.append({
                    'name': col[0],
                    'type': str(col[1]).split('.')[-1],  # например <class 'str'> → str
                    'size': col[2] or 0,
                    'nullable': col[6] > 0 if col[6] is not None else True
                })
            return columns
        except pyodbc.Error as e:
            print(f"EmployeeDatabaseManager -> get_table_columns -> Ошибка при получении структуры таблицы {table_name}: {e}")
            return []

    def get_table_data(self, columns: list = None, table_name: str = None, limit: int = 1000,
                       where: str = None) -> pd.DataFrame:
        select_fields = ", ".join(f"[{c}]" for c in columns) if columns else "*"
        query = f"SELECT TOP {limit} {select_fields} FROM [List]"
        if where:
            query += f" WHERE {where}"

        try:
            conn = self._get_connection()
            df = pd.read_sql(query, conn)
            return df
        except Exception as e:
            print(f"EmployeeDatabaseManager -> get_table_data -> Ошибка при чтении таблицы {table_name}: {e}")
            return pd.DataFrame()

    def execute_query(self, query: str, params: list = None) -> pd.DataFrame:
        try:
            conn = self._get_connection()
            if params:
                df = pd.read_sql_query(query, conn, params=params)
            else:
                df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            print(f"EmployeeDatabaseManager -> execute_query ->Ошибка выполнения запроса:\n{query}\n{e}")
            return pd.DataFrame()

    def test_connection(self) -> Tuple[bool, str]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True, "EmployeeDatabaseManager -> test_connection -> Подключение успешно"
        except Exception as e:
            return False, str(e)

    # ───────────────────────────────────────────────
    # Методы, специфичные для базы сотрудников
    # ───────────────────────────────────────────────

    def get_all_employees(self) -> pd.DataFrame:
        """Все сотрудники"""
        return self.get_table_data()  # предполагаемая таблица — List

    def get_admins(self) -> pd.DataFrame:
        """Только администраторы (где Admin = True)"""
        return self.execute_query(
            "SELECT ФИО, Admin FROM [List] WHERE Admin = True"
        )

    def is_admin(self, full_name: str) -> bool:
        """Проверка, является ли человек администратором по ФИО"""
        df = self.execute_query(
            "SELECT Admin FROM [List] WHERE ФИО = ?",
            params=[full_name]
        )
        if df.empty:
            return False
        return bool(df.iloc[0]['Admin'])

    def find_employee(self, windows_login: str) -> Optional[Dict[str, Any]]:
        """Найти сотрудника по Учетной записи windows"""
        df = self.execute_query(
            "SELECT * FROM [List] WHERE Учетка = ?",
            params=[windows_login]
        )
        if df.empty:
            return None
        #print(df.iloc[0].to_dict())
        return df.iloc[0].to_dict()

    # ───────────────────────────────────────────────
    # CRUD-операции (если в будущем понадобится редактировать сотрудников)
    # ───────────────────────────────────────────────

    def update_record(self, table_name: str, record_id: Any, updates: Dict[str, Any]) -> bool:
        # Пока заглушка / можно реализовать позже
        print("Обновление записей в базе сотрудников пока не поддерживается")
        return False

    def insert_record(self, table_name: str, data: Dict[str, Any]) -> bool:
        print("Добавление записей в базу сотрудников пока не поддерживается")
        return False

    def delete_record(self, table_name: str, record_id: Any) -> bool:
        print("Удаление записей в базе сотрудников пока не поддерживается")
        return False


# ───────────────────────────────────────────────
# Пример использования
# ───────────────────────────────────────────────

if __name__ == "__main__":
    from app.core.current_user import CurrentUser
    curr_user = CurrentUser()
    login = curr_user._get_windows_login()
    print(login)
    # Замени на свой реальный путь
    PATH = settings.get_employees_db_path()
    try:
        mgr = EmployeeDatabaseManager()
        success, msg = mgr.test_connection()
        print(f"Тест подключения: {success} → {msg}")

        if success:
            print("\nТаблицы в базе:")
            print(mgr.get_tables())

            print("\nАдминистраторы:")
            admins = mgr.get_admins()
            print(admins[['ФИО', 'Admin']])

            print("\nАртём — администратор?")
            print(mgr.is_admin("Баюшкин Артем Олегович"))  # подставь реальное ФИО

            empl = mgr.find_employee(login)
            print(empl)
            print('UKA' in empl['Перечень_зданий'])
            print('32' in empl['Код_специальности'])

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if 'mgr' in locals():
            mgr.close()

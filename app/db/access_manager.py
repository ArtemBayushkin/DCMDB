# Основной класс для Access (наследует base_db_manager)

import pyodbc
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from app.core.base_db_manager import BaseDatabaseManager
from app.config.settings_manager import SettingsManager


class AccessManager(BaseDatabaseManager):
    """
        Менеджер для базы данных

        Основные особенности:
        - Чтение списка данных из таблицы
        - Проверка подключения
        - Поддержка большинства стандартных операций из базового интерфейса
    """

    def __init__(self, db_path: str | Path | None = None):

        if db_path is None:
            db_path = SettingsManager().get_main_db_path()
        self.db_path = Path(db_path).resolve()

        if not self.db_path.exists():
            raise FileNotFoundError(f"AccessManager -> Файл базы данных не найден: {self.db_path}")
        # print('AccessManager -> start self.connection_string')
        # print(f'AccessManager -> Path {self.db_path}')
        self.connection_string = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={self.db_path};'
            r'ReadOnly=0;'  # можно менять на 1, если нужна только чтение
        )
        # print('AccessManager -> end self.connection_string')
        self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _get_connection(self) -> pyodbc.Connection:
        """Ленивое подключение + проверка живого соединения"""
        # print('AccessManager -> _get_connection -> start')
        if self._conn is None or self._conn.closed:
            try:
                # print('AccessManager -> _get_connection -> start pyodbc.connect')
                self._conn = pyodbc.connect(self.connection_string, autocommit=True)
                # print(f"AccessManager -> _get_connection -> Подключено к базе сотрудников: {self.db_path.name}")
            except pyodbc.Error as e:
                raise ConnectionError(
                    f"AccessManager -> _get_connection -> Не удалось подключиться к {self.db_path}: {e}")
        return self._conn

    def close(self) -> None:
        """Закрыть соединение явно"""
        if self._conn and not self._conn.closed:
            self._conn.close()
            self._conn = None
            print("AccessManager -> close -> Соединение с базой сотрудников закрыто")


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
            print(f"AccessManager -> get_tables -> Ошибка при получении списка таблиц: {e}")
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
            print(
                f"AccessManager -> get_table_columns -> Ошибка при получении структуры таблицы {table_name}: {e}")
            return []

    def get_table_data(self, table_name: str, limit: int = 1000, where: str = None) -> pd.DataFrame:
        query = f"SELECT TOP {limit} * FROM [{table_name}]"
        if where:
            query += f" WHERE {where}"

        try:
            conn = self._get_connection()
            df = pd.read_sql(query, conn)
            return df
        except Exception as e:
            print(f"AccessManager -> get_table_data -> Ошибка при чтении таблицы {table_name}: {e}")
            return pd.DataFrame()

    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        try:
            conn = self._get_connection()
            if params:
                df = pd.read_sql_query(query, conn, params=params)
            else:
                df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            print(f"AccessManager -> execute_query ->Ошибка выполнения запроса:\n{query}\n{e}")
            return pd.DataFrame()

    def test_connection(self) -> Tuple[bool, str]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True, "AccessManager -> test_connection -> Подключение успешно"
        except Exception as e:
            return False, str(e)

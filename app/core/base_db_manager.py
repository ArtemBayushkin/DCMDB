from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pandas as pd


class BaseDatabaseManager(ABC):
    """Абстрактный интерфейс для работы с любой базой данных"""

    @abstractmethod
    def get_tables(self) -> List[str]: pass

    @abstractmethod
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]: pass

    @abstractmethod
    def get_table_data(self, table_name: str, limit: int = 1000, where: str = None) -> pd.DataFrame: pass

    @abstractmethod
    def update_record(self, table_name: str, record_id: Any, updates: Dict[str, Any]) -> bool: pass

    @abstractmethod
    def insert_record(self, table_name: str, data: Dict[str, Any]) -> bool: pass

    @abstractmethod
    def delete_record(self, table_name: str, record_id: Any) -> bool: pass

    @abstractmethod
    def execute_query(self, query: str, params: list = None) -> pd.DataFrame: pass

    @abstractmethod
    def test_connection(self) -> tuple[bool, str]:
        """Возвращает (успех, сообщение)"""
        pass

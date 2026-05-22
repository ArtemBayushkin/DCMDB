# core/current_user.py
import os
import getpass
from typing import Optional, Dict, Any

from app.db.employee_manager import EmployeeDatabaseManager
from app.config.settings_manager import settings


class CurrentUser:
    """
    Единая точка получения и хранения информации о текущем пользователе.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Инициализация всех данных пользователя при первом обращении"""
        self._windows_login = self._get_windows_login()
        self._load_employee_data()

    @staticmethod
    def _get_windows_login() -> str:
        """
        Получает логин текущего пользователя Windows.
        Пробует несколько способов, возвращает 'Unknown' в крайнем случае.
        """
        try:
            return os.getlogin()
        except Exception:
            try:
                return getpass.getuser()
            except Exception:
                print("CurrentUser -> _get_windows_login -> Не удалось определить логин Windows")
                return "Unknown"

    def _load_employee_data(self) -> None:
        """
        Загружает данные сотрудника из базы по логину Windows.
        Заполняет:
        full_name - ФИО на русском
        surname_eng - Фамилия и инициалы для работы в базе
        is_admin - логическая проверка на админа
        employee_data - вся информация о сотруднике из базы
        """
        self._full_name = None
        self._surname_eng = None
        self._is_admin = False
        self._employee_data = None

        try:
            print("CurrentUser -> _load_employee_data → Начинаем загрузку данных сотрудника...")
            db_path = settings.get_employees_db_path()  # или settings.get_employees_path()
            # print(f"CurrentUser -> _load_employee_data → Путь к базе: {db_path}")

            with EmployeeDatabaseManager(db_path) as mgr:
                # print("CurrentUser -> _load_employee_data → Менеджер создан")
                employee = mgr.find_employee(self._windows_login)
                # print("CurrentUser -> _load_employee_data → Запрос find_employee выполнен")

                if employee:
                    self._employee_data = employee
                    self._full_name = employee.get('ФИО', self._windows_login)
                    self._surname_eng = employee.get('Фамилия_англ')
                    self._is_admin = bool(employee.get('Admin', False))
                    print(f"CurrentUser -> _load_employee_data -> Пользователь найден: {self._full_name} | Admin: {self._is_admin}")
                else:
                    print(f"CurrentUser -> _load_employee_data -> Не найден пользователь с логином '{self._windows_login}'")

        except Exception as e:
            import traceback
            print(f"CurrentUser -> _load_employee_data -> Ошибка при загрузке данных пользователя из базы: {e}")
            print(traceback.format_exc())

    # ─── Свойства для доступа ───────────────────────────────────────────────

    @property
    def windows_login(self) -> str:
        return self._windows_login

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def surname_eng(self) -> Optional[str]:
        return self._surname_eng

    @property
    def is_admin(self) -> bool:
        return self._is_admin

    @property
    def employee_data(self) -> Optional[Dict[str, Any]]:
        return self._employee_data


# Глобальный доступ
current_user = CurrentUser()

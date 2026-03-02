# config/settings_manager.py
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


class SettingsManager:
    """
    Singleton-менеджер настроек приложения.
    Хранит только конфигурацию, которая не меняется от запуска к запуску.
    """
    _instance = None
    _settings: Dict[str, Any] = {}
    if getattr(sys, 'frozen', False):
        # Для скомпилированного .exe
        _file_path = Path(sys.executable).parent / "app" / "config" / "app_settings.json"
    else:
        # Для разработки - путь относительно текущего файла
        _file_path = Path(__file__).parent.parent.parent / "app" / "config" / "app_settings.json"

    DEFAULT_SETTINGS = {
        "database": {
            "main_path": "C:/Users/artem/OneDrive/Рабочий стол/python/db_changer/Исходные данные/DCM-ТAES-ARCHIVE.accdb",
            "employees_path": "",
            "editable_columns": {
                "default": ["Статус", "Приоритет", "Комментарий"],
                "admin":   ["Статус", "Приоритет", "Комментарий", "Исполнитель", "Срок_выполнения", "Заметка"],
                "tech":    ["Статус", "Приоритет"]
                },
            "auto_refresh_interval_sec": 60,
        },
        "ui": {
            "theme": "system",          # "system", "light", "dark"
            "font_size": 12,
            "language": "ru",
            "maximized_on_start": True,
        },
        "behavior": {
            "confirm_exit": True,
            "auto_backup_on_close": False,
            "show_status_messages": True,
        },
        "paths": {
            "reports_dir": "reports/",
            "backups_dir": "backups/",
            "logs_dir": "logs/",
        }
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        """Загружает настройки из файла или создаёт дефолтные"""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

        if self._file_path.exists():
            try:
                with open(self._file_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Глубокое слияние с дефолтными
                    self._settings = self._deep_merge(self.DEFAULT_SETTINGS, loaded)
            except Exception as e:
                print(f"SettingsManager -> _load -> Ошибка чтения настроек: {e}. Используются значения по умолчанию.")
                self._settings = self.DEFAULT_SETTINGS.copy()
        else:
            self._settings = self.DEFAULT_SETTINGS.copy()
            self._save()

    def _deep_merge(self, default: Dict, loaded: Dict) -> Dict:
        """Глубокое слияние словарей (защищает от потери вложенных настроек)"""
        merged = default.copy()
        for key, value in loaded.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    def _save(self):
        """Сохраняет текущие настройки в файл"""
        try:
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

    # ─── Удобные геттеры (самые частые) ─────────────────────────────────────

    def get_main_db_path(self) -> str:
        # print('SettingsManager -> get_main_db_path -> вызов функции')
        return self._settings["database"]["main_path"]

    def get_employees_db_path(self) -> str:
        # print('SettingsManager -> get_employees_db_path -> вызов функции')
        return self._settings["database"]["employees_path"]

    def get_editable_columns(self) -> List[str]:
        return self._settings["database"]["editable_columns"]

    def get_theme(self) -> str:
        return self._settings["ui"]["theme"]

    def get_font_size(self) -> int:
        return self._settings["ui"]["font_size"]

    def is_maximized_on_start(self) -> bool:
        return self._settings["ui"]["maximized_on_start"]

    # ─── Сеттеры (с автосохранением) ────────────────────────────────────────

    def set_main_db_path(self, path: str):
        self._settings["database"]["main_path"] = str(Path(path).resolve())
        self._save()

    def set_employees_db_path(self, path: str):
        self._settings["database"]["employees_path"] = str(Path(path).resolve())
        self._save()

    def set_editable_columns(self, columns: List[str]):
        self._settings["database"]["editable_columns"] = columns
        self._save()

    # ─── Универсальные методы (на всякий случай) ────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        """Доступ как к словарю: settings.get("database.auto_refresh_interval_sec")"""
        keys = key.split(".")
        value = self._settings
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """Установка как в словаре"""
        keys = key.split(".")
        d = self._settings
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
        self._save()

    def reset_to_defaults(self):
        """Сброс всех настроек к дефолтным"""
        self._settings = self.DEFAULT_SETTINGS.copy()
        self._save()

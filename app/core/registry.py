# Реестр вкладок (TAB_REGISTRY)
"""
Реестр вкладок.
Сюда удобно их помещать, чтобы не было проблем с дальнейшим масштабированием кода
"""
from typing import Type, Tuple
from PyQt6.QtWidgets import QWidget

from app.ui.tabs.home_tab import HomeTab
from app.ui.tabs.admin_tab import AdminTab
from app.ui.tabs.settings_tab import SettingsTab
from app.ui.tabs.team_tab import TeamTab
#from app.ui.tabs.dcm_tab import DcmTab
from app.ui.tabs.all_dcm_tab import AllDcmTab
from app.ui.tabs.translate_tab import TranslateTab

#from app.ui.tabs.cq_tab import CqTab
#from app.ui.tabs.archive_tab import ArchiveTab
# ... остальные по мере миграции


TAB_REGISTRY: dict[str, Tuple[Type[QWidget], str, bool]] = {
    "home":     (HomeTab,       "🏠 Главная",                True),
    "admin":    (AdminTab,      "🔧 Администрирование",      True),
    #"dcm":     (DcmTab,        "📊 Основные DCM",           False),
    "all_dcm": (AllDcmTab,     "📦 Все вопросы в работе",   False),
    #"cq":      (CqTab,         "🚨 Срочные DCM",            False),
    #"archive": (ArchiveTab,    "📦 Архив DCM",              False),
    "team":     (TeamTab,       "👥 Команда",                 True),
    "settings": (SettingsTab,   "⚙ Настройки приложения",     True),
    "translate": (TranslateTab, "Проверка перевода", False)
    # "stats", "settings" — добавишь позже
}
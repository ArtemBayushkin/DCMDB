# Реестр вкладок (TAB_REGISTRY)
"""
Реестр вкладок.
Сюда удобно их помещать, чтобы не было проблем с дальнейшим масштабированием кода
"""
from typing import Type, Tuple
from PyQt6.QtWidgets import QWidget

from app.ui.tabs.admin.archive_cq_tab import ArchiveCQTab
from app.ui.tabs.admin.cq_clarification import CqClar
from app.ui.tabs.admin.send_cq_tab import SendCqTab
from app.ui.tabs.admin.send_dcm_tab import SendDcmTab
from app.ui.tabs.user.archive_tab import ArchiveTab
from app.ui.tabs.user.home_tab import HomeTab
from app.ui.tabs.admin.admin_tab import AdminTab
from app.ui.tabs.user.settings_tab import SettingsTab
from app.ui.tabs.user.team_tab import TeamTab
from app.ui.tabs.user.dcm_tab import DcmTab
from app.ui.tabs.user.all_dcm_tab import AllDcmTab
from app.ui.tabs.admin.translate_tab import TranslateTab
from app.ui.tabs.user.cq_tab import CqTab
from app.core.upload_tab import CqUploadTab, DcmUploadTab


TAB_REGISTRY: dict[str, Tuple[Type[QWidget], str, bool]] = {
    "home":     (HomeTab,       "🏠 Главная",                True),
    "admin":    (AdminTab,      "🔧 Администрирование",      True),
    "dcm":     (DcmTab,        "📊 Основные DCM",           False),
    "all_dcm": (AllDcmTab,     "📦 Все вопросы в работе",   False),
    "cq":      (CqTab,         "🚨 Срочные DCM",            False),
    "archive": (ArchiveTab,    "📦 Архив DCM",              False),
    "team":     (TeamTab,       "👥 Команда",                 True),
    "settings": (SettingsTab,   "⚙ Настройки приложения",     True),
    "translate": (TranslateTab, "Проверка перевода", False),
    "cq_upload":  (CqUploadTab,  "🚨 Загрузка CQ",  False),
    "dcm_upload": (DcmUploadTab, "📥 Загрузка DCM", False),
    "send_cq":      (SendCqTab, "🪩Отправка CQ", False),
    "send_dcm":      (SendDcmTab, "Отправка DCM", False),
    "archive_cq":   (ArchiveCQTab, "Архив срочных DCM", False),
    "cq_clar":      (CqClar,       "Срочные DCM на уточнении", False)
}

# Абстрактный базовый класс всех вкладок
# core/base_tab.py
from abc import abstractmethod
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.core.current_user import CurrentUser
from app.ui.components.status_bar import StatusBar
from app.db.dcm_manager import DcmManager
from app.config.settings_manager import settings


class BaseTab(QWidget):
    """
    Базовый класс для всех вкладок приложения
    """

    def __init__(self, title: str = "", icon: str = "", space: int = 60, parent=None, main_window=None):
        super().__init__(parent)
        self.settings = settings
        self.title = title
        self.icon = icon
        self.space = space
        self.model = None
        self.table = None
        self._mgr = None
        if not hasattr(self, 'main_window'):
            self.main_window = main_window
        self.layout = QVBoxLayout()
        self.init_ui()
        self.setLayout(self.layout)
        self.status_bar = StatusBar(self, display_duration=3000, icon_size=18)

    def init_ui(self):
        """Общий код интерфейса"""
        # Заголовок
        self.layout.addSpacing(self.space)
        title_label = QLabel(f"{self.icon} {self.title}")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title_label)
        self.layout.addSpacing(self.space)
        try:
            self.add_content()
        except Exception as e:
            print(e)
            self._status_error('Ошибка открытия вкладки. Перейдите в настройки для подключения базы данных')

    @abstractmethod
    def add_content(self):
        """Здесь реализуется основной контент вкладки"""
        pass

    def save_changes(self):
        """Сохраняет только изменённые ячейки через DcmManager.save_changes()."""
        print("start save_changes...")
        if self.model is None:
            self._status_warning("Нет данных для сохранения изменений.\nОбновите вкладку")
            return

        try:
            with self._mgr as mgr:
                print("BaseTab.save_changes -> try save changes")
                success, count = mgr.save_changes(self.model)
        finally:
            print("BaseTab.save_changes -> call close _mgr.close")

        if success and count == 0:
            print("BaseTab.save_changes -> status: Нет изменений для сохранения")
            self._status_info("Нет изменений для сохранения")
        elif success:
            print(f"BaseTab.save_changes -> status: Сохранено: {count} строк")
            self._status_success(f"Сохранено: {count} строк")
            self.load_data(force=True)
        else:
            print("BaseTab.save_changes -> status: Ошибка при сохранении")
            self._status_error("Ошибка при сохранении — проверьте консоль")

    def load_data(self, checked=None, force=None):
        """Заглушка для переопределения"""
        pass

    def check_changes(self, force: bool = False):
        if not self.settings.get_main_db_path():
            self.status_bar.show_warning("База данных не настроена. Перейдите в Настройки для подключения БД.")
            return

        if not force and not self._confirm_unsaved("Обновить данные и потерять изменения"):
            return

    def connect_admin(self, text: str):
        if CurrentUser().is_admin:
            self.main_window.open_or_switch_tab(text)
        else:
            self.status_bar.show_warning("Эта функция доступна только администраторам")

    # ──────────────────────────────────────────────────────────────
    # Статус-бар
    # ──────────────────────────────────────────────────────────────

    def _status_info(self, message: str, duration: int = 3000) -> None:
        """Отправляет информационное сообщение в статус-бар главного окна."""
        self._send_status("info", message, duration)

    def _status_success(self, message: str, duration: int = 3000) -> None:
        """Отправляет сообщение об успехе в статус-бар главного окна."""
        self._send_status("success", message, duration)

    def _status_warning(self, message: str) -> None:
        """Показывает диалог-предупреждение."""
        if self.main_window and hasattr(self.main_window, 'status_bar'):
            self.main_window.status_bar.show_warning(message)
        else:
            QMessageBox.warning(self, "Внимание", message)

    def _status_error(self, message: str) -> None:
        """Показывает диалог с ошибкой."""
        if self.main_window and hasattr(self.main_window, 'status_bar'):
            self.main_window.status_bar.show_error(message)
        else:
            QMessageBox.critical(self, "Ошибка", message)

    def _send_status(self, level: str, message: str, duration: int) -> None:
        """Внутренний метод отправки сообщения в статус-бар."""
        if self.main_window and hasattr(self.main_window, 'status_bar'):
            sb = self.main_window.status_bar
            if level == "info":
                sb.show_info(message, duration)
            elif level == "success":
                sb.show_success(message, duration)
        else:
            print(f"[{level.upper()}] {message}")

    # ──────────────────────────────────────────────────────────────
    # Защита от потери несохраненных изменений
    # ──────────────────────────────────────────────────────────────

    def has_unsaved_changes(self) -> bool:
        """
        Возвращает True если есть несохранённые изменения.
        """
        return self.model is not None and self.model.has_changes()

    def _confirm_unsaved(self, action: str = "продолжить") -> bool:
        """
        Показывает диалог подтверждения при наличии несохраненных изменений.

        :param action: Описание действия, которое приведёт к потере изменений.
        :return: True если пользователь согласен потерять изменения, False — отмена.
        """
        if not self.has_unsaved_changes():
            return True

        reply = QMessageBox.question(
            self,
            "Несохранённые изменения",
            f"Есть несохранённые изменения.\n{action.capitalize()}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

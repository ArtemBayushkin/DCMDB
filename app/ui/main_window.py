from PyQt6.QtWidgets import (QMainWindow, QTabWidget,
                             QDockWidget, QListWidget, QListWidgetItem,
                             QToolBar, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.ui.tabs.config.about import AboutTab
from app.ui.tabs.user.home_tab import HomeTab
from app.core.registry import TAB_REGISTRY
from app.ui.components.status_bar import StatusBar


class AdvancedMainWindow(QMainWindow):
    def __init__(self, current_user=None):
        self.current_user = current_user
        super().__init__()
        self.setWindowTitle(f"Работа с базой данных")
        self.setGeometry(100, 50, 1200, 800)
        self.showMaximized()

        # Центральный виджет — вкладки
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tab_widget)

        # Статус-бар
        self.status_bar = StatusBar(self, display_duration=3000, icon_size=18)
        self.setStatusBar(self.status_bar)
        self.create_toolbars()

        # Создаём и сразу показываем главную вкладку
        self._init_home_tab()

        # Создаём боковую навигацию
        self._init_navigation_dock()

    def _init_home_tab(self):
        """
        Инициализации класса HomeTab на главном экране
        """
        home = HomeTab(main_window=self)
        self.tab_widget.addTab(home, "🏠 Главная")
        self.tab_widget.setCurrentIndex(0)

    def _init_navigation_dock(self):
        """
        Панель навигации, которая отображает все доступные вкладки.
        """
        dock = QDockWidget("📍Навигация", self)
        dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)  # заморозка панели навигации

        list_widget = QListWidget()

        for key, (widget_class, text, visible) in TAB_REGISTRY.items():
            if not visible:
                continue
            item = QListWidgetItem(text)
            item.setData(256, key)
            item.setFont(QFont('Arial'))
            list_widget.addItem(item)

        list_widget.itemClicked.connect(self._on_nav_clicked)
        dock.setWidget(list_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

    def create_toolbars(self):
        # Верхняя панель инструментов
        menubar = self.menuBar()
        file_menu = menubar.addMenu("📁 &Файл")
        # file_menu.addAction(self.refresh_action)
        file_menu.addSeparator()

        service_menu = menubar.addMenu("⚙️ &Сервис")
        service_menu.addAction("Настройки", lambda: self.open_or_switch_tab("settings"))

        help_menu = menubar.addMenu("❓ &Помощь")
        help_menu.addAction("О программе", self.show_about_dialog)

        # Нижняя статусная панель
        bottom_toolbar = QToolBar("Информационная панель")
        bottom_toolbar.setMovable(False)
        # bottom_toolbar.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, bottom_toolbar)

        # bottom_toolbar.addSeparator()
        bottom_toolbar.addWidget(QLabel("Пользователь: "))
        user_label = QLabel(self.current_user.full_name)
        user_label.setStyleSheet("color: blue; font-weight: bold;")
        bottom_toolbar.addWidget(user_label)

    def _on_nav_clicked(self, item):
        """
        Обрабатывает клики по элементам в навигационной панели (DockWidget с QListWidget)
        1. Получаем ключ вкладки;
        2. Проверяем, что ключ существует;
        3. Открываем/переключаем вкладку.

        :param item: QListWidgetItem - ключ вкладки
        :return: Открываем/переключаем вкладку.
        """
        print('AdvancedMainWindow -> _on_nav_clicked')
        key = item.data(256)
        if key:
            self.open_or_switch_tab(key)

    def open_or_switch_tab(self, key: str):
        """
        Открывает или переключается на вкладку по её ключу.

        Логика работы:
            --------------
            1. Проверяет существование ключа в реестре вкладок
            2. Если вкладка уже открыта - переключается на неё
            3. Если не открыта - создаёт новую вкладку.
        :param key: str
                    (Ключ вкладки из TAB_REGISTRY)
        :Example:
        >>> self.open_or_switch_tab('home')
        """
        # print('AdvancedMainWindow -> open_or_switch_tab')
        if key not in TAB_REGISTRY:
            self.status_bar.warning_dialog(self, message="Вкладка не зарегистрирована")
            # self.status_bar.show_warning(f"Вкладка '{key}' не зарегистрирована", 5000)
            return

        tab_class, title, va = TAB_REGISTRY[key]

        # Проверяем, открыта ли уже такая вкладка
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == title:
                self.tab_widget.setCurrentIndex(i)
                self.status_bar.show_info(f"Переключено на: {title}", 1000)
                return

        # Создаём новую вкладку
        try:
            new_widget = tab_class(self)
            self.tab_widget.addTab(new_widget, title)
            self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
            self.status_bar.show_info(f"Открыта вкладка: {title}", 1000)
        except Exception as e:
            self.status_bar.show_error(f"Ошибка создания вкладки: {e}")

    def close_tab(self, index: int):
        """
        Закрытие вкладки по крестику.
        Если вкладка содержит несохранённые изменения — спрашивает подтверждение.
        """
        widget = self.tab_widget.widget(index)
        tab_title = self.tab_widget.tabText(index)

        if hasattr(widget, 'has_unsaved_changes') and widget.has_unsaved_changes():
            if not widget._confirm_unsaved(f"Закрыть вкладку «{tab_title}» и потерять изменения"):
                return  # Пользователь отменил закрытие

        self.tab_widget.removeTab(index)
        self.status_bar.show_info(f"Закрыта вкладка: {tab_title}", 1000)

    def show_about_dialog(self):
        """Показывает диалоговое окно 'О программе'"""
        from app.ui.tabs.config.about import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec()

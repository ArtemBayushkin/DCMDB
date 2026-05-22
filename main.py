"""
Точка входа в приложение.
Инициализирует и запускает графический интерфейс приложения
"""
import sys
from PyQt6.QtWidgets import QApplication
from app.core.current_user import current_user
from app.ui.main_window import AdvancedMainWindow


def main():
    """
    Основная функция запуска приложения.
    Инициализирует QApplication, создает и отображает главное окно
    приложения с текущим пользователем, а затем запускает главный цикл
    обработки событий.
    :return: None (Функция завершается только при закрытии приложения через sys.exit.)
    """
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AdvancedMainWindow(current_user=current_user)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

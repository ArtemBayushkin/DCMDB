# main.py
import sys
from pathlib import Path
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication
from app.core.current_user import current_user
from ui.main_window import AdvancedMainWindow

# 1. Добавляем путь к plugins/Qt6 вручную (самый надёжный способ)
venv_root = Path(sys.executable).parent.parent  # обычно venv
plugins_dir = venv_root / "lib" / "site-packages" / "PyQt6" / "Qt6" / "plugins"

if plugins_dir.exists():
    QCoreApplication.addLibraryPath(str(plugins_dir))
    print(f"Добавлен путь к Qt6 plugins: {plugins_dir}")
else:
    print(f"Путь не найден: {plugins_dir}")

# 2. Альтернативный/дополнительный путь (иногда Qt ищет без Qt6/)
plugins_dir_alt = venv_root / "lib" / "site-packages" / "PyQt6" / "plugins"
if plugins_dir_alt.exists():
    QCoreApplication.addLibraryPath(str(plugins_dir_alt))
    print(f"Добавлен альтернативный путь: {plugins_dir_alt}")

# 3. Проверяем, что Qt теперь видит драйверы
from PyQt6.QtSql import QSqlDatabase
print("Доступные SQL-драйверы ПОСЛЕ добавления путей:", QSqlDatabase.drivers())


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AdvancedMainWindow(current_user=current_user)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
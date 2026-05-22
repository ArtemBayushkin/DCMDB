# Общие модели записей (опционально)
"""
Декораторы логирования записей
"""


def log_button_click(func):
    def wrapper(self, *args, **kwargs):
        print(f"{func.__cls__}Кнопка {func.__name__} нажата")
        return func(self, *args, **kwargs)

    return wrapper

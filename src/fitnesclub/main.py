import sqlite3

from .database.database import init_db
from .menu import main_menu, setup_menu
from .services.club import needs_setup


def main():
    try:
        init_db()
        if needs_setup():
            setup_menu()
        if not needs_setup():
            main_menu()
    except sqlite3.Error as exc:
        print(f"Ошибка инициализации базы: {exc}")
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nРабота завершена")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

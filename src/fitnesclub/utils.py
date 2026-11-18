import sqlite3


def run_menu(title, actions, *, once=False):
    while True:
        print(f"\n=== {title} ===")
        for index, (label, _) in enumerate(actions, start=1):
            print(f"{index}. {label}")
        print("0. Выход / назад")
        choice = input("Выберите действие: ").strip()
        if choice == "0":
            return
        choices = {str(index): action for index, (_, action) in enumerate(actions, start=1)}
        action = choices.get(choice)
        if action is None:
            print("Выберите пункт меню")
            continue
        try:
            action()
            if once:
                return
        except ValueError as exc:
            print(f"Ошибка: {exc}")
        except sqlite3.Error:
            print("Ошибка работы с базой данных")

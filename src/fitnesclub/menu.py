import sqlite3
from functools import partial

from . import auth
from .services import club


def _menu(title, actions, *, once=False):
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


def _id(label):
    try:
        value = int(input(f"{label}: "))
    except ValueError:
        raise ValueError("Введите целочисленный ID") from None
    if not 0 < value <= 2**63 - 1:
        raise ValueError("ID вне допустимого диапазона")
    return value


def _print_client(client):
    print(f"{client.ClientID} | {client.name} | {client.phone_number} | {client.email}")


def _find_clients(actor):
    matches = club.find_clients(actor, input("Имя, телефон, email или ID: "))
    if not matches:
        print("Клиенты не найдены")
    for client in matches:
        _print_client(client)


def _view_client(actor, client_id=None):
    _print_client(club.get_client(actor, client_id or _id("ID клиента")))


def _edit_client(actor, client_id=None):
    client_id = client_id or _id("ID клиента")
    client = club.get_client(actor, client_id)
    club.edit_client(
        actor, client_id,
        input(f"Имя [{client.name}]: ").strip() or client.name,
        input(f"Телефон [{client.phone_number}]: ").strip() or client.phone_number,
        input(f"Email [{client.email}]: ").strip() or client.email,
    )
    print("Данные сохранены")


def _delete_client(actor):
    client_id = _id("ID клиента")
    if input("Удалить клиента? (да/нет): ").strip().lower() == "да":
        club.delete_client(actor, client_id)
        print("Клиент удалён")


def _clients_menu(actor):
    _menu("Клиенты", [
        ("Зарегистрировать клиента", partial(auth.register_client, actor)),
        ("Найти клиента", partial(_find_clients, actor)),
        ("Просмотреть карточку", partial(_view_client, actor)),
        ("Изменить карточку", partial(_edit_client, actor)),
        ("Удалить клиента", partial(_delete_client, actor)),
    ])


def _schedule(actor):
    trainers, bookings = club.schedule(actor, input("Дата (ГГГГ-ММ-ДД): "))
    if not trainers:
        print("Тренеры ещё не добавлены")
    for coach in trainers:
        times = [record.time for record in bookings if record.CoachID == coach.CoachID]
        busy = ", ".join(sorted(times)) or "нет записей"
        print(f"{coach.CoachID} | {coach.name} | {coach.specialization or '—'} | Занято: {busy}")


def _book(actor):
    record_id = club.book_training(
        actor, _id("ID клиента"), _id("ID тренера"),
        input("Дата (ГГГГ-ММ-ДД): "), input("Время (ЧЧ:ММ): "),
    )
    print(f"Клиент записан. ID записи: {record_id}")


def _cancel(actor):
    club.cancel_training(actor, _id("ID записи"))
    print("Запись отменена")


def _records(actor):
    records = club.list_records(actor)
    if not records:
        print("Записей пока нет")
    for record in records:
        status = {"active": "активна", "cancelled": "отменена"}[record.status]
        print(f"{record.RecordID} | {record.date} {record.time} | "
              f"клиент {record.ClientID} | тренер {record.CoachID} | {status}")


def _bookings_menu(actor):
    _menu("Записи на тренировки", [
        ("Тренеры и занятое время", partial(_schedule, actor)),
        ("Записать клиента", partial(_book, actor)),
        ("Просмотреть записи", partial(_records, actor)),
        ("Отменить запись", partial(_cancel, actor)),
    ])


def _add_coach(actor):
    coach_id = club.add_coach(
        actor, input("Имя: "), input("Специализация: "), input("Email: "),
    )
    print(f"Тренер добавлен. ID: {coach_id}")


def _admin_login():
    actor = auth.login("admin")
    _menu(f"Администратор {actor.name}", [
        ("Клиенты", partial(_clients_menu, actor)),
        ("Записи на тренировки", partial(_bookings_menu, actor)),
        ("Добавить тренера", partial(_add_coach, actor)),
        ("Добавить администратора", partial(auth.register_admin, actor)),
    ])


def _client_login():
    actor = auth.login("client")
    _menu(f"Клиент {actor.name}", [
        ("Моя карточка", partial(_view_client, actor, actor.ClientID)),
        ("Изменить мои данные", partial(_edit_client, actor, actor.ClientID)),
        ("Расписание тренеров", partial(_schedule, actor)),
    ])


def main_menu():
    _menu("FitnesClub", [
        ("Вход администратора", _admin_login),
        ("Вход клиента", _client_login),
    ])


def setup_menu():
    _menu("Первый запуск", [("Создать первого администратора", auth.register_admin)], once=True)

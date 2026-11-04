from getpass import getpass

from .services import club


def login(role):
    identifier = input("Логин: " if role == "admin" else "Email: ")
    return club.authenticate(role, identifier, getpass("Пароль: "))


def register_admin(actor=None):
    admin_id = club.add_admin(
        actor, input("Имя: "), input("Логин: "), input("Email: "),
        getpass("Пароль (от 8 символов): "),
    )
    print(f"Администратор добавлен. ID: {admin_id}")


def register_client(actor):
    client_id = club.register_client(
        actor, input("Имя: "), input("Телефон: "), input("Email: "),
        getpass("Пароль (от 8 символов): "),
    )
    print(f"Клиент зарегистрирован. ID: {client_id}")


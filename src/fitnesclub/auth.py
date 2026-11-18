from .services import auth_serv, users_serv


def login(role):
    identifier = input("Логин: " if role == "admin" else "Email: ")
    return auth_serv.authenticate(role, identifier, input("Пароль: "))


def register_admin(actor=None):
    admin_id = auth_serv.add_admin(
        actor, input("ФИО: "), input("Логин: "), input("Email: "),
        input("Пароль (от 8 символов): "),
    )
    print(f"Администратор добавлен. ID: {admin_id}")


def register_client(actor):
    client_id = users_serv.register_client(
        actor, input("ФИО: "), input("Телефон: "), input("Email: "),
        input("Пароль (от 8 символов): "),
    )
    print(f"Клиент зарегистрирован. ID: {client_id}")

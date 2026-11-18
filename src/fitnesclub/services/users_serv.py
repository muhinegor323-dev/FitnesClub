from ..models.client import Client
from ..repositories.clients_rep import clients
from .access_control import require_admin
from .auth_serv import hash_password
from .validation import validate_email, required, save


def _client_details(name, phone, email):
    phone = required(phone, "Телефон")
    digits = "".join(char for char in phone if char in "0123456789")
    if any(char not in "0123456789+()- " for char in phone) or not 7 <= len(digits) <= 15:
        raise ValueError("Введите корректный телефон")
    return dict(name=required(name, "ФИО"), phone_number=digits, email=validate_email(email))


def register_client(actor, name, phone, email, password):
    require_admin(actor)
    return save(
        clients.create, "Телефон или email клиента уже используется",
        **_client_details(name, phone, email), AdminID=actor.AdminID,
        password_hash=hash_password(password),
    )


def find_clients(actor, query):
    require_admin(actor)
    query = required(query, "Поиск").casefold()
    return [
        client for client in clients.get_all()
        if any(query in value.casefold() for value in (
            str(client.ClientID), client.name, client.phone_number, client.email
        ))
    ]


def get_client(actor, client_id):
    if not isinstance(actor, Client) or actor.ClientID != client_id:
        require_admin(actor)
    client = clients.get_by_id(client_id)
    if client is None:
        raise ValueError("Клиент не найден")
    return client


def edit_client(actor, client_id, name, phone, email):
    get_client(actor, client_id)
    if not save(
        clients.update, "Телефон или email клиента уже используется",
        client_id, **_client_details(name, phone, email),
    ):
        raise ValueError("Клиент не найден")


def delete_client(actor, client_id):
    require_admin(actor)
    if not save(clients.delete, "У клиента есть история записей", client_id):
        raise ValueError("Клиент не найден")

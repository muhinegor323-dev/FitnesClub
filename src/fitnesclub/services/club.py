import hashlib
import hmac
import secrets
import sqlite3
from datetime import date, time

from ..models.entities import Admin, Client
from ..repositories.crud import admins, clients, coaches, records


def _required(value, label):
    value = value.strip()
    if not value:
        raise ValueError(f"Заполните поле «{label}»")
    return value


def _email(value):
    value = value.strip().lower()
    local, separator, domain = value.partition("@")
    if not local or not separator or "." not in domain or value.count("@") != 1 or any(
        char.isspace() for char in value
    ):
        raise ValueError("Введите корректный email")
    return value


def _digest(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600_000).hex()


def _hash_password(password):
    if len(password.strip()) < 8:
        raise ValueError("Пароль должен содержать минимум 8 символов")
    salt = secrets.token_bytes(16)
    return f"{salt.hex()}:{_digest(password, salt)}"


def authenticate(role, identifier, password):
    if role == "admin":
        matches = admins.get_all(login=identifier.strip().lower())
    elif role == "client":
        matches = clients.get_all(email=identifier.strip().lower())
    else:
        raise ValueError("Неизвестная роль")
    if matches:
        user = matches[0]
        salt, digest = user.password_hash.split(":")
        if hmac.compare_digest(_digest(password, bytes.fromhex(salt)), digest):
            return user
    raise ValueError("Неверные данные для входа")


def _require_admin(actor):
    if not isinstance(actor, Admin) or not admins.get_by_id(actor.AdminID):
        raise ValueError("Действие доступно администратору")


def _save(action, error, *args, **values):
    try:
        return action(*args, **values)
    except sqlite3.IntegrityError as exc:
        raise ValueError(error) from exc


def add_admin(actor, name, login, email, password):
    if actor is not None or admins.get_all():
        _require_admin(actor)
    return _save(
        admins.create, "Логин или email администратора уже используется",
        name=_required(name, "Имя"), login=_required(login, "Логин").lower(),
        email=_email(email), password_hash=_hash_password(password),
    )


def _client_details(name, phone, email):
    phone = _required(phone, "Телефон")
    digits = "".join(char for char in phone if char in "0123456789")
    if any(char not in "0123456789+()- " for char in phone) or not 7 <= len(digits) <= 15:
        raise ValueError("Введите корректный телефон")
    return dict(name=_required(name, "Имя"), phone_number=digits, email=_email(email))


def register_client(actor, name, phone, email, password):
    _require_admin(actor)
    return _save(
        clients.create, "Телефон или email клиента уже используется",
        **_client_details(name, phone, email), AdminID=actor.AdminID,
        password_hash=_hash_password(password),
    )


def find_clients(actor, query):
    _require_admin(actor)
    query = _required(query, "Поиск").casefold()
    return [
        client for client in clients.get_all()
        if any(query in value.casefold() for value in (
            str(client.ClientID), client.name, client.phone_number, client.email
        ))
    ]


def get_client(actor, client_id):
    if not isinstance(actor, Client) or actor.ClientID != client_id:
        _require_admin(actor)
    client = clients.get_by_id(client_id)
    if client is None:
        raise ValueError("Клиент не найден")
    return client


def edit_client(actor, client_id, name, phone, email):
    get_client(actor, client_id)
    if not _save(
        clients.update, "Телефон или email клиента уже используется",
        client_id, **_client_details(name, phone, email),
    ):
        raise ValueError("Клиент не найден")


def delete_client(actor, client_id):
    _require_admin(actor)
    if not _save(clients.delete, "У клиента есть история записей", client_id):
        raise ValueError("Клиент не найден")


def add_coach(actor, name, specialization, email):
    _require_admin(actor)
    return _save(
        coaches.create, "Email тренера уже используется",
        name=_required(name, "Имя"), specialization=specialization.strip() or None,
        email=_email(email),
    )


def schedule(actor, date_value):
    if not isinstance(actor, Client):
        _require_admin(actor)
    day = date.fromisoformat(date_value).isoformat()
    return coaches.get_all(), records.get_all(date=day, status="active")


def book_training(actor, client_id, coach_id, date_value, time_value):
    _require_admin(actor)
    get_client(actor, client_id)
    if not coaches.get_by_id(coach_id):
        raise ValueError("Тренер не найден")
    day = date.fromisoformat(date_value)
    hour = time.fromisoformat(time_value)
    if hour.tzinfo is not None or hour.second or hour.microsecond:
        raise ValueError("Введите время в формате ЧЧ:ММ")
    slot = hour.isoformat(timespec="minutes")
    return _save(
        records.create, "Время тренера занято или данные записи изменились",
        ClientID=client_id, CoachID=coach_id, AdminID=actor.AdminID,
        date=day.isoformat(), time=slot, status="active",
    )


def cancel_training(actor, record_id):
    _require_admin(actor)
    if not records.update(record_id, status="cancelled"):
        raise ValueError("Запись не найдена")


def list_records(actor):
    _require_admin(actor)
    return records.get_all()


def needs_setup():
    return not admins.get_all()

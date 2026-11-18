import hashlib
import hmac
import secrets

from ..repositories.admins_rep import admins
from ..repositories.clients_rep import clients
from .access_control import require_admin
from .validation import validate_email, required, save


def _digest(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600_000).hex()


def hash_password(password):
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


def add_admin(actor, name, login, email, password):
    if actor is not None or admins.get_all():
        require_admin(actor)
    return save(
        admins.create, "Логин или email администратора уже используется",
        name=required(name, "ФИО"), login=required(login, "Логин").lower(),
        email=validate_email(email), password_hash=hash_password(password),
    )


def needs_setup():
    return not admins.get_all()

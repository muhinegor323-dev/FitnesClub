import sqlite3


def required(value, label):
    value = value.strip()
    if not value:
        raise ValueError(f"Заполните поле «{label}»")
    return value


def validate_email(value):
    value = value.strip().lower()
    local, separator, domain = value.partition("@")
    if not local or not separator or "." not in domain or value.count("@") != 1 or any(
        char.isspace() for char in value
    ):
        raise ValueError("Введите корректный email")
    return value


def save(action, error, *args, **values):
    try:
        return action(*args, **values)
    except sqlite3.IntegrityError as exc:
        raise ValueError(error) from exc

from datetime import date

from ..models.client import Client
from ..repositories.coaches_rep import coaches
from ..repositories.records_rep import records
from .access_control import require_admin
from .validation import validate_email, required, save


def add_coach(actor, name, specialization, email):
    require_admin(actor)
    return save(
        coaches.create, "Email тренера уже используется",
        name=required(name, "ФИО"), specialization=specialization.strip() or None,
        email=validate_email(email),
    )


def schedule(actor, date_value):
    if not isinstance(actor, Client):
        require_admin(actor)
    day = date.fromisoformat(date_value).isoformat()
    return coaches.get_all(), records.get_all(date=day, status="active")

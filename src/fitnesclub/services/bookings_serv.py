from datetime import date, time

from ..repositories.coaches_rep import coaches
from ..repositories.records_rep import records
from .access_control import require_admin
from .users_serv import get_client
from .validation import save


def book_training(actor, client_id, coach_id, date_value, time_value):
    require_admin(actor)
    get_client(actor, client_id)
    if not coaches.get_by_id(coach_id):
        raise ValueError("Тренер не найден")
    day = date.fromisoformat(date_value)
    hour = time.fromisoformat(time_value)
    if hour.tzinfo is not None or hour.second or hour.microsecond:
        raise ValueError("Введите время в формате ЧЧ:ММ")
    slot = hour.isoformat(timespec="minutes")
    return save(
        records.create, "Время тренера занято или данные записи изменились",
        ClientID=client_id, CoachID=coach_id, AdminID=actor.AdminID,
        date=day.isoformat(), time=slot, status="active",
    )


def cancel_training(actor, record_id):
    require_admin(actor)
    if not records.update(record_id, status="cancelled"):
        raise ValueError("Запись не найдена")


def list_records(actor):
    require_admin(actor)
    return records.get_all()

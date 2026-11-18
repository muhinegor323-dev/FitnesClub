from ..database.db import get_connection
from ..models.record import Record
from .base import Repository


records = Repository(Record)


def read_export_rows():
    with get_connection() as connection:
        cursor = connection.execute("""
            SELECT r.RecordID AS id, r.date, r.time, r.status,
                   c.ClientID AS "client.id", c.name AS "client.name",
                   t.CoachID AS "coach.id", t.name AS "coach.name",
                   t.specialization AS "coach.specialization",
                   a.AdminID AS "admin.id", a.name AS "admin.name"
            FROM Record AS r
            LEFT JOIN Client AS c ON c.ClientID = r.ClientID
            LEFT JOIN Coach AS t ON t.CoachID = r.CoachID
            LEFT JOIN Admin AS a ON a.AdminID = r.AdminID
            ORDER BY r.RecordID
        """)
        return [column[0] for column in cursor.description], cursor.fetchall()

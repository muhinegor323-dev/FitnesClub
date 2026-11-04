from dataclasses import fields

from ..database.database import get_connection
from ..models.entities import Admin, Client, Coach, Record


class Repository:
    def __init__(self, model):
        self.model = model
        self.table = model.__name__
        self.columns = tuple(field.name for field in fields(model))
        self.key = self.columns[0]

    def _validate_columns(self, values):
        if not values or not values.keys() <= set(self.columns[1:]):
            raise ValueError("Недопустимые поля")

    def create(self, **values):
        self._validate_columns(values)
        columns = ", ".join(values)
        placeholders = ", ".join("?" for _ in values)
        with get_connection() as connection:
            cursor = connection.execute(
                f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})",
                tuple(values.values()),
            )
            return cursor.lastrowid

    def get_by_id(self, object_id):
        with get_connection() as connection:
            row = connection.execute(
                f"SELECT * FROM {self.table} WHERE {self.key} = ?", (object_id,)
            ).fetchone()
            return self.model(**row) if row else None

    def get_all(self, **filters):
        query = f"SELECT * FROM {self.table}"
        if filters:
            self._validate_columns(filters)
            query += " WHERE " + " AND ".join(f"{column} = ?" for column in filters)
        query += f" ORDER BY {self.key}"
        with get_connection() as connection:
            return [self.model(**row) for row in connection.execute(query, tuple(filters.values()))]

    def update(self, object_id, **values):
        self._validate_columns(values)
        assignments = ", ".join(f"{column} = ?" for column in values)
        with get_connection() as connection:
            cursor = connection.execute(
                f"UPDATE {self.table} SET {assignments} WHERE {self.key} = ?",
                (*values.values(), object_id),
            )
            return cursor.rowcount > 0

    def delete(self, object_id):
        with get_connection() as connection:
            cursor = connection.execute(
                f"DELETE FROM {self.table} WHERE {self.key} = ?", (object_id,)
            )
            return cursor.rowcount > 0


admins = Repository(Admin)
clients = Repository(Client)
coaches = Repository(Coach)
records = Repository(Record)


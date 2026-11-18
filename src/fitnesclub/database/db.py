import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def get_connection():
    path = os.environ.get("FITNESCLUB_DB", "fitnesclub.sqlite3")
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            yield connection
    finally:
        connection.close()


def init_db():
    schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    with get_connection() as connection:
        connection.executescript(schema)


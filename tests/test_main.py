import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.fitnesclub.database.database import init_db
from src.fitnesclub.main import main
from src.fitnesclub.repositories.crud import clients, records
from src.fitnesclub.services import club


class ClubTest(unittest.TestCase):
    def setUp(self):
        directory = self._temporary_directory()
        environment = patch.dict(os.environ, {
            "FITNESCLUB_DB": str(Path(directory) / "test.sqlite3"),
        })
        environment.start()
        self.addCleanup(environment.stop)

    def _temporary_directory(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        return directory.name

    def test_roles_and_booking(self):
        init_db()
        admin_id = club.add_admin(None, "Администратор", "admin", "admin@example.org", "test-pass")
        admin = club.authenticate("admin", "admin", "test-pass")
        self.assertEqual(admin.AdminID, admin_id)
        with self.assertRaises(ValueError):
            club.add_admin(None, "Второй", "second", "second@example.org", "test-pass")

        client_id = club.register_client(admin, "Анна", "123456789", "anna@example.org", "test-pass")
        other_id = club.register_client(admin, "Иван", "987654321", "ivan@example.org", "test-pass")
        client = club.authenticate("client", "anna@example.org", "test-pass")
        self.assertEqual(club.get_client(client, client_id).AdminID, admin_id)
        with self.assertRaises(ValueError):
            club.get_client(client, other_id)
        with self.assertRaises(ValueError):
            club.authenticate("client", "anna@example.org", "wrong")

        coach_id = club.add_coach(admin, "Тренер", "Силовые", "coach@example.org")
        day, hour = "2030-01-15", "10:00"
        record_id = club.book_training(admin, client_id, coach_id, day, hour)
        with self.assertRaisesRegex(ValueError, "занято"):
            club.book_training(admin, other_id, coach_id, day, hour)
        club.cancel_training(admin, record_id)
        new_id = club.book_training(admin, other_id, coach_id, day, hour)
        init_db()
        self.assertEqual(records.get_by_id(record_id).status, "cancelled")
        self.assertEqual([record.RecordID for record in club.schedule(client, day)[1]], [new_id])
        with self.assertRaisesRegex(ValueError, "история"):
            club.delete_client(admin, client_id)

    def test_console_registration(self):
        answers = [
            "1", "Администратор", "admin", "admin@example.org",
            "1", "admin", "1", "1", "Анна", "123456789", "anna@example.org",
            "0", "0", "2", "anna@example.org", "1", "0", "0",
        ]
        with (
            patch("builtins.input", side_effect=answers),
            patch("src.fitnesclub.auth.getpass", return_value="test-pass"),
            patch("builtins.print") as output,
        ):
            self.assertEqual(main(), 0)
        self.assertEqual(clients.get_all()[0].name, "Анна")
        output.assert_any_call("Клиент зарегистрирован. ID: 1")
        output.assert_any_call("1 | Анна | 123456789 | anna@example.org")


if __name__ == "__main__":
    unittest.main()


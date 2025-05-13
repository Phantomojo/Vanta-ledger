import os
import unittest
import tempfile
import sqlite3
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend')))
import importlib.util
spec = importlib.util.spec_from_file_location("kivy_app", os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'frontend', 'kivy_app.py')))
kivy_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kivy_app)
VantaLedgerUI = kivy_app.VantaLedgerUI

class TestVantaLedgerApp(unittest.TestCase):
    def setUp(self):
        # Setup a temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app_ui = VantaLedgerUI()
        self.app_ui.db_path = self.db_path
        self.app_ui.load_settings()
        self.app_ui.authenticated = True
        self.app_ui.update_ui_state()

        # Manually assign ObjectProperty widgets to avoid NoneType errors in tests
        self.app_ui.type_input = type('obj', (object,), {'text': ''})()
        self.app_ui.amount_input = type('obj', (object,), {'text': ''})()
        self.app_ui.description_input = type('obj', (object,), {'text': ''})()
        self.app_ui.date_input = type('obj', (object,), {'text': ''})()
        self.app_ui.transaction_list = type('obj', (object,), {'add_widget': lambda x: None, 'clear_widgets': lambda *args: None})()
        self.app_ui.summary_label = type('obj', (object,), {'text': ''})()
        self.app_ui.currency_input = type('obj', (object,), {'text': 'USD'})()
        self.app_ui.allow_negative_checkbox = type('obj', (object,), {'active': False})()
        self.app_ui.login_btn = type('obj', (object,), {'disabled': False})()
        self.app_ui.logout_btn = type('obj', (object,), {'disabled': True})()
        self.app_ui.tab_panel = type('obj', (object,), {'disabled': True})()
        self.app_ui.save_btn = type('obj', (object,), {'disabled': False})()
        self.app_ui.cancel_btn = type('obj', (object,), {'disabled': False})()
        self.app_ui.export_btn = type('obj', (object,), {'disabled': False})()

        # Initialize DB schema
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_login_logout_ui_state(self):
        self.app_ui.authenticated = False
        self.app_ui.update_ui_state()
        self.assertTrue(self.app_ui.logout_btn.disabled)
        self.assertFalse(self.app_ui.login_btn.disabled)
        self.app_ui.authenticated = True
        self.app_ui.update_ui_state()
        self.assertTrue(self.app_ui.login_btn.disabled)
        self.assertFalse(self.app_ui.logout_btn.disabled)

    def test_add_transaction_valid(self):
        self.app_ui.type_input.text = "sale"
        self.app_ui.amount_input.text = "100.50"
        self.app_ui.description_input.text = "Test sale"
        self.app_ui.date_input.text = "2023-01-01"
        self.app_ui.editing_id = None
        self.app_ui.save_transaction()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        rows = cursor.fetchall()
        conn.close()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], "sale")
        self.assertAlmostEqual(rows[0][2], 100.50)
        self.assertEqual(rows[0][3], "Test sale")
        self.assertEqual(rows[0][4], "2023-01-01")

    def test_add_transaction_invalid_amount(self):
        self.app_ui.type_input.text = "sale"
        self.app_ui.amount_input.text = "invalid"
        self.app_ui.description_input.text = "Test sale"
        self.app_ui.date_input.text = "2023-01-01"
        self.app_ui.editing_id = None
        # Should show popup, but here we just check no insertion
        self.app_ui.save_transaction()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        rows = cursor.fetchall()
        conn.close()
        self.assertEqual(len(rows), 0)

    def test_edit_transaction(self):
        # Insert a transaction
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transactions (type, amount, description, date) VALUES (?, ?, ?, ?)",
            ("sale", 50.0, "Old description", "2023-01-01"),
        )
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()

        # Edit the transaction
        self.app_ui.editing_id = last_id
        self.app_ui.type_input.text = "expenditure"
        self.app_ui.amount_input.text = "75.25"
        self.app_ui.description_input.text = "Updated description"
        self.app_ui.date_input.text = "2023-02-01"
        self.app_ui.save_transaction()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE id=?", (last_id,))
        row = cursor.fetchone()
        conn.close()
        self.assertEqual(row[1], "expenditure")
        self.assertAlmostEqual(row[2], 75.25)
        self.assertEqual(row[3], "Updated description")
        self.assertEqual(row[4], "2023-02-01")

    def test_delete_transaction(self):
        # Insert a transaction
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transactions (type, amount, description, date) VALUES (?, ?, ?, ?)",
            ("sale", 50.0, "To be deleted", "2023-01-01"),
        )
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()

        self.app_ui.editing_id = last_id
        self.app_ui.delete_transaction()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE id=?", (last_id,))
        row = cursor.fetchone()
        conn.close()
        self.assertIsNone(row)

    def test_load_summary(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transactions (type, amount, description, date) VALUES (?, ?, ?, ?)",
            ("sale", 100.0, "Sale 1", "2023-01-01"),
        )
        cursor.execute(
            "INSERT INTO transactions (type, amount, description, date) VALUES (?, ?, ?, ?)",
            ("expenditure", 40.0, "Expense 1", "2023-01-02"),
        )
        conn.commit()
        conn.close()

        self.app_ui.load_summary()
        expected_text = (
            f"Total Sales: {self.app_ui.currency} 100.00\n"
            f"Total Expenses: {self.app_ui.currency} 40.00\n"
            f"Profit/Loss: {self.app_ui.currency} 60.00\n"
        )
        # Remove trailing whitespace and normalize newlines for comparison
        actual_text = self.app_ui.summary_label.text.replace('\\n', '\n').strip()
        expected_text = expected_text.strip()
        self.assertEqual(actual_text, expected_text)

    def test_save_settings(self):
        self.app_ui.currency_input.text = "EUR"
        self.app_ui.allow_negative_checkbox.active = True
        self.app_ui.save_settings()
        self.assertEqual(self.app_ui.currency, "EUR")
        self.assertTrue(self.app_ui.allow_negative_balance)

    def test_change_password_valid(self):
        old_token = self.app_ui.access_token
        new_token = "newtoken123"
        self.app_ui.change_password(new_token)
        self.assertEqual(self.app_ui.access_token, new_token)
        # Login with new token should succeed
        self.app_ui.access_token_input = type('obj', (object,), {'text': new_token})()
        self.app_ui.login()
        self.assertTrue(self.app_ui.authenticated)

    def test_change_password_to_admin_token(self):
        admin_token = self.app_ui.admin_token
        self.app_ui.change_password(admin_token)
        # Token should not change to admin token
        self.assertNotEqual(self.app_ui.access_token, admin_token)

    def test_login_with_admin_token(self):
        admin_token = self.app_ui.admin_token
        self.app_ui.access_token_input = type('obj', (object,), {'text': admin_token})()
        self.app_ui.login()
        self.assertTrue(self.app_ui.authenticated)

if __name__ == "__main__":
    unittest.main()

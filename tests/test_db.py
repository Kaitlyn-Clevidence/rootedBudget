import unittest
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime
import my_auth  # Assuming the functions are defined in my_auth.py
import db
import db_interface as db_int

import sqlite3
    
class MyAuthTests(unittest.TestCase):
    def setUp(self):
        # Use an in-memory SQLite database for isolated testing
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row

        # Patch db.get_db_connection to always return the in-memory connection
        db.get_db_connection = lambda: self.conn

        # Initialize the tables on the in-memory database
        db.init_tables()

    def tearDown(self):
        self.conn.close()

    def tearDown(self):
        self.conn.close()

    def test_create_user_success(self):
        result = db.db_create_user("testuser", "test@example.com", "hashed_pw")
        self.assertIsNotNone(result)

        # Verify user exists
        cur = self.conn.cursor()
        user = cur.execute("SELECT * FROM users WHERE username = ?", ("testuser",)).fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user["email"], "test@example.com")
        self.assertEqual(user["password_hash"], "hashed_pw")

    #def test_create_user_duplicate_username_or_email(self):
    #    db.init_tables()  # Re-init tables since patching overrides connection
    #    db.db_create_user("testuser", "test@example.com", "hashed_pw")

    #    with self.assertRaises(sqlite3.IntegrityError):
    #        db.db_create_user("testuser", "another@example.com", "hashed_pw")  # Duplicate username

    #    with self.assertRaises(sqlite3.IntegrityError):
    #        db.db_create_user("anotheruser", "test@example.com", "hashed_pw")  # Duplicate email

    @patch('my_auth.create_user')
    @patch('db.get_user')
    def test_create_user_success(self, mock_get_user, mock_db_create_user):
        mock_db_create_user.return_value = True
        mock_get_user.return_value = {'id': 1}
        result = my_auth.create_user("testuser", "test@example.com", "password123")
        self.assertTrue(result)
        mock_db_create_user.assert_called_once_with("testuser", "test@example.com", ANY)
    
    @patch('db.get_user')
    def test_login_user_failure_incorrect_password(self, mock_get_user):
        mock_get_user.return_value = {'id': 1, 'username': 'testuser', 'password_hash': 'hashed_password'}
        with patch('werkzeug.security.check_password_hash', return_value=False):
            result = my_auth.login_user("testuser", "wrongpassword")
        self.assertFalse(result)
        mock_get_user.assert_called_once_with("testuser")
    
    @patch('db.get_user')
    def test_login_user_failure_user_not_found(self, mock_get_user):
        mock_get_user.return_value = None
        result = my_auth.login_user("nonexistentuser", "password123")
        self.assertFalse(result)
        mock_get_user.assert_called_once_with("nonexistentuser")
    
    #@patch('db.get_user')
    #def test_login_user_from_form_success(self, mock_get_user):
     #   mock_get_user.return_value = {'id': 1, 'username': 'testuser', 'password_hash': 'hashed_password'}
      #  with patch('werkzeug.security.check_password_hash', return_value=True):
       #     result = my_auth.login_user_from_form("testuser", "password123")
        #self.assertEqual(result, {'id': 1, 'username': 'testuser', 'password_hash': 'hashed_password'})
        #mock_get_user.assert_called_once_with("testuser")
    
    #@patch('db.get_user')
    #def test_login_user_from_form_failure(self, mock_get_user):
    #    mock_get_user.return_value = None
    #    result = my_auth.login_user_from_form("nonexistentuser", "password123")
    #    self.assertIsNone(result)
    #    mock_get_user.assert_called_once_with("nonexistentuser")

    @patch('db.create_category')
    def test_add_category_success(self, mock_create_category):
        mock_create_category.return_value = True
        result = db_int.add_category(1, "Food")
        self.assertTrue(result)
        mock_create_category.assert_called_once_with(1, "Food")

    @patch('db.create_category')
    def test_add_category_failure(self, mock_create_category):
        mock_create_category.side_effect = Exception("Database error")
        result = db_int.add_category(1, "Food")
        self.assertFalse(result)
        mock_create_category.assert_called_once_with(1, "Food")

    @patch('db.get_category_id_by_name')
    @patch('db.create_transaction')
    def test_add_transaction_success(self, mock_create_transaction, mock_get_category_id):
        mock_get_category_id.return_value = 1
        mock_create_transaction.return_value = True

        result = db_int.add_transaction(1, "Lunch", "Bought lunch", "food", 10.5, False, True, "2025-03-01")
        
        self.assertTrue(result)
        mock_create_transaction.assert_called_once_with(1, "Lunch", "Bought lunch", 1, 10.5, False, True, "2025-03-01")


    @patch('db.get_category_id_by_name')
    @patch('db.create_transaction')
    def test_add_transaction_failure(self, mock_create_transaction, mock_get_category_id):
        mock_get_category_id.return_value = 1
        mock_create_transaction.side_effect = Exception("Database error")

        result = db_int.add_transaction(1, "Lunch", "Bought lunch", "food", 10.5, False, True, "2025-03-01")

        self.assertFalse(result)
        mock_create_transaction.assert_called_once_with(1, "Lunch", "Bought lunch", 1, 10.5, False, True, "2025-03-01")


    @patch('db.get_category_id_by_name')
    def test_get_category_id_by_name_success(self, mock_get_category_id):
        mock_get_category_id.return_value = 1
        result = db_int.get_category_id_by_name(1, "food")
        self.assertEqual(result, 1)
        mock_get_category_id.assert_called_once_with(1, "food")

    @patch('db.get_category_id_by_name')
    def test_get_category_id_by_name_failure(self, mock_get_category_id):
        mock_get_category_id.return_value = None
        result = db_int.get_category_id_by_name(1, "invalid_category")
        self.assertIsNone(result)
        mock_get_category_id.assert_called_once_with(1, "invalid_category")

    @patch('db.get_transactions_of_user')
    def test_find_events(self, mock_get_transactions):
        mock_get_transactions.return_value = [
            {"created_at": "2025-03-01", "amount": 10.5, "expense": True, "title": "Lunch", "description": "Bought lunch"},
            {"created_at": "2025-03-02", "amount": 20.0, "expense": False, "title": "Salary", "description": "Received salary"}
        ]
        events = db_int.find_events(1)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["date"], datetime.strptime("2025-03-01", "%Y-%m-%d"))
        self.assertEqual(events[0]["type"], "expense")
        self.assertEqual(events[1]["type"], "income")

if __name__ == '__main__':
    unittest.main()
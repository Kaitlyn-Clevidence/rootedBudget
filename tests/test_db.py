import unittest
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime
import my_auth 
import db
import db_interface

import sqlite3
    
class MyAuthTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        db.get_db_connection = lambda: self.conn
        db.init_tables()

    def tearDown(self):
        self.conn.close()

    def test_create_user_success(self):
        result = db.db_create_user("testuser", "test@example.com", "hashed_pw")
        self.assertIsNotNone(result)

        cur = self.conn.cursor()
        user = cur.execute("SELECT * FROM users WHERE username = ?", ("testuser",)).fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user["email"], "test@example.com")
        self.assertEqual(user["password_hash"], "hashed_pw")

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

    @patch('db.create_category')
    def test_add_category_success(self, mock_create_category):
        mock_create_category.return_value = True
        result = db_interface.add_category(1, "Food")
        self.assertTrue(result)
        mock_create_category.assert_called_once_with(1, "Food")

    @patch('db.create_category')
    def test_add_category_failure(self, mock_create_category):
        mock_create_category.side_effect = Exception("Database error")
        result = db_interface.add_category(1, "Food")
        self.assertFalse(result)
        mock_create_category.assert_called_once_with(1, "Food")

    @patch('db.get_category_id_by_name')
    @patch('db.create_transaction')
    def test_add_transaction_success(self, mock_create_transaction, mock_get_category_id):
        mock_get_category_id.return_value = 1
        mock_create_transaction.return_value = True

        result = db_interface.add_transaction(1, "Lunch", "Bought lunch", "food", 10.5, False, True, "2025-03-01")
        
        self.assertTrue(result)
        mock_create_transaction.assert_called_once_with(1, "Lunch", "Bought lunch", 1, 10.5, False, True, "2025-03-01")


    @patch('db.get_category_id_by_name')
    @patch('db.create_transaction')
    def test_add_transaction_failure(self, mock_create_transaction, mock_get_category_id):
        mock_get_category_id.return_value = 1
        mock_create_transaction.side_effect = Exception("Database error")

        result = db_interface.add_transaction(1, "Lunch", "Bought lunch", "food", 10.5, False, True, "2025-03-01")

        self.assertFalse(result)
        mock_create_transaction.assert_called_once_with(1, "Lunch", "Bought lunch", 1, 10.5, False, True, "2025-03-01")


    @patch('db.get_category_id_by_name')
    def test_get_category_id_by_name_success(self, mock_get_category_id):
        mock_get_category_id.return_value = 1
        result = db_interface.get_category_id_by_name(1, "food")
        self.assertEqual(result, 1)
        mock_get_category_id.assert_called_once_with(1, "food")

    @patch('db.get_category_id_by_name')
    def test_get_category_id_by_name_failure(self, mock_get_category_id):
        mock_get_category_id.return_value = None
        result = db_interface.get_category_id_by_name(1, "invalid_category")
        self.assertIsNone(result)
        mock_get_category_id.assert_called_once_with(1, "invalid_category")

    @patch('db.get_transactions_of_user')
    def test_find_events(self, mock_get_transactions):
        mock_get_transactions.return_value = [
            {"created_at": "2025-03-01", "amount": 10.5, "expense": True, "title": "Lunch", "description": "Bought lunch"},
            {"created_at": "2025-03-02", "amount": 20.0, "expense": False, "title": "Salary", "description": "Received salary"}
        ]
        events = db_interface.find_events(1)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["date"], datetime.strptime("2025-03-01", "%Y-%m-%d"))
        self.assertEqual(events[0]["type"], "expense")
        self.assertEqual(events[1]["type"], "income")

    @patch('db.save_user_budget')
    def test_save_user_budget_success(self, mock_save_budget):
        mock_save_budget.return_value = True
        result = db.save_user_budget(1, 1000.0)
        self.assertTrue(result) 
        mock_save_budget.assert_called_once_with(1, 1000.0)

    @patch('db.get_user')
    def test_get_user_invalid_identifier(self, mock_get_user):
        mock_get_user.return_value = None
        result = db.get_user("nonexistentuser")
        self.assertIsNone(result)
        mock_get_user.assert_called_once_with("nonexistentuser")
    
    @patch('db.get_transactions_of_user')
    def test_get_transactions_multiple(self, mock_get_transactions):
        mock_get_transactions.return_value = [
            {"title": "Lunch", "amount": 15.0, "category_id": 1, "expense": True},
            {"title": "Salary", "amount": 3000.0, "category_id": 2, "expense": False}
        ]
        result = db.get_transactions_of_user(1)
        self.assertEqual(len(result), 2) 
        self.assertEqual(result[0]['title'], "Lunch")
        self.assertEqual(result[1]['title'], "Salary")

    @patch('db.get_categories_of_user')
    def test_get_categories_multiple(self, mock_get_categories):
        mock_get_categories.return_value = [
            {"name": "food", "user_id": 1},
            {"name": "rent", "user_id": 1}
        ]
        result = db.get_categories_of_user(1)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], "food")
        self.assertEqual(result[1]['name'], "rent")

if __name__ == '__main__':
    unittest.main()
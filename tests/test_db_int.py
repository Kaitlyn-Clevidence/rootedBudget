import unittest
from unittest.mock import patch
import flaskApp
import db_interface

class TestFinanceTracker(unittest.TestCase):
    USER_ID = 1
    CATEGORY_NAME = "Food"
    CATEGORY_ID = 1
    VALID_DATE = "2025-05-01"
    INVALID_DATE = "invalid-date"
    TRANSACTION_DATA = {
        "title": "Test",
        "description": "Desc",
        "category_name": CATEGORY_NAME,
        "amount": 10.5,
        "expense": False,
        "recurring": True,
        "input_date": VALID_DATE
    }

    @patch('db_interface.db.create_transaction')
    @patch('db_interface.get_category_id_by_name')
    def test_add_transaction_success(self, mock_get_category_id_by_name, mock_create_transaction):
        mock_get_category_id_by_name.return_value = self.CATEGORY_ID
        mock_create_transaction.return_value = None

        result = db_interface.add_transaction(self.USER_ID, **self.TRANSACTION_DATA)
        self.assertTrue(result)
        mock_create_transaction.assert_called_once()

    @patch('db_interface.get_category_id_by_name')
    def test_add_transaction_invalid_category(self, mock_get_category_id_by_name):
        mock_get_category_id_by_name.return_value = None
        result = db_interface.add_transaction(self.USER_ID, **self.TRANSACTION_DATA)
        self.assertFalse(result)

    @patch('db_interface.db.create_transaction', side_effect=Exception("DB Error"))
    @patch('db_interface.get_category_id_by_name')
    def test_add_transaction_db_error(self, mock_get_category_id_by_name, mock_create_transaction):
        mock_get_category_id_by_name.return_value = self.CATEGORY_ID
        result = db_interface.add_transaction(self.USER_ID, **self.TRANSACTION_DATA)
        self.assertFalse(result)

    @patch('db_interface.db.create_transaction')
    @patch('db_interface.get_category_id_by_name')
    def test_add_transaction_invalid_amount(self, mock_get_category_id_by_name, mock_create_transaction):
        mock_get_category_id_by_name.return_value = self.CATEGORY_ID
        result = db_interface.add_transaction(
            self.USER_ID,
            title="Test",
            description="Desc",
            category_name=self.CATEGORY_NAME,
            amount=-100.0,
            expense=False,
            recurring=True,
            input_date=self.VALID_DATE
        )
        self.assertTrue(result)

    @patch('db_interface.get_category_id_by_name')
    def test_add_transaction_invalid_date_format(self, mock_get_category_id_by_name):
        mock_get_category_id_by_name.return_value = self.CATEGORY_ID
        result = db_interface.add_transaction(
            self.USER_ID,
            title="Test",
            description="Desc",
            category_name=self.CATEGORY_NAME,
            amount=10.0,
            expense=False,
            recurring=True,
            input_date=self.INVALID_DATE
        )
        self.assertFalse(result)

    @patch('db_interface.db.create_category')
    def test_add_category_success(self, mock_create_category):
        mock_create_category.return_value = None
        result = db_interface.add_category(self.USER_ID, "Groceries")
        self.assertTrue(result)
        mock_create_category.assert_called_once_with(self.USER_ID, "Groceries")

    @patch('db_interface.db.create_category', side_effect=Exception("DB Error"))
    def test_add_category_failure(self, mock_create_category):
        result = db_interface.add_category(self.USER_ID, "Groceries")
        self.assertFalse(result)

    @patch('db_interface.db.get_category_id_by_name')
    def test_get_category_id_by_name_success(self, mock_get):
        mock_get.return_value = 42
        result = db_interface.get_category_id_by_name(self.USER_ID, "Utilities")
        self.assertEqual(result, 42)

    @patch('db_interface.db.get_category_id_by_name', side_effect=Exception("Not Found"))
    def test_get_category_id_by_name_failure(self, mock_get):
        result = db_interface.get_category_id_by_name(self.USER_ID, "Invalid")
        self.assertIsNone(result)

    @patch('db_interface.db.get_transactions_of_user')
    def test_find_events(self, mock_get_transactions):
        mock_get_transactions.return_value = [
            {
                "created_at": "2025-05-01",
                "amount": 20.0,
                "expense": True,
                "title": "Lunch",
                "description": "Fast food"
            },
            {
                "created_at": "2025-05-02",
                "amount": 100.0,
                "expense": False,
                "title": "Salary",
                "description": "Monthly salary"
            }
        ]
        result = db_interface.find_events(self.USER_ID)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["type"], "expense")
        self.assertEqual(result[1]["type"], "income")
        self.assertEqual(result[0]["name"], "Lunch")
        self.assertEqual(result[1]["name"], "Salary")

    @patch('flaskApp.my_auth.login_user_from_form')
    def test_login_user_success(self, mock_login):
        mock_login.return_value = {"id": self.USER_ID, "username": "testuser"}
        result = flaskApp.my_auth.login_user_from_form("testuser", "password123")
        self.assertEqual(result["username"], "testuser")

    @patch('flaskApp.my_auth.login_user_from_form')
    def test_login_user_failure(self, mock_login):
        mock_login.return_value = None
        result = flaskApp.my_auth.login_user_from_form("testuser", "wrongpass")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
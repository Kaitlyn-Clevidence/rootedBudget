#lots of integration between authentication and database here

import unittest
from unittest.mock import patch, MagicMock, ANY, call
import my_auth as my_auth  # Assuming the functions are defined in my_auth.py

class MyAuthTests(unittest.TestCase):
    
    @patch('my_auth.init_default_categories')
    @patch('db.db_create_user')
    @patch('db.get_user')
    def test_create_user_success(self, mock_get_user, mock_db_create_user, mock_init_categories):
        mock_db_create_user.return_value = True
        mock_get_user.return_value = {'id': 1}
        mock_init_categories.return_value = None
        
        result = my_auth.create_user("testuser", "test@example.com", "password123")
        
        self.assertTrue(result)
        mock_db_create_user.assert_called_once_with("testuser", "test@example.com", ANY)
        mock_init_categories.assert_called_once_with(1, ["rent", "groceries", "spending", "paycheck", "savings"])

    @patch('db.db_create_user')  # Patch the actual DB function
    @patch('db.get_user')     # If get_user is also used inside create_user
    def test_create_user_failure(self, mock_get_user, mock_db_create_user):
        mock_db_create_user.side_effect = Exception("Database error")
        result = my_auth.create_user("testuser", "test@example.com", "password123")
        self.assertFalse(result)
        mock_db_create_user.assert_called_once_with("testuser", "test@example.com", ANY)

    @patch('my_auth.check_password_hash', return_value=True)
    @patch('db.get_user')
    def test_login_user_success(self, mock_get_user, mock_check_password):
        mock_get_user.return_value = {
            'id': 1, 'username': 'testuser', 'password_hash': 'hashed_password'
        }

        result = my_auth.login_user("testuser", "password123")

        self.assertTrue(result)
        mock_get_user.assert_called_once_with("testuser")
        mock_check_password.assert_called_once_with('hashed_password', 'password123')

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
    
    @patch('my_auth.login_user', return_value=True)
    @patch('db.get_user')
    def test_login_user_from_form_success(self, mock_get_user, mock_login_user):
        mock_get_user.return_value = {
            'id': 1,
            'username': 'testuser',
            'password_hash': 'hashed_password'
        }

        result = my_auth.login_user_from_form("testuser", "password123")

        self.assertEqual(result, {'id': 1, 'username': 'testuser', 'password_hash': 'hashed_password'})
        mock_login_user.assert_called_once_with("testuser", "password123")
        mock_get_user.assert_called_once_with("testuser")

    
    @patch('db.get_user')
    def test_login_user_from_form_failure(self, mock_get_user):
        mock_get_user.return_value = None
        result = my_auth.login_user_from_form("nonexistentuser", "password123")
        self.assertIsNone(result)
        mock_get_user.assert_called_once_with("nonexistentuser")

    @patch('db.create_category')
    def test_init_default_categories(self, mock_create_category):
        user_id = 1
        categories = ["rent", "groceries", "spending", "paycheck", "savings"]
        my_auth.init_default_categories(user_id, categories)
        for category in categories:
            mock_create_category.assert_any_call(user_id, category)

if __name__ == '__main__':
    unittest.main()
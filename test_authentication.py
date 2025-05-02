import unittest
from unittest.mock import patch, MagicMock
import my_auth  # Assuming the functions are defined in my_auth.py

class MyAuthTests(unittest.TestCase):

    @patch('db.db_create_user')
    @patch('db.get_user')
    @patch('db.create_category')
    def test_create_user_success(self, mock_create_category, mock_get_user, mock_db_create_user):
        mock_db_create_user.return_value = True
        mock_get_user.return_value = {'id': 1}
        mock_create_category.return_value = True
        
        result = my_auth.create_user("testuser", "test@example.com", "password123")
        self.assertTrue(result)
        mock_db_create_user.assert_called_once_with("testuser", "test@example.com", "hashed_password")
        mock_create_category.assert_called_with(1, "rent")
        mock_create_category.assert_called_with(1, "groceries")
        mock_create_category.assert_called_with(1, "spending")
        mock_create_category.assert_called_with(1, "paycheck")
        mock_create_category.assert_called_with(1, "savings")

    @patch('db.db_create_user')
    @patch('db.get_user')
    def test_create_user_failure(self, mock_get_user, mock_db_create_user):
        mock_db_create_user.side_effect = Exception("Database error")
        result = my_auth.create_user("testuser", "test@example.com", "password123")
        self.assertFalse(result)
        mock_db_create_user.assert_called_once_with("testuser", "test@example.com", "hashed_password")

    @patch('db.get_user')
    def test_login_user_success(self, mock_get_user):
        mock_get_user.return_value = {'id': 1, 'username': 'testuser', 'password_hash': 'hashed_password'}
        with patch('werkzeug.security.check_password_hash', return_value=True):
            result = my_auth.login_user("testuser", "password123")
        self.assertTrue(result)
        mock_get_user.assert_called_once_with("testuser")
    
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
    
    @patch('db.get_user')
    def test_login_user_from_form_success(self, mock_get_user):
        mock_get_user.return_value = {'id': 1, 'username': 'testuser', 'password_hash': 'hashed_password'}
        with patch('werkzeug.security.check_password_hash', return_value=True):
            result = my_auth.login_user_from_form("testuser", "password123")
        self.assertEqual(result, {'id': 1, 'username': 'testuser', 'password_hash': 'hashed_password'})
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
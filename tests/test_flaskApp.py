import unittest
from flask import session
from unittest.mock import patch
from flaskApp import app


class FlaskAppTests(unittest.TestCase):

    @patch('db_interface.find_events')
    @patch('db.get_categories_of_user')
    @patch('db.get_transactions_of_user')
    def test_landing_page_logged_in(self, mock_get_transactions, mock_get_categories, mock_find_events):
        # Mock return values for the patched methods
        mock_get_transactions.return_value = []
        mock_get_categories.return_value = []
        mock_find_events.return_value = []

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1  # Set session user_id
            response = client.get('/')
            self.assertEqual(response.status_code, 302)

    def test_landing_page_not_logged_in(self):
        with app.test_client() as client:
            response = client.get('/')
            self.assertEqual(response.status_code, 200)

    @patch('my_auth.create_user')
    def test_signup_success(self, mock_create_user):
        mock_create_user.return_value = True
        with app.test_client() as client:
            response = client.post('/signup/', data={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'password123'
            })
            self.assertEqual(response.status_code, 302)
            with client.session_transaction() as sess:
                self.assertIn('Sign up successful. You can now log in.', sess['_flashes'][0][1])

    @patch('my_auth.create_user')
    def test_signup_failure(self, mock_create_user):
        mock_create_user.return_value = False
        with app.test_client() as client:
            response = client.post('/signup/', data={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'password123'
            })
            self.assertEqual(response.status_code, 302)
            with client.session_transaction() as sess:
                self.assertIn('Sign up failed. Please try again', sess['_flashes'][0][1])

    @patch('my_auth.login_user_from_form')
    def test_login_success(self, mock_login_user):
        mock_login_user.return_value = {'id': 1, 'username': 'testuser'}
        with app.test_client() as client:
            response = client.post('/login/', data={
                'username': 'testuser',
                'password': 'password123'
            })
            self.assertEqual(response.status_code, 302)
            with client.session_transaction() as sess:
                self.assertEqual(sess['user_id'], 1)

    @patch('my_auth.login_user_from_form')
    def test_login_failure(self, mock_login_user):
        mock_login_user.return_value = None
        with app.test_client() as client:
            response = client.post('/login/', data={
                'username': 'testuser',
                'password': 'wrongpassword'
            })
            self.assertEqual(response.status_code, 302)
            with client.session_transaction() as sess:
                self.assertIn('Invalid username or password', sess['_flashes'][0][1])

    @patch('db_interface.find_events')
    def test_calendar_logged_in(self, mock_find_events):
        mock_find_events.return_value = []
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1
            response = client.get('/calendar/')
            self.assertEqual(response.status_code, 200)
            self.assertIn('<div class="calendar-wrapper">', response.data.decode())

    @patch('db_interface.find_events')
    def test_calendar_not_logged_in(self, mock_find_events):
        with app.test_client() as client:
            response = client.get('/calendar/')
            self.assertEqual(response.status_code, 302)

    @patch('flaskApp.db.get_categories_of_user')
    @patch('flaskApp.db.get_transactions_of_user')
    @patch('flaskApp.suggestions.get_budget_tips')
    def test_tips(self, mock_get_budget_tips, mock_get_transactions, mock_get_categories):
        # Set up mock return values
        mock_get_categories.return_value = [{'ID': 1, 'name': 'Rent'}]
        mock_get_transactions.return_value = [{
            'category_id': 1,
            'amount': '1000',
            'title': 'Rent',
            'expense': True
        }]
        mock_get_budget_tips.return_value = "Keep your rent within 30% of your income."
        
        # Simulate the client making a request while logged in
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1  # Mocking logged-in user
                
            response = client.get('/tips/')
            self.assertEqual(response.status_code, 200)
            self.assertIn('Keep your rent within 30% of your income.', response.data.decode())


    @patch('db.save_user_budget')
    def test_budget_update(self, mock_save_user_budget):
        mock_save_user_budget.return_value = True
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1
            response = client.post('/budget/', data={'total-budget': '5000'})
            self.assertEqual(response.status_code, 302)
            with client.session_transaction() as sess:
                self.assertIn('Your budget has been updated!', sess['_flashes'][0][1])

    def test_logout(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1
            response = client.get('/logout/')
            self.assertEqual(response.status_code, 302)
            with client.session_transaction() as sess:
                self.assertNotIn('user_id', sess)

    @patch('db_interface.add_transaction')
    def test_add_event(self, mock_add_transaction):

        mock_add_transaction.return_value = True
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1
            response = client.post('/add_event/', data={
                'name': 'Test Event',
                'description': 'This is a test',
                'amount': '100',
                'category': 'test_category',
                'type': 'expense',
                'date': '2025-05-01'
            })
            self.assertEqual(response.status_code, 302)
            with client.session_transaction() as sess:
                self.assertIn('Event added successfully!', sess['_flashes'][0][1])

if __name__ == '__main__':
    unittest.main()

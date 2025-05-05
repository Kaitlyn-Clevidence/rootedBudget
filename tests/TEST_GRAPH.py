import unittest
from unittest.mock import patch
from datetime import datetime
from bs4 import BeautifulSoup
import graph

class TestGenerateGraphs(unittest.TestCase):

    def _parse_html_and_check_div(self, html):
        """Helper function to parse HTML and check for <div> tags."""
        soup = BeautifulSoup(html, "html.parser")
        divs = soup.find_all("div")
        self.assertGreater(len(divs), 0)

    @patch('graph.db.get_category_name_by_id')
    @patch('graph.datetime')
    def test_generate_graphs(self, mock_datetime, mock_get_category_name_by_id):
        # Force current date to April 2025
        mock_datetime.now.return_value = datetime(2025, 4, 20)
        mock_datetime.strptime = datetime.strptime

        # Sample transaction data
        transaction_list = [
            {
                'created_at': '2025-04-10',
                'category_id': 1,
                'expense': True,
                'amount': 100.0,
                'title': 'Groceries',
                'user_id': 'user1'
            },
            {
                'created_at': '2025-04-15',
                'category_id': 2,
                'expense': True,
                'amount': 50.0,
                'title': 'Entertainment',
                'user_id': 'user1'
            },
            {
                'created_at': '2025-04-25',
                'category_id': 1,
                'expense': False,
                'amount': 200.0,
                'title': 'Salary',
                'user_id': 'user1'
            }
        ]

        mock_get_category_name_by_id.side_effect = lambda user_id, cat_id: {
            '1': "Groceries",
            '2': "Entertainment"
        }.get(str(cat_id), "Unknown")

        base_budget = 500.0

        pie_html, bar_html = graph.generate_graphs(transaction_list, base_budget)

        # Validate HTML via BeautifulSoup
        self._parse_html_and_check_div(pie_html)
        self._parse_html_and_check_div(bar_html)

        self.assertIn("Spending Breakdown", pie_html)
        self.assertIn("Budget vs. Actual Spending", bar_html)

    @patch('graph.datetime')
    def test_generate_graphs_empty(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2025, 4, 20)
        mock_datetime.strptime = datetime.strptime

        empty_transaction_list = []
        base_budget = 500.0

        pie_html, bar_html = graph.generate_graphs(empty_transaction_list, base_budget)

        self._parse_html_and_check_div(pie_html)
        self._parse_html_and_check_div(bar_html)

        self.assertIn("Spending Breakdown", pie_html)
        self.assertIn("Budget vs. Actual Spending", bar_html)

    @patch('graph.datetime')
    def test_generate_graphs_no_expenses(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2025, 4, 20)
        mock_datetime.strptime = datetime.strptime

        transaction_list = [
            {
                'created_at': '2025-04-10',
                'category_id': 1,
                'expense': False,
                'amount': 100.0,
                'title': 'Salary',
                'user_id': 'user1'
            },
            {
                'created_at': '2025-04-15',
                'category_id': 2,
                'expense': False,
                'amount': 200.0,
                'title': 'Salary',
                'user_id': 'user1'
            }
        ]
        base_budget = 500.0

        pie_html, bar_html = graph.generate_graphs(transaction_list, base_budget)

        self._parse_html_and_check_div(pie_html)
        self._parse_html_and_check_div(bar_html)

        self.assertIn("0.00", bar_html)

    @patch('graph.datetime')
    def test_generate_graphs_extra_income(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2025, 4, 20)
        mock_datetime.strptime = datetime.strptime

        transaction_list = [
            {
                'created_at': '2025-04-10',
                'category_id': 1,
                'expense': False,
                'amount': 600.0,
                'title': 'Salary',
                'user_id': 'user1'
            }
        ]
        base_budget = 500.0

        pie_html, bar_html = graph.generate_graphs(transaction_list, base_budget)

        self._parse_html_and_check_div(pie_html)
        self._parse_html_and_check_div(bar_html)

        self.assertIn("600.00", bar_html)

    def test_pastel_gradient(self):
        n = 5
        base_color = (0.87, 0.73, 0.66)
        gradient_colors = graph.pastel_gradient(n, base_color)

        self.assertEqual(len(gradient_colors), n)
        for color in gradient_colors:
            self.assertTrue(color.startswith("rgba(") and color.endswith(")"))

if __name__ == '__main__':
    unittest.main()
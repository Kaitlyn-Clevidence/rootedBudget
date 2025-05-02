import unittest
from unittest.mock import patch
from datetime import datetime

# Assuming the relevant functions and imports from your original code are already available
from your_module import generate_graphs, pastel_gradient


class TestGenerateGraphs(unittest.TestCase):

    @patch('your_module.db.get_category_name_by_id')
    def test_generate_graphs(self, mock_get_category_name_by_id):
        # Sample data for testing
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
        base_budget = 500.0

        # Mocking database function call
        mock_get_category_name_by_id.return_value = "Groceries" if '1' in str(mock_get_category_name_by_id.call_args[0]) else "Entertainment"

        # Call the function with the sample data
        pie_html, bar_html = generate_graphs(transaction_list, base_budget)

        # Test: Ensure that pie and bar charts are generated correctly
        self.assertIn("<div id=\"", pie_html)  # Check if the pie chart HTML has been generated
        self.assertIn("<div id=\"", bar_html)  # Check if the bar chart HTML has been generated

        # Test: Check if the mock data for category names are being used
        mock_get_category_name_by_id.assert_called()

        # Additional assertions can be done to check correct data in the charts
        # For example, testing for specific labels or values in the HTML (e.g., checking total income, total spent, etc.)
        self.assertIn("Spending Breakdown", pie_html)
        self.assertIn("Budget vs. Actual Spending", bar_html)
    
    def test_pastel_gradient(self):
        # Test pastel_gradient function for correct output format
        n = 5
        base_color = (0.87, 0.73, 0.66)
        gradient_colors = pastel_gradient(n, base_color)

        # Check that the gradient has the correct number of colors
        self.assertEqual(len(gradient_colors), n)

        # Check that each color is in RGBA format
        for color in gradient_colors:
            self.assertTrue(color.startswith("rgba(") and color.endswith(")"))

    def test_generate_graphs_empty(self):
        # Test with empty transaction list
        empty_transaction_list = []
        base_budget = 500.0

        pie_html, bar_html = generate_graphs(empty_transaction_list, base_budget)

        # Check that the pie and bar charts are still generated
        self.assertIn("<div id=\"", pie_html)
        self.assertIn("<div id=\"", bar_html)

        # Ensure that values reflect the empty transaction list
        self.assertIn('Budget vs. Actual Spending', bar_html)
        self.assertIn('Spending Breakdown', pie_html)

    def test_generate_graphs_no_expenses(self):
        # Test when no expenses exist in the transaction list
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

        pie_html, bar_html = generate_graphs(transaction_list, base_budget)

        # Check that the pie and bar charts are still generated
        self.assertIn("<div id=\"", pie_html)
        self.assertIn("<div id=\"", bar_html)

        # Check that the total spent is 0 in the bar chart
        self.assertIn('0.00', bar_html)

    def test_generate_graphs_extra_income(self):
        # Test when income exceeds the base budget
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

        pie_html, bar_html = generate_graphs(transaction_list, base_budget)

        # Check if the effective budget is set to total income
        self.assertIn('600.00', bar_html)  # Effective Budget will be equal to total income

if __name__ == '__main__':
    unittest.main()
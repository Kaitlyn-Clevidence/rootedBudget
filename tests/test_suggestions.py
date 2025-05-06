import unittest
from unittest.mock import patch
from suggestions import analyze_spending, get_budget_tips

class TestBudgetingFunctions(unittest.TestCase):
    def test_analyze_spending_good_budget(self):
        user_income = 4000
        user_rent = 1200
        user_food = 600
        user_spending = 400
        user_savings = 800
        expected = {
            "rent": "good",
            "food": "good",
            "spending": "good",
            "savings": "good",
        }
        result = analyze_spending(user_income, user_rent, user_food, user_spending, user_savings)
        self.assertEqual(result, expected)

    def test_analyze_spending_high_rent(self):
        user_income = 4000
        user_rent = 1500
        user_food = 600
        user_spending = 400
        user_savings = 800
        expected = {
            "rent": "too high",
            "food": "good",
            "spending": "good",
            "savings": "good",
        }
        result = analyze_spending(user_income, user_rent, user_food, user_spending, user_savings)
        self.assertEqual(result, expected)

    def test_analyze_spending_low_savings(self):
        user_income = 4000
        user_rent = 1200
        user_food = 600
        user_spending = 400
        user_savings = 300
        expected = {
            "rent": "good",
            "food": "good",
            "spending": "good",
            "savings": "too low",
        }
        result = analyze_spending(user_income, user_rent, user_food, user_spending, user_savings)
        self.assertEqual(result, expected)

    @patch('suggestions.genai.GenerativeModel.generate_content')
    def test_get_budget_tips(self, mock_generate_content):
        mock_generate_content.return_value = type('obj', (object,), {'text': "You should save more and reduce your entertainment spending."}) 
        user_income = 4000
        user_rent = 1200
        user_food = 600
        user_spending = 450
        user_savings = 500
        expected_output = "You should save more and reduce your entertainment spending."
        result = get_budget_tips(user_income, user_rent, user_food, user_spending, user_savings)
        self.assertEqual(result, expected_output)

    @patch('suggestions.genai.GenerativeModel.generate_content')
    def test_get_budget_tips_with_error(self, mock_generate_content):
        mock_generate_content.side_effect = Exception("API call failed")
        user_income = 4000
        user_rent = 1200
        user_food = 600
        user_spending = 450
        user_savings = 500
        expected_output = "Error generating response: API call failed"
        result = get_budget_tips(user_income, user_rent, user_food, user_spending, user_savings)        
        self.assertEqual(result, expected_output)

    def test_analyze_spending_exact_thresholds(self):
        user_income = 4000
        user_rent = 0.30 * user_income
        user_food = 0.15 * user_income
        user_spending = 0.10 * user_income
        user_savings = 0.20 * user_income
        expected = {
            "rent": "good",
            "food": "good",
            "spending": "good",
            "savings": "good",
        }
        result = analyze_spending(user_income, user_rent, user_food, user_spending, user_savings)
        self.assertEqual(result, expected)

    @patch('suggestions.genai.GenerativeModel.generate_content')
    def test_get_budget_tips_ideal_scenario(self, mock_generate_content):
        mock_generate_content.return_value = type('obj', (object,), {'text': "Your budgeting looks great!"})
        result = get_budget_tips(4000, 1200, 600, 400, 800)
        self.assertEqual(result, "Your budgeting looks great!")

if __name__ == '__main__':
    unittest.main()
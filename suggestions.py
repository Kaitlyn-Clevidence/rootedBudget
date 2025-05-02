import google.generativeai as genai

# Set API Key
API_KEY = "AIzaSyABMAcLWBV178zPub_j5LgJ0Jb253OPIKw"
genai.configure(api_key=API_KEY)

# Initialize the correct model
model = genai.GenerativeModel("gemini-2.0-flash")

# Define a database of recommended spending by category (as percentages of income)
category_recommendations = {
    "Rent": 0.30,  # Recommended 30% for housing (rent)
    "Food": 0.15,  # Recommended 15% for food
    "Spending": 0.10,  # Recommended 10% for entertainment
    "Savings": 0.20,  # Recommended 20% for savings
}

def get_budget_tips(income, rent, food, spending, savings):
    prompt = f"""
    You are a personal finance assistant. Based on the user's financial data, provide clear, actionable budgeting advice.

    **User's Financial Data:**
    - Income: ${income}
    - Rent: ${rent}
    - Food: ${food}
    - Spending: ${spending}
    - Savings: ${savings}

    Use best financial practices (e.g., 50/30/20 rule) to give tailored recommendations. Consider the following:
    - Rent should be around 30% of income
    - Food should be around 15% of income
    - Spending should be around 10% of income
    - Savings should be around 20% of income
    
    Please analyze the user's spending habits and suggest areas they can improve. Be concise with the advice.
    """

    try:
        response = model.generate_content(prompt)
        return response.text if hasattr(response, "text") else "Unexpected response format."
    
    except Exception as e:
        return f"Error generating response: {e}"

def analyze_spending(user_income, user_rent, user_food, user_spending, user_savings):
    # Calculate recommended amounts based on the 50/30/20 rule
    recommended_rent = user_income * category_recommendations["rent"]
    recommended_food = user_income * category_recommendations["food"]
    recommended_spending = user_income * category_recommendations["spending"]
    recommended_savings = user_income * category_recommendations["savings"]

    # Calculate overspending or underspending in each category
    rent_analysis = "good" if user_rent <= recommended_rent else "too high"
    food_analysis = "good" if user_food <= recommended_food else "too high"
    spending_analysis = "good" if user_spending <= recommended_spending else "too high"
    savings_analysis = "good" if user_savings >= recommended_savings else "too low"

    return {
        "rent": rent_analysis,
        "food": food_analysis,
        "spending": spending_analysis,
        "savings": savings_analysis,
    }

# Example usage
if __name__ == "__main__":
    user_income = 4000
    user_rent = 1600
    user_food = 700
    user_spending = 450
    user_savings = 500

    # Get spending analysis
    spending_analysis = analyze_spending(user_income, user_rent, user_food, user_spending, user_savings)

    print("Spending Analysis:")
    for category, analysis in spending_analysis.items():
        print(f"- {category}: {analysis}")

    # Get budgeting tips from Gemini model
    budget_tips = get_budget_tips(user_income, user_rent, user_food, user_spending, user_savings)
    print("\nBudgeting Tips:")
    print(budget_tips)

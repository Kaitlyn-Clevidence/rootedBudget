import re
import google.generativeai as genai

API_KEY = "AIzaSyABMAcLWBV178zPub_j5LgJ0Jb253OPIKw"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def clean_text(text):
    """Removes all Markdown-style formatting, including asterisks for bold and italic."""
    # Remove all Markdown-style bold and italic (i.e., ** or * wrapped content)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove **bold**
    text = re.sub(r'\*(.*?)\*', r'\1', text)  # Remove *italic*

    return text

def format_budget_output(income, rent, food, spending, savings):
    formatted_output = """
    ### Tips
    
    #### Current Budget Analysis
    Your current budget allocates resources as follows:
    
    - **Rent**:\t{}% of income
    - **Food**:\t{}% of income
    - **Spending**:\t{}% of income
    - **Savings**:\t{}% of income
    
    Generally, a healthy budget aims for the following:
    
    - **Rent/Housing**:\t30% or less
    - **Food**:\t15% or less
    - **Spending (Discretionary)**:\t10-15%
    - **Savings/Debt Repayment**:\t20% or more
    
    **Observations**:
    - Your **rent** is significantly higher than the recommended guideline.
    - Your **food** expenses are slightly above the ideal range.
    - Your **spending** is within a reasonable range.
    - While **saving** is a good habit, your savings percentage could be improved.
    
    #### Recommendations
    Here are some specific suggestions to optimize each area of your budget:
    
    - **Rent**:
      - **Explore alternative housing**: This is the most significant area for potential improvement. Consider moving to a more affordable apartment, finding a roommate, or exploring neighborhoods with lower rental costs.
      - **Negotiate your rent**: Research comparable rental rates in your area and politely attempt to negotiate with your landlord. This is less likely to work, but it's worth a try.
    
    - **Food**:
      - **Meal Planning**: Plan your meals for the week in advance to avoid impulse purchases and food waste.
      - **Cook at Home**: Eating out is a major budget drain. Increase the frequency of cooking at home.
      - **Grocery Shopping Strategically**: Use coupons, compare prices at different stores, buy in bulk when appropriate, and avoid shopping when hungry. Consider generic brands.
      - **Reduce Food Waste**: Store food properly and use leftovers creatively.
    
    - **Spending**:
      - **Track Your Spending**: For a month, meticulously track every dollar you spend. This will reveal where your money is actually going and identify areas where you can cut back. Use a budgeting app, spreadsheet, or notebook.
      - **Identify Needs vs. Wants**: Distinguish between essential spending and discretionary spending. Prioritize needs and consciously reduce wants.
      - **Implement a "30-Day Rule"**: Before making any non-essential purchase, wait 30 days. This helps you avoid impulse buys.
      - **Find Free or Low-Cost Entertainment**: Explore free events in your community, utilize library resources, and pursue hobbies that don't require significant spending.
    
    - **Savings**:
      - **Automate Savings**: Set up automatic transfers from your checking account to your savings account each month. This makes saving effortless.
      - **Increase Savings Incrementally**: Even small increases in your savings rate can make a big difference over time. Aim to increase your savings by 1% each month until you reach your target.
      - **Set Specific Savings Goals**: Having clear goals (e.g., emergency fund, down payment on a house) can motivate you to save more.
    
    #### Revised Budget Goal
    Here's a possible revised budget breakdown based on the recommendations:
    
    - **Rent**:\t$1200 (30%) - Requires a housing change to be achievable
    - **Food**:\t$600 (15%)
    - **Spending**:\t$400 (10%)
    - **Savings**:\t$800 (20%)
    - **Remaining**:\t$100 (5%) - This can be allocated to unexpected expenses, debt repayment, or further increased savings.
    
    #### Key Takeaway
    **Prioritize reducing your rent expense by exploring alternative housing options** to free up a substantial portion of your income for savings and other financial goals.
    """.format(rent, food, spending, savings)

    # Clean up the text (remove any stray Markdown, asterisks, etc.)
    formatted_output = clean_text(formatted_output)

    return formatted_output


def get_budget_tips(income, rent, food, spending, savings):
    prompt = f"""
    You are a financial assistant. Based on the user's financial data, provide budgeting advice in a structured format.

    **User's Financial Data:**
    - Income: ${income}
    - Rent: ${rent}
    - Food: ${food}
    - Spending: ${spending}
    - Savings: ${savings}

    Structure the response with clear section headers:
    
    **Current Budget Analysis:**  
    Explain how the user's budget compares to financial best practices.  

    **Recommendations:**  
    Provide specific, practical tips for optimizing rent, food, spending, and savings.  

    **Revised Budget Goal:**  
    Suggest an improved budget breakdown (Rent, Food, Spending, Savings).  

    **Key Takeaway:**  
    Summarize the most important action item in a single sentence.  
    """

    try:
        # Generate response using the AI model
        response = model.generate_content(prompt)

        if hasattr(response, "text"):
            response_text = response.text.strip()
        elif hasattr(response, "candidates"):
            response_text = response.candidates[0].content.strip()
        else:
            return {"error": "Unexpected response format from API."}

        # Clean the generated response to remove * and ** completely
        response_text = clean_text(response_text)

        lines = response_text.split('\n')
        tips_data = {
            "income": income,
            "rent": rent,
            "food": food,
            "spending": spending,
            "savings": savings,
            "analysis": "",
            "recommendations": "",
            "revised_budget": "",
            "key_takeaway": ""
        }

        current_section = None
        for line in lines:
            line = line.strip()
            if not line or line.startswith("*"):  # Remove bullet points
                line = re.sub(r"^\*+", "", line).strip()

            # Detect section headers
            if "Current Budget Analysis" in line:
                current_section = "analysis"
                continue
            elif "Recommendations" in line:
                current_section = "recommendations"
                continue
            elif "Revised Budget Goal" in line:
                current_section = "revised_budget"
                continue
            elif "Key Takeaway" in line:
                current_section = "key_takeaway"
                continue

            if current_section:
                tips_data[current_section] += line + " "

        return tips_data

    except Exception as e:
        return {"error": f"Error generating response: {e}"}

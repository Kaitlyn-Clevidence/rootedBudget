from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import my_auth
import db_interface
import db
import suggestions
import markdown

#from werkzeug.security import check_password_hash, generate_password_hash
#from functools import wraps
from datetime import datetime, timedelta
from collections import namedtuple
#import numpy as np
import graph
from calendar import monthrange
#from http import HTTPStatus

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route("/")
def landing():
    if 'user_id' in session:
        return redirect(url_for("personalView"))
    return render_template("landingPage.html")

@app.route("/signup/", methods=["POST"])
def sign_up():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if not username or not email or not password:
        flash("Please fill out all fields.", "signup_error")
        return redirect(url_for("landing"))

    success = my_auth.create_user(username, email, password)
    if(success):
        flash("Sign up successful. You can now log in.", "signup_success")
    else:
        flash("Sign up failed. Please try again", "signup_error")
    return redirect(url_for("landing"))

@app.route("/login/", methods=["POST"])
def login():
    identifier = request.form.get("username") or request.form.get("email")
    password = request.form.get("password")

    user = my_auth.login_user_from_form(identifier, password)

    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect(url_for("personalView"))

    flash("Invalid username or password", "login_error")
    return redirect(url_for("landing"))

# Temporary structure for events
Event = namedtuple('Event', ['date', 'amount', 'description', 'type'])

@app.route("/calendar/")
def calendar():
    if 'user_id' not in session:
        return redirect(url_for("landing"))
    user_id = session['user_id']
    month_offset = int(request.args.get('month_offset', 0))
    today = datetime.today()
    
    # Shift month by offset
    shifted_month = today.replace(day=1) + timedelta(days=month_offset * 30)
    year = shifted_month.year
    month = shifted_month.month

    first_day_of_month = datetime(year, month, 1)
    days_in_month = monthrange(year, month)[1]

    # Get all transactions
    events = db_interface.find_events(user_id)
    print(events)
    return render_template(
        "calendar.html",
        current_month=first_day_of_month.strftime("%B"),
        current_year=year,
        month_offset=month_offset,
        first_day_of_month=first_day_of_month,
        days_in_month=days_in_month,
        events=events
    )

@app.template_filter('markdown')
def markdown_filter(text):
    return markdown.markdown(text, extensions=['nl2br'])

@app.route("/tips/")
def tips():
    if 'user_id' not in session:
        return redirect(url_for("landing"))
    
    category_dict = {}
    translation_dict = {}   # key is category ID, value is category name
    subcategories = []
    categories = db.get_categories_of_user(session['user_id'])
    transactions = db.get_transactions_of_user(session['user_id'])

    for c in categories:
        category_id = c['ID']
        category_dict[category_id] = []

    for transaction in transactions:
        category_id = int(transaction['category_id'])

        try:
            category_dict[category_id].append(transaction)
        except KeyError:
            category_dict[category_id] = [transaction]

        if transaction['title'] not in subcategories:
            subcategories.append(transaction['title'])

        for category_id in category_dict.keys():
            user_id = session.get('user_id')
            category_name = db.get_category_name_by_id(user_id, category_id)
            translation_dict[category_name] = category_id

    print(translation_dict)
    print(category_dict)

    # for x in category_dict.values():
    #     if x:
    #         print(x[0]['title'], x[0]['amount'])
    

    def sum_expenses(category_name):
        if category_name not in translation_dict:
            return 0.0  # Handle missing category gracefully
        
        expenses_transactions = category_dict[translation_dict[category_name]]
        expenses = 0.0
        for x in expenses_transactions:
            value = float(x['amount'])
            print(x['title'], value)
            if(bool(x['expense'])):
                expenses += value
            else:
                expenses -= value
        return expenses
    
    if 'paycheck' in translation_dict:
        user_income = -1 * sum_expenses('paycheck')
    else:
        user_income = 0  # Default to 0 if 'paycheck' is not found
        user_rent = sum_expenses('rent')
    user_food = sum_expenses('groceries')
    user_spending = sum_expenses('spending')
    user_savings = sum_expenses('savings')


    budget_tips = suggestions.get_budget_tips(user_income, user_rent, user_food, user_spending, user_savings)
    

    return render_template("tips.html", budget_tips=budget_tips)

@app.route('/budget/', methods=['GET', 'POST'])
def budget():
    if 'user_id' not in session:
        return redirect(url_for("landing"))

    total_budget = db.get_user_budget(session['user_id'])

    if request.method == "POST":
        total_budget = request.form.get("total-budget")
        db.save_user_budget(session['user_id'], total_budget)
        flash("Your budget has been updated!", "success")
        return redirect(url_for("budget"))
    return render_template("budget.html", total_budget=total_budget)

@app.route("/logout/")
def logout():
    if 'user_id' not in session:
        return redirect(url_for("landing"))
    session.clear()
    return redirect(url_for("landing"))

@app.route("/dashboard/")
def personalView():
    if 'user_id' not in session:
        return redirect(url_for("landing"))
    
    username = session['username']
    transaction_list = db.get_transactions_of_user(session['user_id'])
    events = db_interface.find_events(session['user_id'])  # This contains recent events
    total_budget = db.get_user_budget(session['user_id'])
    pie_html, bar_html = graph.generate_graphs(transaction_list, total_budget)
    return render_template("dashboard.html", username=username, pie_html=pie_html, bar_html=bar_html, recent_events=events)

@app.route("/add_event/", methods=["POST"])
def add_event():
    if 'user_id' not in session:
        return redirect(url_for("landing"))

    name = request.form.get("name").lower()
    description = request.form.get("description").lower()
    amount = float(request.form.get("amount"))
    category = request.form.get("category").lower()
    new_category = request.form.get("newCategory")
    if new_category:
        new_category = new_category.lower()

    final_category = None
    user_id = session['user_id']
    if category == "__new__" and new_category:
        success = db_interface.add_category(user_id, new_category)
        if success:
            final_category = new_category
        else:
            flash("Failed to add new category", "event_error")
    else:
        final_category = category


    # Use new category if selected
    # final_category = new_category if category == "__new__" and new_category else category

    event_type = request.form.get("type")
    expense_bool = event_type.lower() == "expense"

    date_str = request.form.get("date")
    print(date_str)
    recurring = 'recurring' in request.form

    print(f"[NEW EVENT] {name} | ${amount} | {final_category} | {event_type} | {date_str} | Recurring: {recurring}")

    success = db_interface.add_transaction(user_id, name, description, final_category, amount, recurring, expense_bool, date_str)

    if success:
        flash("Event added successfully!", "event_success")
        #return redirect(url_for("personalView"))
    else:
        flash("Failed to add event", "event_error")

    recurrence_type = request.form.get("recurrence_type")
    custom_days = request.form.get("custom_days", "")

    original_date = datetime.strptime(date_str, "%Y-%m-%d")
    events_to_add = [Event(original_date, amount, description, event_type)]

    # Generate future recurring events
    if recurring:
        for i in range(1, 6):  # Create 6 recurrences for now
            if recurrence_type == "weekly":
                next_date = original_date + timedelta(weeks=i)
                events_to_add.append(Event(next_date, amount, description, event_type))
            elif recurrence_type == "biweekly":
                next_date = original_date + timedelta(weeks=i * 2)
                events_to_add.append(Event(next_date, amount, description, event_type))
            elif recurrence_type == "monthly":
                next_month = original_date.month + i
                year = original_date.year + (next_month - 1) // 12
                month = (next_month - 1) % 12 + 1
                try:
                    next_date = original_date.replace(year=year, month=month)
                except ValueError:
                    next_date = original_date.replace(year=year, month=month, day=28)  # Safe fallback
                events_to_add.append(Event(next_date, amount, description, event_type))
            elif recurrence_type == "custom_days":
                days = [int(d.strip()) for d in custom_days.split(",") if d.strip().isdigit()]
                for m in range(1, 4):  # Next 3 months
                    for d in days:
                        try:
                            next_date = original_date.replace(month=original_date.month + m, day=d)
                            events_to_add.append(Event(next_date, amount, description, event_type))
                        except ValueError:
                            continue

    for ev in events_to_add[1:]:  # Skip the first, already added event
        success = db_interface.add_transaction(
            user_id,
            name,
            ev.description,
            final_category,
            ev.amount,
            True,
            expense_bool,
            ev.date.strftime("%Y-%m-%d")
        )
        if not success:
            print(f"[ERROR] Failed to add recurring event: {ev}")

    flash("Event(s) added successfully!", "event_success")
    
    return redirect(url_for('personalView'))

@app.teardown_appcontext
def teardown_db(exception):
    db.close_connection()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000, debug=True)
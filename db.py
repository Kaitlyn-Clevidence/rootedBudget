import sqlite3

DATABASE_PATH = "database.db"

def init_tables():
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()

    create_users_table = """CREATE TABLE IF NOT EXISTS users (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,  -- Fixed typo
        created_at TEXT DEFAULT (DATETIME('now')),
        last_login TEXT,
        budget FLOAT DEFAULT 0.0
    );"""

    create_transactions_table = """CREATE TABLE IF NOT EXISTS transactions (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        recurring BOOLEAN DEFAULT 0,
        created_at TEXT DEFAULT (DATETIME('now')),
        user_id INTEGER NOT NULL,
        expense BOOLEAN NOT NULL,
        FOREIGN KEY(category_id) REFERENCES categories(ID),
        FOREIGN KEY(user_id) REFERENCES users(ID)
    );"""

    create_categories_table = """CREATE TABLE IF NOT EXISTS categories (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(ID),
        UNIQUE(user_id, name)
    );"""

    cur.execute(create_users_table)
    cur.execute(create_transactions_table)
    cur.execute(create_categories_table)
    con.commit()  # Commit changes after creating the tables
    con.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Reusable function to close connections after query execution
def close_connection(conn):
    conn.commit()
    conn.close()

def db_create_user(username: str, email: str, hashed_password: str):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, email, password_hash) VALUES(?,?,?)", (username, email, hashed_password))
    except sqlite3.IntegrityError as e:
        print("Error: ", e)  # Handle integrity errors (like unique constraint violation)
    close_connection(conn)

def get_user(identifier: str):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ? OR ID = ?', (identifier, identifier, identifier)).fetchone()
    close_connection(conn)
    return user

def create_transaction(user_id, title: str, description: str, category_id: int, amount: float, recurring: bool, expense: bool, input_date):
    title = title.lower()
    conn = get_db_connection()
    conn.execute("INSERT INTO transactions(title, description, category_id, amount, recurring, user_id, expense, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                 (title, description, category_id, amount, recurring, user_id, expense, input_date))
    close_connection(conn)

def create_category(user_id, category_name: str):
    category_name = category_name.lower()
    conn = get_db_connection()
    conn.execute("INSERT INTO categories(name, user_id) VALUES (?, ?)", (category_name, user_id))
    close_connection(conn)
    return True

def get_transactions_of_user(user_id):
    conn = get_db_connection()
    transactions = conn.execute("SELECT * FROM transactions t JOIN users u ON t.user_id = u.id WHERE u.id = ?", (user_id,)).fetchall()
    close_connection(conn)
    return transactions

def get_categories_of_user(user_id):
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories c JOIN users u ON c.user_id = u.id WHERE u.id = ?", (user_id,)).fetchall()
    close_connection(conn)
    return categories

def get_category_id_by_name(user_id, category_name: str):
    conn = get_db_connection()
    category_id = conn.execute("SELECT c.id FROM categories c JOIN users u ON c.user_id = u.id WHERE u.id = ? AND c.name = ?", (user_id, category_name)).fetchone()
    close_connection(conn)
    return category_id['id'] if category_id else None

def get_category_name_by_id(user_id, category_id: str):
    conn = get_db_connection()
    category = conn.execute("SELECT c.name FROM categories c JOIN users u ON c.user_id = u.id WHERE u.id = ? AND c.id = ?", (user_id, category_id)).fetchone()
    close_connection(conn)
    return category['name'] if category else None

def save_user_budget(user_id, total_budget):
    conn = get_db_connection()
    conn.execute("UPDATE users SET budget = ? WHERE ID = ?", (total_budget, user_id))
    close_connection(conn)

def get_user_budget(user_id):
    conn = get_db_connection()
    budget_query = "SELECT budget FROM users WHERE ID = ?"
    budget_result = conn.execute(budget_query, (user_id,)).fetchone()
    close_connection(conn)
    return budget_result[0] if budget_result else 0.0

if __name__ == "__main__":
    init_tables()
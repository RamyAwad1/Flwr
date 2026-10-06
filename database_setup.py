import sqlite3

def setup_database():
    # Connect to SQLite (this automatically creates 'store_database.db' in your folder)
    conn = sqlite3.connect('store_database.db')
    cursor = conn.cursor()

    # 1. Users Table (Admin vs Worker)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')

    # 2. Products Table (Barcode is optional TEXT, cost_price is standard)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT, 
        name TEXT NOT NULL,
        quantity_in_stock INTEGER NOT NULL,
        cost_price REAL NOT NULL,
        sell_price REAL NOT NULL
    )
    ''')

    # 3. Customers Table (For handling debt)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone_number TEXT,
        total_debt REAL DEFAULT 0.0
    )
    ''')

    # 4. Sales Table (The overarching transaction)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        total_amount REAL NOT NULL,
        user_id INTEGER,
        customer_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    )
    ''')

    # 5. Sale_Items Table (The individual wires/parts on the receipt)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER,
        product_id INTEGER,
        quantity_sold INTEGER NOT NULL,
        price_at_time_of_sale REAL NOT NULL,
        FOREIGN KEY(sale_id) REFERENCES sales(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    ''')

    # Save changes and close
    conn.commit()
    conn.close()
    print("Success! 'store_database.db' has been created with all 5 tables.")

if __name__ == '__main__':
    setup_database()
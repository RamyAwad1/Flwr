import sqlite3

def add_test_stock():
    conn = sqlite3.connect('store_database.db')
    cursor = conn.cursor()
    
    # Adding a few dummy electric parts
    products = [
        ("1001", "Copper Wire 2mm", 50, 0.50, 1.25), # Barcode, Name, Stock, Cost, Sell Price
        ("1002", "10A Fuse", 200, 0.10, 0.50),
        ("1003", "LED Bulb 9W", 30, 1.50, 3.00),
        (None, "Electrical Tape (Black)", 100, 0.20, 1.00) # No barcode example
    ]
    
    cursor.executemany("""
        INSERT INTO products (barcode, name, quantity_in_stock, cost_price, sell_price)
        VALUES (?, ?, ?, ?, ?)
    """, products)
    
    conn.commit()
    conn.close()
    print("Test products added to the storage room!")

if __name__ == '__main__':
    add_test_stock()
import sqlite3
import hashlib

def create_admin():
    conn = sqlite3.connect('store_database.db')
    cursor = conn.cursor()

    username = "Ramy"
    password = "Secret.173" 
    
    # We scramble (hash) the password so it isn't saved as plain text
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                       (username, hashed_password, "Admin"))
        conn.commit()
        print(f"Success! User '{username}' created with password '{password}'.")
    except sqlite3.IntegrityError:
        print("Admin user already exists in the database!")
        
    conn.close()

if __name__ == '__main__':
    create_admin()
import sqlite3

# Create a new SQLite database
conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

# Create a table to store user data with role column
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')

# Create a table to store product data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        image_path TEXT,  -- Change 'image_url' to 'image_path'
        shopper_id INTEGER,
        FOREIGN KEY (shopper_id) REFERENCES users(id)
    )
''')

# Insert the default users with roles
cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('shopper', 'admin', 'Shopper'))
cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('client', 'admin', 'Client'))

# Commit the changes and close the connection
conn.commit()
conn.close()

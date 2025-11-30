import sqlite3
import os

# Create data directory if it doesn't exist
os.makedirs("telecom_assistant/data", exist_ok=True)

# Connect to database (creates it if it doesn't exist)
conn = sqlite3.connect("telecom_assistant/data/telecom.db")
cursor = conn.cursor()

# Create dummy tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id TEXT PRIMARY KEY,
    name TEXT,
    plan TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS billing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT,
    amount REAL,
    date TEXT,
    description TEXT
)
''')

# Insert dummy data
cursor.execute("INSERT OR IGNORE INTO customers (id, name, plan) VALUES ('CUST123', 'John Doe', 'Premium Plan')")
cursor.execute("INSERT OR IGNORE INTO billing (customer_id, amount, date, description) VALUES ('CUST123', 120.50, '2023-10-01', 'Monthly Service Charge')")
cursor.execute("INSERT OR IGNORE INTO billing (customer_id, amount, date, description) VALUES ('CUST123', 15.00, '2023-10-05', 'International Call')")

conn.commit()
conn.close()

print("Database created successfully.")

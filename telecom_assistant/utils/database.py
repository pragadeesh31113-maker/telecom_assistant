import sqlite3
import os
from langchain_community.utilities import SQLDatabase
from config.config import DB_PATH

def get_db_connection():
    """Get a connection to the SQLite database"""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    return sqlite3.connect(DB_PATH)

def get_sql_database():
    """Get a LangChain SQLDatabase instance"""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    return SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

def init_db():
    """Initialize the database with schema and sample data if it doesn't exist"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        plan_id TEXT,
        phone_number TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS plans (
        id TEXT PRIMARY KEY,
        name TEXT,
        price REAL,
        data_limit_gb INTEGER,
        voice_limit_min INTEGER,
        sms_limit INTEGER,
        description TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS billing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        amount REAL,
        date TEXT,
        description TEXT,
        status TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        month TEXT,
        data_used_gb REAL,
        voice_used_min INTEGER,
        sms_used INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS network_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT,
        status TEXT,
        incident_details TEXT,
        updated_at TEXT
    )
    ''')
    
    # Insert sample data if empty
    cursor.execute("SELECT count(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        # Plans
        cursor.execute("INSERT INTO plans VALUES ('STD_500', 'Standard Plan', 49.99, 10, 500, 1000, 'Basic plan for light users')")
        cursor.execute("INSERT INTO plans VALUES ('PRM_1000', 'Premium Plan', 89.99, 50, 9999, 9999, 'Unlimited plan for power users')")
        cursor.execute("INSERT INTO plans VALUES ('FAM_SHARE', 'Family Share Plus', 120.00, 100, 9999, 9999, 'Shared plan for families')")
        
        # Customers
        cursor.execute("INSERT INTO customers VALUES ('CUST001', 'Rahul Sharma', 'rahul@example.com', 'STD_500', '9876543210')")
        cursor.execute("INSERT INTO customers VALUES ('CUST002', 'Priya Patel', 'priya@example.com', 'PRM_1000', '9876543211')")
        
        # Billing
        cursor.execute("INSERT INTO billing (customer_id, amount, date, description, status) VALUES ('CUST001', 49.99, '2023-05-01', 'Monthly Subscription', 'Paid')")
        cursor.execute("INSERT INTO billing (customer_id, amount, date, description, status) VALUES ('CUST001', 64.99, '2023-06-01', 'Monthly Subscription + Roaming', 'Due')")
        
        # Usage
        cursor.execute("INSERT INTO usage (customer_id, month, data_used_gb, voice_used_min, sms_used) VALUES ('CUST001', '2023-05', 8.5, 320, 45)")
        cursor.execute("INSERT INTO usage (customer_id, month, data_used_gb, voice_used_min, sms_used) VALUES ('CUST001', '2023-06', 12.2, 410, 60)")
        
        # Network Status
        cursor.execute("INSERT INTO network_status (region, status, incident_details, updated_at) VALUES ('Mumbai', 'Normal', NULL, '2023-06-20 10:00:00')")
        cursor.execute("INSERT INTO network_status (region, status, incident_details, updated_at) VALUES ('Delhi', 'Maintenance', 'Scheduled maintenance in South Delhi', '2023-06-20 10:00:00')")
        
        conn.commit()
        print("Database initialized with sample data.")
    
    conn.close()

if __name__ == "__main__":
    init_db()

import sqlite3
import os

# Define path relative to the script execution
DB_PATH = os.path.join(os.getcwd(), 'telecom_assistant', 'data', 'telecom.db')

def populate_db():
    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop existing tables
    print("Dropping existing tables...")
    cursor.execute("DROP TABLE IF EXISTS customers")
    cursor.execute("DROP TABLE IF EXISTS plans")
    cursor.execute("DROP TABLE IF EXISTS billing")
    cursor.execute("DROP TABLE IF EXISTS usage")
    cursor.execute("DROP TABLE IF EXISTS network_status")

    # Recreate tables with correct schema
    print("Creating tables...")
    cursor.execute('''
    CREATE TABLE customers (
        id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        plan_id TEXT,
        phone_number TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE plans (
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
    CREATE TABLE billing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        amount REAL,
        date TEXT,
        description TEXT,
        status TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        month TEXT,
        data_used_gb REAL,
        voice_used_min INTEGER,
        sms_used INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE network_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT,
        status TEXT,
        incident_details TEXT,
        updated_at TEXT
    )
    ''')

    # --- PLANS ---
    print("Inserting Plans...")
    plans = [
        ('STD_500', 'Standard Plan', 49.99, 10, 500, 1000, 'Basic plan for light users. 10GB Data, 500 Mins.'),
        ('PRM_1000', 'Premium Plan', 89.99, 50, 9999, 9999, 'Unlimited plan for power users. 50GB Data, Unlimited Calls.'),
        ('FAM_SHARE', 'Family Share Plus', 120.00, 100, 9999, 9999, 'Shared plan for families. 100GB Data, Unlimited Calls.'),
        ('INT_ROAM', 'Global Traveler', 150.00, 30, 2000, 5000, 'Plan for frequent travelers. 30GB Data, Free Roaming.')
    ]
    cursor.executemany("INSERT INTO plans VALUES (?, ?, ?, ?, ?, ?, ?)", plans)

    # --- CUSTOMERS ---
    print("Inserting Customers...")
    customers = [
        ('CUST001', 'Rahul Sharma', 'rahul@example.com', 'STD_500', '9876543210'),
        ('CUST002', 'Priya Patel', 'priya@example.com', 'PRM_1000', '9876543211'),
        ('CUST003', 'Amit Singh', 'amit@example.com', 'INT_ROAM', '9876543212')
    ]
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", customers)

    # --- BILLING & USAGE HISTORY ---
    print("Inserting Billing and Usage History...")
    
    # CUST001: Rahul (Standard Plan) - Consistently exceeds data limit
    billing_cust1 = [
        ('CUST001', 49.99, '2023-01-01', 'Monthly Subscription', 'Paid'),
        ('CUST001', 55.00, '2023-02-01', 'Monthly Subscription + Data Overage (1GB)', 'Paid'),
        ('CUST001', 65.00, '2023-03-01', 'Monthly Subscription + Data Overage (3GB)', 'Paid'),
        ('CUST001', 75.00, '2023-04-01', 'Monthly Subscription + Data Overage (5GB)', 'Paid'),
        ('CUST001', 80.00, '2023-05-01', 'Monthly Subscription + Data Overage (6GB)', 'Due')
    ]
    usage_cust1 = [
        ('CUST001', '2023-01', 9.5, 400, 50),
        ('CUST001', '2023-02', 11.0, 450, 60),
        ('CUST001', '2023-03', 13.0, 480, 70),
        ('CUST001', '2023-04', 15.0, 500, 80),
        ('CUST001', '2023-05', 16.0, 520, 90)
    ]

    # CUST002: Priya (Premium Plan) - Underutilizes plan (Candidate for downgrade)
    billing_cust2 = [
        ('CUST002', 89.99, '2023-01-01', 'Monthly Subscription', 'Paid'),
        ('CUST002', 89.99, '2023-02-01', 'Monthly Subscription', 'Paid'),
        ('CUST002', 89.99, '2023-03-01', 'Monthly Subscription', 'Paid'),
        ('CUST002', 89.99, '2023-04-01', 'Monthly Subscription', 'Paid'),
        ('CUST002', 89.99, '2023-05-01', 'Monthly Subscription', 'Due')
    ]
    usage_cust2 = [
        ('CUST002', '2023-01', 5.0, 100, 10),
        ('CUST002', '2023-02', 4.5, 120, 15),
        ('CUST002', '2023-03', 6.0, 110, 12),
        ('CUST002', '2023-04', 5.5, 130, 20),
        ('CUST002', '2023-05', 5.0, 100, 10)
    ]

    # CUST003: Amit (Traveler) - High Roaming
    billing_cust3 = [
        ('CUST003', 150.00, '2023-01-01', 'Monthly Subscription', 'Paid'),
        ('CUST003', 200.00, '2023-02-01', 'Monthly Subscription + Extra Roaming Data', 'Paid'),
        ('CUST003', 150.00, '2023-03-01', 'Monthly Subscription', 'Paid')
    ]
    usage_cust3 = [
        ('CUST003', '2023-01', 20.0, 500, 100),
        ('CUST003', '2023-02', 35.0, 800, 200),
        ('CUST003', '2023-03', 25.0, 600, 150)
    ]

    cursor.executemany("INSERT INTO billing (customer_id, amount, date, description, status) VALUES (?, ?, ?, ?, ?)", billing_cust1 + billing_cust2 + billing_cust3)
    cursor.executemany("INSERT INTO usage (customer_id, month, data_used_gb, voice_used_min, sms_used) VALUES (?, ?, ?, ?, ?)", usage_cust1 + usage_cust2 + usage_cust3)

    # --- NETWORK STATUS ---
    print("Inserting Network Status...")
    network_status = [
        ('Mumbai', 'Normal', None, '2023-06-20 10:00:00'),
        ('Delhi', 'Maintenance', 'Scheduled 5G upgrades in Central Delhi', '2023-06-20 10:00:00'),
        ('Bangalore', 'Outage', 'Fiber cut reported in Whitefield area', '2023-06-20 09:30:00'),
        ('Chennai', 'Normal', None, '2023-06-20 10:00:00')
    ]
    cursor.executemany("INSERT INTO network_status (region, status, incident_details, updated_at) VALUES (?, ?, ?, ?)", network_status)

    conn.commit()
    conn.close()
    print("✅ Database successfully populated with realistic sample data!")

if __name__ == "__main__":
    populate_db()

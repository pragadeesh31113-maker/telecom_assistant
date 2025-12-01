import os
import sys
import sqlite3

# Add project root to path
sys.path.append(os.getcwd())

try:
    from telecom_assistant.config.config import DB_PATH
    print(f"Checking database at: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("❌ Database file not found.")
        sys.exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables found:", [t[0] for t in tables])
    
    # Check network_incidents
    if ('network_incidents',) in tables:
        print("✅ 'network_incidents' table exists.")
        cursor.execute("SELECT count(*) FROM network_incidents")
        count = cursor.fetchone()[0]
        print(f"Row count: {count}")
    else:
        print("❌ 'network_incidents' table MISSING.")
        
    conn.close()

except Exception as e:
    print(f"Error: {e}")

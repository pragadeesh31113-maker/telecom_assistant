import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

# Simulate .env loading (if python-dotenv is used in config)
# But config.py likely uses os.environ directly.
# Let's check if the env var is set in this process
print(f"TELECOM_DB_PATH env var: {os.environ.get('TELECOM_DB_PATH')}")

try:
    from telecom_assistant.config.config import DB_PATH
    print(f"Resolved DB_PATH: {DB_PATH}")
    
    if os.path.exists(DB_PATH):
        print("✅ Database file exists at this path.")
    else:
        print("❌ Database file NOT found at this path.")
        
except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"Error: {e}")

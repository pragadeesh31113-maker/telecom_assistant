import hashlib
import sqlite3
import os
from telecom_assistant.config.config import DB_PATH
from telecom_assistant.utils.database import init_user_db

def hash_password(password):
    """Hash a password using SHA-256 (for demonstration)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    return hash_password(password) == hashed_password

def authenticate_user(username, password):
    """Authenticate a user and return their details"""
    init_user_db() # Ensure table exists
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, password_hash, role, customer_id FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        stored_hash = user[2]
        if verify_password(password, stored_hash):
            return {
                "id": user[0],
                "username": user[1],
                "role": user[3],
                "customer_id": user[4]
            }
    return None

def create_user(username, password, role="Customer", customer_id=None):
    """Create a new user"""
    init_user_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, customer_id) VALUES (?, ?, ?, ?)",
            (username, password_hash, role, customer_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Username exists
    finally:
        conn.close()

def seed_users():
    """Seed default users if they don't exist"""
    init_user_db()
    
    # Admin
    if not authenticate_user("admin", "admin123"):
        create_user("admin", "admin123", "Admin")
        print("Seeded admin user.")
        
    # Customer
    if not authenticate_user("rahul", "password123"):
        create_user("rahul", "password123", "Customer", "CUST001")
        print("Seeded customer user (rahul).")

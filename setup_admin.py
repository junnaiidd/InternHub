#!/usr/bin/env python3
"""
setup_admin.py
Run this ONCE after importing database.sql to set the correct admin password hash.
This script updates the admin account with a properly generated bcrypt hash.

Usage:
    python setup_admin.py
"""

import mysql.connector
from werkzeug.security import generate_password_hash

# ===== UPDATE THESE TO MATCH YOUR MYSQL SETUP =====
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'junnaiidd',         # <-- Your MySQL root password
    'database': 'internship_portal'
}

ADMIN_EMAIL = 'admin@portal.com'
ADMIN_PASSWORD = 'admin123'
COMPANY_EMAIL = 'techcorp@example.com'
COMPANY_PASSWORD = 'company123'

def setup():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # Fix admin password
        admin_hash = generate_password_hash(ADMIN_PASSWORD)
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE email = %s",
            (admin_hash, ADMIN_EMAIL)
        )
        print(f"Admin password set for: {ADMIN_EMAIL} (password: {ADMIN_PASSWORD})")

        # Fix company password
        company_hash = generate_password_hash(COMPANY_PASSWORD)
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE email = %s",
            (company_hash, COMPANY_EMAIL)
        )
        print(f"Company password set for: {COMPANY_EMAIL} (password: {COMPANY_PASSWORD})")

        conn.commit()
        print("\nSetup complete! You can now log in with the demo accounts above.")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    setup()

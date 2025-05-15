#!/usr/bin/env python
import sys
from db_operations.dbop_auth import DatabaseOperationsAuth

def create_admin():
    if len(sys.argv) != 3:
        print("Usage: python create_initial_admin.py <username> <password>")
        return
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    db_auth = DatabaseOperationsAuth()
    
    # Check if admin_users table exists
    try:
        db_auth.cursor.execute("SELECT 1 FROM admin_users LIMIT 1")
    except Exception as e:
        print("Error: admin_users table doesn't exist. Run database setup first.")
        db_auth.close()
        return
    
    # Check if user already exists
    db_auth.cursor.execute(
        "SELECT COUNT(*) FROM admin_users WHERE username = %s",
        (username,)
    )
    count = db_auth.cursor.fetchone()[0]
    
    if count > 0:
        print(f"Admin user '{username}' already exists.")
        db_auth.close()
        return
    
    # Create the admin user
    if db_auth.create_admin_user(username, password):
        print(f"Admin user '{username}' created successfully.")
    else:
        print("Failed to create admin user.")
    
    db_auth.close()

if __name__ == "__main__":
    create_admin() 
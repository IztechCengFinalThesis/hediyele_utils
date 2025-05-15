from typing import Optional
import hashlib
import os
from config.db_config import get_db_connection

class DatabaseOperationsAuth:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
    
    def _hash_password(self, password: str) -> str:
        """Hash a password for storing."""
        salt = os.urandom(32)  # A new salt for this user
        key = hashlib.pbkdf2_hmac(
            'sha256',  # The hash digest algorithm for PBKDF2
            password.encode('utf-8'),  # Convert the password to bytes
            salt,  # Provide the salt
            100000  # 100,000 iterations of SHA-256
        )
        # Store the salt with the password
        return salt.hex() + ':' + key.hex()
    
    def _verify_password(self, stored_password: str, provided_password: str) -> bool:
        """Verify a stored password against a provided password"""
        salt_hex, key_hex = stored_password.split(':')
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        
        # Use the same hash function
        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt,
            100000
        )
        return key == new_key
    
    def create_admin_user(self, username: str, password: str) -> bool:
        """Create a new admin user with hashed password."""
        try:
            hashed_password = self._hash_password(password)
            self.cursor.execute(
                "INSERT INTO admin_users (username, password) VALUES (%s, %s);",
                (username, hashed_password)
            )
            self.commit()
            return True
        except Exception as e:
            print(f"Error creating admin user: {e}")
            self.rollback()
            return False
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate a user by username and password."""
        try:
            self.cursor.execute(
                "SELECT password FROM admin_users WHERE username = %s;",
                (username,)
            )
            result = self.cursor.fetchone()
            if not result:
                return False
            
            stored_password = result[0]
            return self._verify_password(stored_password, password)
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def get_all_admin_users(self):
        """Get all admin usernames for administrative purposes."""
        try:
            self.cursor.execute(
                "SELECT id, username, created_at FROM admin_users ORDER BY id;"
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching admin users: {e}")
            return []
    
    def delete_admin_user(self, user_id: int) -> bool:
        """Delete an admin user by ID."""
        try:
            self.cursor.execute(
                "DELETE FROM admin_users WHERE id = %s;",
                (user_id,)
            )
            self.commit()
            return True
        except Exception as e:
            print(f"Error deleting admin user: {e}")
            self.rollback()
            return False 
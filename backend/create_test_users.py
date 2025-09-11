"""
Simple User Creation Script

Creates test users directly using SQLAlchemy without complex imports.
"""

import sqlite3
import bcrypt
import sys
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "exam_transcripts.db"

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_users():
    """Create test users directly in SQLite."""
    
    # Users to create (using correct enum values)
    users = [
        ("admin@example.com", "admin123", "admin"),
        ("supervisor@example.com", "supervisor123", "supervisor"), 
        ("user@example.com", "user123", "user"),
        ("john.doe@example.com", "password123", "user"),
        ("jane.smith@example.com", "password123", "user")
    ]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if users already exist
        cursor.execute("SELECT COUNT(*) FROM user")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"✅ Database already has {existing_count} users. Skipping seed.")
            return
        
        # Insert users
        for email, password, role in users:
            hashed_password = hash_password(password)
            
            cursor.execute("""
                INSERT INTO user (email, hashed_password, role, created_at, updated_at)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
            """, (email, hashed_password, role))
        
        conn.commit()
        
        print("🎉 Successfully created test users:")
        print()
        for email, password, role in users:
            print(f"📧 Email: {email}")
            print(f"🔑 Password: {password}")
            print(f"👤 Role: {role}")
            print("-" * 40)
            
        print("\n✨ You can now login to the React app with any of these credentials!")
        print("🌐 Frontend: http://localhost:3000")
        print("📚 API Docs: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("🌱 Creating test users...")
    create_users()

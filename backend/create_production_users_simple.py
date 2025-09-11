"""
Simple Production User Creation Script

Uses the existing app infrastructure to create users in production.
Works with both PostgreSQL and SQLite.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

# Set environment to production for this script
os.environ['ENVIRONMENT'] = 'production'
# Set a temporary secret key to avoid validation errors
os.environ['SECRET_KEY'] = 'temporary-secret-key-for-user-creation-script-only'

from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User, UserRole
from app.config.settings import get_settings


def create_users_sync():
    """Create users synchronously."""
    
    print("🌱 Creating users in production database...")
    
    try:
        settings = get_settings()
        print(f"📊 Environment: {settings.environment}")
        print(f"🔗 Database: {settings.database_connection_url}")
        
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        # Check existing users
        existing_count = db.query(User).count()
        print(f"📊 Found {existing_count} existing users")
        
        if existing_count > 0:
            print("🗑️ Removing existing users...")
            db.query(User).delete()
            db.commit()
        
        # Users to create
        users_data = [
            ("admin@example.com", "admin123", UserRole.ADMIN),
            ("supervisor@example.com", "supervisor123", UserRole.SUPERVISOR),
            ("user@example.com", "user123", UserRole.USER),
            ("john.doe@example.com", "password123", UserRole.USER),
            ("jane.smith@example.com", "password123", UserRole.USER)
        ]
        
        print(f"👥 Creating {len(users_data)} users...")
        
        created_users = []
        for email, password, role in users_data:
            # Hash password
            hashed_password = hash_password(password)
            
            # Create user
            user = User(
                email=email,
                hashed_password=hashed_password,
                role=role
            )
            
            db.add(user)
            created_users.append((email, password, role.value))
            print(f"✅ Added user: {email}")
        
        # Commit all users
        db.commit()
        db.close()
        
        print(f"\n🎉 Successfully created {len(created_users)} users!")
        print("\n📧 Login credentials:")
        for email, password, role in created_users:
            print(f"👤 {role.title()}: {email} / {password}")
        
        print("\n🌐 Frontend: https://api-is-for-exam-transcripts.vercel.app")
        print("🔗 Backend: https://apis-for-exam-transcripts.onrender.com")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        return False


if __name__ == "__main__":
    success = create_users_sync()
    if success:
        print("✅ User creation completed!")
        sys.exit(0)
    else:
        print("❌ User creation failed!")
        sys.exit(1)

"""
Database Seeding Script

Creates initial users for testing the application.
Solves the "chicken and egg" problem of needing users to test login.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User, UserRole


async def create_seed_users():
    """Create initial users for testing."""
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"✅ Database already has {existing_users} users. Skipping seed.")
            return
        
        # Create test users
        users_to_create = [
            {
                "email": "admin@example.com",
                "password": "admin123",
                "role": UserRole.ADMIN
            },
            {
                "email": "supervisor@example.com", 
                "password": "supervisor123",
                "role": UserRole.SUPERVISOR
            },
            {
                "email": "user@example.com",
                "password": "user123", 
                "role": UserRole.USER
            },
            {
                "email": "john.doe@example.com",
                "password": "password123",
                "role": UserRole.USER
            },
            {
                "email": "jane.smith@example.com",
                "password": "password123",
                "role": UserRole.USER
            }
        ]
        
        created_users = []
        for user_data in users_to_create:
            # Hash the password
            hashed_password = hash_password(user_data["password"])
            
            # Create user
            user = User(
                email=user_data["email"],
                hashed_password=hashed_password,
                role=user_data["role"]
            )
            
            db.add(user)
            created_users.append(user_data)
        
        # Commit all users
        db.commit()
        
        print("🎉 Successfully created seed users:")
        print()
        for user_data in created_users:
            print(f"📧 Email: {user_data['email']}")
            print(f"🔑 Password: {user_data['password']}")
            print(f"👤 Role: {user_data['role'].value}")
            print("-" * 40)
            
        print("\n✨ You can now login to the React app with any of these credentials!")
        print("🌐 Frontend: http://localhost:3000")
        print("📚 API Docs: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error creating seed users: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding database with initial users...")
    asyncio.run(create_seed_users())

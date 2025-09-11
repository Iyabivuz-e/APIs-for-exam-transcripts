"""
Production User Creation Script

Quick script to create users directly in production PostgreSQL database.
Can be run from Render shell or locally with production database URL.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

import asyncpg
import bcrypt
from datetime import datetime


async def create_users_directly():
    """Create users directly in PostgreSQL database."""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    if not database_url.startswith('postgresql'):
        print("❌ This script is for PostgreSQL databases only")
        return False
    
    print(f"🔗 Connecting to database...")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)
        
        # Check if user table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'user'
            );
        """)
        
        if not table_exists:
            print("❌ User table doesn't exist. Run the backend first to create tables.")
            await conn.close()
            return False
        
        # Check existing users
        existing_count = await conn.fetchval("SELECT COUNT(*) FROM \"user\"")
        print(f"📊 Found {existing_count} existing users")
        
        if existing_count > 0:
            # Delete existing users
            print("🗑️ Removing existing users...")
            await conn.execute("DELETE FROM \"user\"")
        
        # Users to create
        users = [
            ("admin@example.com", "admin123", "admin"),
            ("supervisor@example.com", "supervisor123", "supervisor"), 
            ("user@example.com", "user123", "user"),
            ("john.doe@example.com", "password123", "user"),
            ("jane.smith@example.com", "password123", "user")
        ]
        
        print(f"👥 Creating {len(users)} users...")
        
        # Create users
        for email, password, role in users:
            # Hash password using bcrypt (same as the app)
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insert user
            await conn.execute("""
                INSERT INTO "user" (email, hashed_password, role, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5)
            """, email, hashed_password, role, datetime.now(), datetime.now())
            
            print(f"✅ Created user: {email} (password: {password}, role: {role})")
        
        await conn.close()
        
        print("\n🎉 Successfully created all users!")
        print("\n📧 Login credentials:")
        print("👤 Admin: admin@example.com / admin123")
        print("👤 Supervisor: supervisor@example.com / supervisor123") 
        print("👤 User: user@example.com / user123")
        print("👤 User: john.doe@example.com / password123")
        print("👤 User: jane.smith@example.com / password123")
        print("\n🌐 Frontend: https://api-is-for-exam-transcripts.vercel.app")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🌱 Creating users in production database...")
    success = asyncio.run(create_users_directly())
    if success:
        print("✅ User creation completed!")
        sys.exit(0)
    else:
        print("❌ User creation failed!")
        sys.exit(1)

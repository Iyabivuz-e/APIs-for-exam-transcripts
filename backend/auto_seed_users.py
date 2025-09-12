"""
Auto User Creation for Production (Free Tier Render)

This script automatically creates users when the app starts if:
1. Environment variable CREATE_INITIAL_USERS=true
2. Database is PostgreSQL 
3. No users exist yet

This solves the free tier limitation where shell access isn't available.
"""

import os
import logging
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def should_create_users() -> bool:
    """Check if we should auto-create users."""
    create_users = os.getenv('CREATE_INITIAL_USERS', 'false').lower()
    database_url = os.getenv('DATABASE_URL', '')
    
    return (
        create_users in ['true', '1', 'yes'] and 
        database_url.startswith('postgresql')
    )


async def auto_create_users_if_needed():
    """Auto create users on startup if conditions are met."""
    
    if not should_create_users():
        logger.info("🚫 Auto user creation disabled or not needed")
        return False
    
    try:
        # Import here to avoid circular imports
        from app.db.session import get_db
        from app.models.user import User, UserRole
        from app.core.security import hash_password
        
        logger.info("🌱 Auto-creating initial users for production...")
        
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # Check if users already exist
            existing_count = db.query(User).count()
            
            if existing_count > 0:
                logger.info(f"✅ Database already has {existing_count} users, skipping auto-creation")
                return True
            
            # Define users to create
            users_to_create = [
                ("admin@example.com", "admin123", UserRole.ADMIN),
                ("supervisor@example.com", "supervisor123", UserRole.SUPERVISOR),
                ("user@example.com", "user123", UserRole.USER),
                ("john.doe@example.com", "password123", UserRole.USER),
                ("jane.smith@example.com", "password123", UserRole.USER)
            ]
            
            logger.info(f"👥 Creating {len(users_to_create)} initial users...")
            
            # Create users
            for email, password, role in users_to_create:
                hashed_password = hash_password(password)
                
                user = User(
                    email=email,
                    hashed_password=hashed_password,
                    role=role
                )
                
                db.add(user)
                logger.info(f"✅ Added user: {email} ({role.value})")
            
            # Commit all users
            db.commit()
            
            final_count = db.query(User).count()
            logger.info(f"🎉 Successfully created {final_count} users in production database!")
            
            logger.info("📧 Login credentials available:")
            logger.info("👤 Admin: admin@example.com / admin123")
            logger.info("👤 Supervisor: supervisor@example.com / supervisor123")
            logger.info("👤 User: user@example.com / user123")
            logger.info("👤 User: john.doe@example.com / password123")
            logger.info("👤 User: jane.smith@example.com / password123")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating users: {e}")
            db.rollback()
            return False
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Error in auto user creation: {e}")
        return False


# For testing
if __name__ == "__main__":
    import asyncio
    
    # Set test environment
    os.environ['CREATE_INITIAL_USERS'] = 'true'
    os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'
    
    print("Testing auto user creation logic...")
    result = asyncio.run(auto_create_users_if_needed())
    print(f"Result: {'✅ Success' if result else '❌ Failed'}")

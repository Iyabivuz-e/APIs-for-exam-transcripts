"""
Database Seeding Script

Creates initial users for testing the application.
Solves the "chicken and egg" problem of needing users to test login.

Usage:
    python seed_users.py [--force] [--production]
    
Options:
    --force: Force recreation of users even if they exist
    --production: Run in production mode with secure defaults
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User, UserRole
from app.config.settings import get_settings


def setup_logging(production_mode: bool = False) -> logging.Logger:
    """Setup logging configuration."""
    level = logging.INFO if production_mode else logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s" if production_mode
        else "%(levelname)s: %(message)s"
    )
    return logging.getLogger(__name__)


async def create_seed_users(force: bool = False, production_mode: bool = False):
    """Create initial users for testing."""
    logger = setup_logging(production_mode)
    
    # Override environment for this script if production_mode is True
    if production_mode:
        import os
        os.environ['ENVIRONMENT'] = 'production'
        # Set a temporary secret key to avoid validation errors in production mode
        if not os.getenv('SECRET_KEY') or os.getenv('SECRET_KEY') == 'your-super-secret-key-change-this-in-production':
            os.environ['SECRET_KEY'] = 'temporary-secret-key-for-user-creation-script-only'
    
    settings = get_settings()
    
    logger.info(f"🔧 Environment: {settings.environment}")
    logger.info(f"🔗 Database: {settings.database_connection_url}")
    
    # Warn if using SQLite in production mode
    if production_mode and settings.database_connection_url.startswith('sqlite'):
        logger.warning("⚠️ Production mode is using SQLite database!")
        logger.warning("💡 Users will be created locally, not in your production PostgreSQL")
        logger.warning("💡 To create users in production PostgreSQL, run this script in Render's shell")
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0 and not force:
            logger.info(f"✅ Database already has {existing_users} users. Use --force to recreate.")
            return True
        
        if force and existing_users > 0:
            logger.warning(f"🗑️ Removing {existing_users} existing users...")
            db.query(User).delete()
            db.commit()
        
        # Define user data based on environment
        if production_mode:
            # Production: Create same users as development for easier testing
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
            logger.info("🚨 Creating production users with development credentials for testing")
        else:
            # Development: Create test users
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
        
        logger.info(f"🎉 Successfully created {len(created_users)} users")
        
        # Show credentials for testing (in both development and production)
        logger.info("Created users:")
        for user_data in created_users:
            logger.info(f"📧 Email: {user_data['email']}")
            logger.info(f"🔑 Password: {user_data['password']}")
            logger.info(f"👤 Role: {user_data['role'].value}")
            logger.info("-" * 40)
        
        if not production_mode:
            logger.info("\n✨ You can now login to the React app with any of these credentials!")
            logger.info("🌐 Frontend: http://localhost:3000")
            logger.info("📚 API Docs: http://localhost:8000/docs")
        else:
            logger.info("\n✨ You can now login to your production app with these credentials!")
            logger.info("🌐 Frontend: https://api-is-for-exam-transcripts.vercel.app")
            logger.info("📚 API Backend: https://apis-for-exam-transcripts.onrender.com")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating users: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(description="Seed database with initial users")
    parser.add_argument("--force", action="store_true", help="Force recreate users even if they exist")
    parser.add_argument("--production", action="store_true", help="Run in production mode")
    
    args = parser.parse_args()
    
    logger = setup_logging(args.production)
    logger.info("🌱 Starting database seeding...")
    
    # Run the seeding
    success = asyncio.run(create_seed_users(args.force, args.production))
    
    if success:
        logger.info("✅ Database seeding completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Database seeding failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Production Database User Creation Script

This script connects directly to your production PostgreSQL database 
and creates users. It's designed to be run in Render's shell environment.

Usage:
    python create_users_production.py
"""

import os
import sys
import logging
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_users_in_production():
    """Create users in production database using actual environment."""
    
    logger.info("🚀 Starting production user creation...")
    
    # Check if we're in production environment
    database_url = os.getenv('DATABASE_URL')
    environment = os.getenv('ENVIRONMENT', 'development')
    
    logger.info(f"📊 Environment: {environment}")
    logger.info(f"🔗 Database URL: {database_url[:50]}..." if database_url else "🔗 No DATABASE_URL found")
    
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set!")
        logger.error("💡 This script should be run in Render's shell where DATABASE_URL is available")
        return False
    
    if not database_url.startswith('postgresql'):
        logger.error("❌ This script requires a PostgreSQL database")
        logger.error(f"💡 Current database type: {database_url.split(':')[0]}")
        return False
    
    try:
        # Import app components with the production environment
        from app.core.security import hash_password
        from app.db.session import get_db
        from app.models.user import User, UserRole
        from app.config.settings import get_settings
        
        settings = get_settings()
        logger.info(f"🔧 App environment: {settings.environment}")
        logger.info(f"🔗 App database: {settings.database_connection_url}")
        
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # Check existing users
            existing_count = db.query(User).count()
            logger.info(f"📊 Existing users in database: {existing_count}")
            
            if existing_count > 0:
                logger.info("🗑️ Removing existing users to recreate...")
                db.query(User).delete()
                db.commit()
                logger.info("✅ Existing users removed")
            
            # Users to create
            users_data = [
                ("admin@example.com", "admin123", UserRole.ADMIN, "Administrator"),
                ("supervisor@example.com", "supervisor123", UserRole.SUPERVISOR, "Supervisor"),
                ("user@example.com", "user123", UserRole.USER, "Regular User"),
                ("john.doe@example.com", "password123", UserRole.USER, "Test User 1"),
                ("jane.smith@example.com", "password123", UserRole.USER, "Test User 2")
            ]
            
            logger.info(f"👥 Creating {len(users_data)} users...")
            
            created_users = []
            for email, password, role, description in users_data:
                # Hash password
                hashed_password = hash_password(password)
                
                # Create user
                user = User(
                    email=email,
                    hashed_password=hashed_password,
                    role=role
                )
                
                db.add(user)
                created_users.append((email, password, role.value, description))
                logger.info(f"✅ Added {description}: {email}")
            
            # Commit all users
            db.commit()
            logger.info("💾 Users committed to database")
            
            # Verify creation
            final_count = db.query(User).count()
            logger.info(f"✅ Final user count: {final_count}")
            
            db.close()
            
            logger.info(f"\n🎉 Successfully created {len(created_users)} users in production database!")
            logger.info("\n📧 Login credentials for your app:")
            logger.info("=" * 60)
            
            for email, password, role, description in created_users:
                logger.info(f"👤 {description}")
                logger.info(f"   📧 Email: {email}")
                logger.info(f"   🔑 Password: {password}")
                logger.info(f"   🎭 Role: {role}")
                logger.info("-" * 40)
            
            logger.info("\n🌐 Test these credentials at:")
            logger.info("   Frontend: https://api-is-for-exam-transcripts.vercel.app")
            logger.info("   Backend API: https://apis-for-exam-transcripts.onrender.com")
            
            return True
            
        except Exception as db_error:
            logger.error(f"❌ Database operation failed: {db_error}")
            db.rollback()
            db.close()
            return False
            
    except ImportError as import_error:
        logger.error(f"❌ Failed to import app modules: {import_error}")
        logger.error("💡 Make sure you're running this from the backend directory")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    logger.info("🌱 Production User Creation Script")
    logger.info("=" * 50)
    
    success = create_users_in_production()
    
    if success:
        logger.info("✅ User creation completed successfully!")
        logger.info("🚀 You can now login to your app!")
        sys.exit(0)
    else:
        logger.error("❌ User creation failed!")
        logger.error("💡 Check the error messages above for details")
        sys.exit(1)

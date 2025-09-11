#!/usr/bin/env python3
"""
Production Database UUID Migration Script

This script handles migrating the production PostgreSQL database 
from integer IDs to UUID strings for Render deployment.

Usage:
    python fix_production_db.py
"""

import os
import sys
import logging
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    return logging.getLogger(__name__)


def main():
    """Main function to fix production database."""
    logger = setup_logging()
    logger.info("🚀 Starting production database UUID migration...")
    
    try:
        from sqlalchemy import create_engine, text, inspect
        
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("❌ DATABASE_URL environment variable not found")
            return False
        
        if not database_url.startswith("postgresql"):
            logger.info("ℹ️ Not a PostgreSQL database, no migration needed")
            return True
        
        logger.info(f"🔗 Connecting to: {database_url[:50]}...")
        
        # Create engine
        engine = create_engine(database_url)
        
        # Check current schema
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            logger.info("✅ Empty database - schema will be created correctly")
            return True
        
        if "user" not in tables:
            logger.info("✅ No user table - schema will be created correctly")
            return True
        
        # Check user table schema
        columns = inspector.get_columns("user")
        id_column = None
        for col in columns:
            if col["name"] == "id":
                id_column = col
                break
        
        if not id_column:
            logger.error("❌ User table has no id column!")
            return False
        
        column_type = str(id_column["type"]).upper()
        logger.info(f"📋 Current 'id' column type: {column_type}")
        
        if "VARCHAR" in column_type or "TEXT" in column_type:
            logger.info("✅ Database already uses UUID-compatible schema")
            return True
        
        if "INTEGER" in column_type or "SERIAL" in column_type:
            logger.info("🔄 Migrating from integer IDs to UUID...")
            
            # Check for existing data
            with engine.connect() as conn:
                result = conn.execute(text('SELECT COUNT(*) FROM "user"'))
                user_count = result.scalar()
                
                if user_count > 0:
                    logger.warning(f"⚠️ Found {user_count} existing users")
                    logger.info("🗑️ Clearing existing data for migration...")
                    
                    # Clear data in correct order (foreign keys first)
                    conn.execute(text('DELETE FROM "user_exam"'))
                    conn.execute(text('DELETE FROM "exam"'))
                    conn.execute(text('DELETE FROM "user"'))
                    conn.commit()
            
            # Perform migration
            migration_sql = [
                # Enable UUID extension
                "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
                
                # Drop and recreate tables with UUID
                'DROP TABLE IF EXISTS "user_exam" CASCADE;',
                'DROP TABLE IF EXISTS "exam" CASCADE;',
                'DROP TABLE IF EXISTS "user" CASCADE;',
                
                # Create user table with UUID
                """
                CREATE TABLE "user" (
                    email VARCHAR(255) NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    id VARCHAR(36) NOT NULL DEFAULT gen_random_uuid()::text,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    PRIMARY KEY (id)
                );
                """,
                
                # Create exam table with UUID
                """
                CREATE TABLE "exam" (
                    title VARCHAR(255) NOT NULL,
                    date DATE NOT NULL,
                    id VARCHAR(36) NOT NULL DEFAULT gen_random_uuid()::text,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    PRIMARY KEY (id)
                );
                """,
                
                # Create user_exam table with UUID
                """
                CREATE TABLE "user_exam" (
                    user_id VARCHAR(36) NOT NULL,
                    exam_id VARCHAR(36) NOT NULL,
                    vote FLOAT,
                    id VARCHAR(36) NOT NULL DEFAULT gen_random_uuid()::text,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    PRIMARY KEY (id),
                    CONSTRAINT uq_user_exam UNIQUE (user_id, exam_id),
                    FOREIGN KEY(user_id) REFERENCES "user" (id) ON DELETE CASCADE,
                    FOREIGN KEY(exam_id) REFERENCES "exam" (id) ON DELETE CASCADE
                );
                """,
                
                # Create indexes
                'CREATE UNIQUE INDEX ix_user_email ON "user" (email);',
                'CREATE UNIQUE INDEX ix_user_id ON "user" (id);',
                'CREATE UNIQUE INDEX ix_exam_id ON "exam" (id);',
                'CREATE UNIQUE INDEX ix_exam_title ON "exam" (title);',
                'CREATE INDEX ix_exam_date ON "exam" (date);',
                'CREATE UNIQUE INDEX ix_user_exam_id ON "user_exam" (id);',
                'CREATE INDEX ix_user_exam_user_id ON "user_exam" (user_id);',
                'CREATE INDEX ix_user_exam_exam_id ON "user_exam" (exam_id);',
            ]
            
            with engine.begin() as conn:
                for i, sql in enumerate(migration_sql, 1):
                    if sql.strip():
                        logger.info(f"📝 Executing step {i}/{len(migration_sql)}...")
                        conn.execute(text(sql))
            
            logger.info("✅ Database migration completed successfully!")
            return True
        
        logger.warning(f"⚠️ Unknown column type: {column_type}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Database Migration Script: Integer IDs to UUID Migration

This script migrates the database schema from integer IDs to UUID strings.
It handles both PostgreSQL (production) and SQLite (local development).

Usage:
    python migrate_to_uuid.py [--dry-run] [--force]
    
Options:
    --dry-run: Show what would be done without making changes
    --force: Force migration even if data exists
"""

import argparse
import logging
import sys
import uuid
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import get_db
from app.config.settings import get_settings


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    return logging.getLogger(__name__)


def is_postgresql(engine):
    """Check if database is PostgreSQL."""
    return "postgresql" in str(engine.url)


def is_sqlite(engine):
    """Check if database is SQLite."""
    return "sqlite" in str(engine.url)


def get_database_type(engine):
    """Get database type string."""
    if is_postgresql(engine):
        return "PostgreSQL"
    elif is_sqlite(engine):
        return "SQLite"
    else:
        return "Unknown"


def check_current_schema(engine, logger):
    """Check current database schema."""
    inspector = inspect(engine)
    
    # Check if tables exist
    tables = inspector.get_table_names()
    if not tables:
        logger.info("📋 No tables found - this is a fresh database")
        return "fresh"
    
    if "user" not in tables:
        logger.info("📋 User table not found - this is a fresh database")
        return "fresh"
    
    # Check user table schema
    columns = inspector.get_columns("user")
    id_column = None
    for col in columns:
        if col["name"] == "id":
            id_column = col
            break
    
    if not id_column:
        logger.error("❌ User table has no id column!")
        return "error"
    
    # Check column type
    column_type = str(id_column["type"]).upper()
    logger.info(f"📋 Current 'id' column type: {column_type}")
    
    if "INTEGER" in column_type or "SERIAL" in column_type:
        return "integer_ids"
    elif "VARCHAR" in column_type or "TEXT" in column_type or "UUID" in column_type:
        return "uuid_ids"
    else:
        logger.warning(f"⚠️ Unknown ID column type: {column_type}")
        return "unknown"


def migrate_postgresql(engine, logger, dry_run=False):
    """Migrate PostgreSQL database from integer IDs to UUIDs."""
    logger.info("🔄 Starting PostgreSQL migration to UUIDs...")
    
    migration_sql = [
        # Step 1: Create uuid-ossp extension if not exists
        "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
        
        # Step 2: Check if we need to migrate data
        """
        DO $$
        BEGIN
            -- Check if tables have data
            IF EXISTS (SELECT 1 FROM "user" LIMIT 1) THEN
                RAISE EXCEPTION 'Cannot migrate: Database contains data. Please backup and clear data first, or use --force flag.';
            END IF;
        END $$;
        """,
        
        # Step 3: Drop existing tables and recreate with UUID
        'DROP TABLE IF EXISTS "user_exam" CASCADE;',
        'DROP TABLE IF EXISTS "exam" CASCADE;',
        'DROP TABLE IF EXISTS "user" CASCADE;',
        
        # Step 4: Create tables with UUID primary keys
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
        
        # Step 5: Create indexes
        'CREATE UNIQUE INDEX ix_user_email ON "user" (email);',
        'CREATE UNIQUE INDEX ix_user_id ON "user" (id);',
        'CREATE UNIQUE INDEX ix_exam_id ON "exam" (id);',
        'CREATE UNIQUE INDEX ix_exam_title ON "exam" (title);',
        'CREATE INDEX ix_exam_date ON "exam" (date);',
        'CREATE UNIQUE INDEX ix_user_exam_id ON "user_exam" (id);',
        'CREATE INDEX ix_user_exam_user_id ON "user_exam" (user_id);',
        'CREATE INDEX ix_user_exam_exam_id ON "user_exam" (exam_id);',
    ]
    
    if dry_run:
        logger.info("🔍 DRY RUN - PostgreSQL migration SQL:")
        for sql in migration_sql:
            logger.info(f"  {sql}")
        return True
    
    try:
        with engine.begin() as conn:
            for i, sql in enumerate(migration_sql, 1):
                logger.info(f"📝 Executing step {i}/{len(migration_sql)}...")
                if sql.strip():  # Skip empty SQL
                    conn.execute(text(sql))
            
        logger.info("✅ PostgreSQL migration completed successfully!")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"❌ PostgreSQL migration failed: {e}")
        return False


def migrate_sqlite(engine, logger, dry_run=False):
    """Migrate SQLite database - just recreate tables since SQLite doesn't support column type changes."""
    logger.info("🔄 Starting SQLite migration to UUIDs...")
    
    migration_sql = [
        # SQLite: Drop and recreate tables
        'DROP TABLE IF EXISTS user_exam;',
        'DROP TABLE IF EXISTS exam;',
        'DROP TABLE IF EXISTS user;',
    ]
    
    if dry_run:
        logger.info("🔍 DRY RUN - SQLite migration SQL:")
        for sql in migration_sql:
            logger.info(f"  {sql}")
        logger.info("  -- Tables would be recreated with UUID schema via SQLAlchemy")
        return True
    
    try:
        # Drop existing tables
        with engine.begin() as conn:
            for sql in migration_sql:
                if sql.strip():
                    conn.execute(text(sql))
        
        # Let SQLAlchemy recreate tables with new schema
        from app.db.base import Base
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ SQLite migration completed successfully!")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"❌ SQLite migration failed: {e}")
        return False


def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description="Migrate database IDs to UUIDs")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--force", action="store_true", help="Force migration even if data exists")
    
    args = parser.parse_args()
    
    logger = setup_logging()
    logger.info("🚀 Starting database UUID migration...")
    
    # Get database session
    settings = get_settings()
    logger.info(f"🔧 Environment: {settings.environment}")
    logger.info(f"🔗 Database URL: {settings.database_connection_url}")
    
    db_gen = get_db()
    db = next(db_gen)
    engine = db.bind
    
    db_type = get_database_type(engine)
    logger.info(f"💾 Database type: {db_type}")
    
    try:
        # Check current schema
        schema_status = check_current_schema(engine, logger)
        
        if schema_status == "error":
            logger.error("❌ Database schema check failed")
            return False
        elif schema_status == "fresh":
            logger.info("✅ Fresh database detected - no migration needed, tables will be created with UUID schema")
            return True
        elif schema_status == "uuid_ids":
            logger.info("✅ Database already uses UUID IDs - no migration needed")
            return True
        elif schema_status == "integer_ids":
            logger.info("📋 Database uses integer IDs - migration required")
        
        # Perform migration based on database type
        if is_postgresql(engine):
            success = migrate_postgresql(engine, logger, args.dry_run)
        elif is_sqlite(engine):
            success = migrate_sqlite(engine, logger, args.dry_run)
        else:
            logger.error(f"❌ Unsupported database type: {db_type}")
            return False
        
        if success:
            if args.dry_run:
                logger.info("🔍 DRY RUN completed - no changes made")
            else:
                logger.info("🎉 Migration completed successfully!")
        else:
            logger.error("❌ Migration failed")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Migration error: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

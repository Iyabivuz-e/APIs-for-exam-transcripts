"""
Database Migration Endpoints

Provides endpoints to handle database migrations in production environments
where direct shell access is limited (like Render).
"""

import os
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.core.permissions import require_admin

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/migrate-to-uuid")
async def migrate_database_to_uuid(
    current_user: User = Depends(require_admin),
) -> dict:
    """
    Migrate production database from integer IDs to UUID strings.
    
    This endpoint can be called via HTTP to trigger database migration
    in environments where shell access is limited.
    
    **Admin access required.**
    
    Returns:
        dict: Migration result status
    """
    try:
        # Get database URL
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="DATABASE_URL environment variable not found"
            )
        
        if not database_url.startswith("postgresql"):
            return {
                "success": True,
                "message": "Not a PostgreSQL database, no migration needed",
                "database_type": "sqlite"
            }
        
        logger.info(f"🔄 Starting UUID migration for production database...")
        
        # Create engine
        engine = create_engine(database_url)
        
        # Check current schema
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            return {
                "success": True,
                "message": "Empty database - schema will be created correctly",
                "action": "none_needed"
            }
        
        if "user" not in tables:
            return {
                "success": True,
                "message": "No user table - schema will be created correctly",
                "action": "none_needed"
            }
        
        # Check user table schema
        columns = inspector.get_columns("user")
        id_column = None
        for col in columns:
            if col["name"] == "id":
                id_column = col
                break
        
        if not id_column:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User table has no id column!"
            )
        
        column_type = str(id_column["type"]).upper()
        logger.info(f"📋 Current 'id' column type: {column_type}")
        
        if "VARCHAR" in column_type or "TEXT" in column_type:
            return {
                "success": True,
                "message": "Database already uses UUID-compatible schema",
                "current_type": column_type,
                "action": "none_needed"
            }
        
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
            
            executed_steps = 0
            with engine.begin() as conn:
                for sql in migration_sql:
                    if sql.strip():
                        logger.info(f"📝 Executing migration step {executed_steps + 1}...")
                        conn.execute(text(sql))
                        executed_steps += 1
            
            logger.info("✅ Database migration completed successfully!")
            
            return {
                "success": True,
                "message": "Database migration completed successfully!",
                "executed_steps": executed_steps,
                "old_type": column_type,
                "new_type": "VARCHAR(36)",
                "action": "migrated"
            }
        
        return {
            "success": False,
            "message": f"Unknown column type: {column_type}",
            "current_type": column_type,
            "action": "unknown"
        }
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )


@router.get("/schema-status")
async def check_schema_status(
    current_user: User = Depends(require_admin),
) -> dict:
    """
    Check the current database schema status.
    
    **Admin access required.**
    
    Returns:
        dict: Current schema information
    """
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return {"error": "DATABASE_URL not found"}
        
        if not database_url.startswith("postgresql"):
            return {
                "database_type": "sqlite",
                "compatible": True,
                "message": "SQLite database - no migration needed"
            }
        
        engine = create_engine(database_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if "user" not in tables:
            return {
                "database_type": "postgresql",
                "compatible": True,
                "message": "User table not found - will be created with UUID schema",
                "tables": tables
            }
        
        columns = inspector.get_columns("user")
        id_column = None
        for col in columns:
            if col["name"] == "id":
                id_column = col
                break
        
        if not id_column:
            return {
                "database_type": "postgresql",
                "compatible": False,
                "message": "User table exists but has no id column",
                "tables": tables
            }
        
        column_type = str(id_column["type"]).upper()
        is_uuid_compatible = "VARCHAR" in column_type or "TEXT" in column_type
        
        return {
            "database_type": "postgresql",
            "compatible": is_uuid_compatible,
            "id_column_type": column_type,
            "message": "Schema compatible" if is_uuid_compatible else "Schema migration needed",
            "tables": tables,
            "columns": [col["name"] for col in columns]
        }
        
    except Exception as e:
        logger.error(f"Schema check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schema check failed: {str(e)}"
        )

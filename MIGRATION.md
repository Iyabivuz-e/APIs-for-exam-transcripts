# Database Migration Guide for Render Deployment

## Problem
When deploying to Render with UUID changes, the production PostgreSQL database still uses INTEGER columns while the application expects VARCHAR(36) UUID columns, causing this error:

```
⚠️ Database schema mismatch detected!
⚠️ Production database uses integer IDs but application expects UUIDs
RuntimeError: generator didn't yield
```

## Solution

### Option 1: Use Web-Based Migration (Recommended for Render)

1. **Deploy the Fixed Application**
   - The lifespan function is now fixed to not crash on schema mismatch
   - The app will start successfully but skip user creation

2. **Login as Admin**
   - Use existing admin credentials or create them manually if needed
   - Access: `https://your-app.onrender.com/docs`

3. **Check Schema Status**
   ```
   GET /private/admin/migration/schema-status
   ```
   This will show current database schema information.

4. **Run Migration**
   ```
   POST /private/admin/migration/migrate-to-uuid
   ```
   This will:
   - Check current schema
   - Drop and recreate tables with UUID columns
   - Clear existing data (if any)
   - Set up proper indexes and constraints

### Option 2: Manual Database Migration

If you have database access, run the `fix_production_db.py` script:

```bash
python fix_production_db.py
```

## What the Migration Does

1. **Schema Conversion**:
   - `id` columns: INTEGER → VARCHAR(36)
   - Maintains all relationships and constraints
   - Adds proper UUID indexes

2. **Data Handling**:
   - Clears existing data to prevent conflicts
   - Tables are recreated with UUID-compatible schema
   - Auto-user creation will work after migration

3. **Safety Checks**:
   - Detects current schema before making changes
   - Only runs on PostgreSQL databases
   - Provides detailed status information

## After Migration

1. **Restart Application**: After migration, restart your Render service
2. **Auto-User Creation**: The app will now create initial users automatically
3. **Login Credentials**:
   - Admin: `admin@example.com` / `admin123`
   - Supervisor: `supervisor@example.com` / `supervisor123` 
   - User: `user@example.com` / `user123`

## Environment Variables

Ensure these are set in your Render environment:

```bash
CREATE_INITIAL_USERS=true
DATABASE_URL=postgresql://... (provided by Render)
```

## Verification

After migration, check the logs for:
```
✅ Database schema compatible (ID type: VARCHAR)
🎉 Successfully created X users in production database!
```

The UUID conversion provides better security by using non-sequential, unpredictable identifiers instead of incremental integers.

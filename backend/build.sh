#!/bin/bash

# Render Build Script for Free Tier
# This runs during deployment and creates users automatically

echo "🚀 Starting build process..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create users in production database
echo "👥 Creating users in production database..."
python -c "
import os
import sys
sys.path.append('.')

# Import required modules
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User, UserRole

print('🌱 Creating production users...')

try:
    # Get database session  
    db_gen = get_db()
    db = next(db_gen)
    
    # Check if users exist
    existing_count = db.query(User).count()
    
    if existing_count > 0:
        print(f'✅ Database has {existing_count} users already')
    else:
        # Create users
        users = [
            ('admin@example.com', 'admin123', UserRole.ADMIN),
            ('supervisor@example.com', 'supervisor123', UserRole.SUPERVISOR),
            ('user@example.com', 'user123', UserRole.USER),
            ('john.doe@example.com', 'password123', UserRole.USER),
            ('jane.smith@example.com', 'password123', UserRole.USER)
        ]
        
        for email, password, role in users:
            hashed_password = hash_password(password)
            user = User(email=email, hashed_password=hashed_password, role=role)
            db.add(user)
            print(f'✅ Added user: {email}')
        
        db.commit()
        print(f'🎉 Created {len(users)} users successfully!')
        
        print('📧 Login credentials:')
        print('👤 Admin: admin@example.com / admin123')
        print('👤 Supervisor: supervisor@example.com / supervisor123')
        print('👤 User: user@example.com / user123')
        print('👤 User: john.doe@example.com / password123')
        print('👤 User: jane.smith@example.com / password123')
    
    db.close()

except Exception as e:
    print(f'⚠️ User creation skipped: {e}')
    # Don't fail the build if user creation fails
    pass
"

echo "✅ Build completed successfully!"

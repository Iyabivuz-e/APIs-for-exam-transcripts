#!/usr/bin/env python3
"""
Production Configuration Test for Render Deployment
"""

import os
import sys

def test_render_environment():
    print("🔍 RENDER DEPLOYMENT CONFIGURATION TEST")
    print("=" * 50)
    
    # Check critical environment variables
    env_vars = {
        'ENVIRONMENT': os.getenv('ENVIRONMENT'),
        'AUTO_CREATE_USERS': os.getenv('AUTO_CREATE_USERS'),
        'ENABLE_DOCS': os.getenv('ENABLE_DOCS'),
        'DATABASE_URL': os.getenv('DATABASE_URL', '')[0:50] + '...' if os.getenv('DATABASE_URL') else None,
        'SECRET_KEY': '***CONFIGURED***' if os.getenv('SECRET_KEY') else None,
        'LOG_LEVEL': os.getenv('LOG_LEVEL'),
        'PORT': os.getenv('PORT'),
    }
    
    print("\n1. Environment Variables:")
    for key, value in env_vars.items():
        if value:
            print(f"   ✅ {key}: {value}")
        else:
            print(f"   ❌ {key}: NOT SET")
    
    # Test production safety
    print("\n2. Production Safety Checks:")
    environment = os.getenv('ENVIRONMENT', 'development')
    auto_create = os.getenv('AUTO_CREATE_USERS', 'true').lower() == 'true'
    
    if environment == 'production':
        print(f"   ✅ Environment: {environment}")
        
        if auto_create:
            print("   ❌ AUTO_CREATE_USERS: true (MUST BE FALSE IN PRODUCTION!)")
            return False
        else:
            print("   ✅ AUTO_CREATE_USERS: false")
        
        if not os.getenv('DATABASE_URL'):
            print("   ❌ DATABASE_URL: not configured")
            return False
        else:
            print("   ✅ DATABASE_URL: configured")
            
        if not os.getenv('SECRET_KEY') or os.getenv('SECRET_KEY') == 'your-super-secret-key-change-this-in-production':
            print("   ❌ SECRET_KEY: not secure")
            return False
        else:
            print("   ✅ SECRET_KEY: configured securely")
    
    # Try to load settings
    print("\n3. Settings Validation:")
    try:
        from app.config.settings import get_settings
        settings = get_settings()
        print(f"   ✅ Settings loaded successfully")
        print(f"   ✅ Environment: {settings.environment}")
        print(f"   ✅ Auto create users: {settings.auto_create_users}")
        print(f"   ✅ Enable docs: {settings.enable_docs}")
        return True
    except Exception as e:
        print(f"   ❌ Settings validation failed: {e}")
        return False

if __name__ == "__main__":
    success = test_render_environment()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 RENDER CONFIGURATION: ✅ READY")
    else:
        print("❌ RENDER CONFIGURATION: FAILED")
        sys.exit(1)

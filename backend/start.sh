#!/bin/bash

# Render.com Startup Script
# =========================

echo "🚀 Starting Exam Transcripts API on Render..."

# Set production environment variables (fallback if not set in Render dashboard)
export ENVIRONMENT=${ENVIRONMENT:-"production"}
export AUTO_CREATE_USERS=${AUTO_CREATE_USERS:-"false"}
export ENABLE_DOCS=${ENABLE_DOCS:-"false"}
export LOG_LEVEL=${LOG_LEVEL:-"INFO"}

# Validate critical environment variables
if [ "$ENVIRONMENT" = "production" ]; then
    echo "✅ Production environment detected"
    
    if [ "$AUTO_CREATE_USERS" = "true" ]; then
        echo "❌ ERROR: AUTO_CREATE_USERS must be false in production"
        exit 1
    fi
    
    if [ -z "$DATABASE_URL" ]; then
        echo "❌ ERROR: DATABASE_URL must be set in production"
        exit 1
    fi
    
    if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-super-secret-key-change-this-in-production" ]; then
        echo "❌ ERROR: Secure SECRET_KEY must be set in production"
        exit 1
    fi
    
    echo "✅ Production safety checks passed"
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Run database migrations (if you have any)
echo "🗄️ Preparing database..."

# Start the application
echo "🎯 Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

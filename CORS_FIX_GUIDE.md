# CORS Configuration Fix Guide

## Problem
You're getting CORS errors when connecting your frontend to the backend deployed on Render.

## Root Causes
1. **Frontend API URL mismatch**: Your `.env.production` had a placeholder URL
2. **Missing frontend domain**: Your backend doesn't know about your actual frontend domain
3. **CORS configuration**: May need additional headers for Render

## Fixes Applied

### 1. Frontend Configuration
Updated `/frontend/.env.production`:
```bash
REACT_APP_API_URL=https://apis-for-exam-transcripts.onrender.com
```

### 2. Backend CORS Configuration
Enhanced `/backend/app/config/settings.py`:
- Added dynamic CORS origins support
- Added `frontend_url` environment variable support
- Improved CORS origins property

### 3. FastAPI CORS Middleware
Updated `/backend/app/main.py`:
- Added explicit HTTP methods
- Added `expose_headers` for better compatibility
- Using dynamic origins from settings

## Deployment Steps

### For Render Backend:
1. Add these environment variables in Render dashboard:
   ```
   ENVIRONMENT=production
   SECRET_KEY=your-production-secret-key-here
   FRONTEND_URL=https://your-frontend-domain.vercel.app
   LOG_LEVEL=INFO
   ENABLE_DOCS=false
   ```

2. If using PostgreSQL on Render:
   ```
   DATABASE_URL=postgresql://username:password@hostname:port/database
   ```

### For Vercel Frontend:
1. Ensure your build is using the production environment
2. Make sure `REACT_APP_API_URL` is set to your Render backend URL

## Testing
1. Deploy backend to Render with new environment variables
2. Deploy frontend to Vercel with updated `.env.production`
3. Test the connection

## Additional CORS Troubleshooting

If you still have issues, you can temporarily add your exact frontend domain:

1. Find your exact frontend URL from Vercel
2. Add it to `allowed_origins` in `settings.py`:
   ```python
   allowed_origins: List[str] = [
       # ... existing origins ...
       "https://your-exact-frontend-url.vercel.app"
   ]
   ```

## Environment Variables Reference

### Backend (.env.render):
```bash
ENVIRONMENT=production
SECRET_KEY=your-production-secret-key-change-this
DATABASE_URL=postgresql://username:password@hostname:port/database
FRONTEND_URL=https://your-frontend-domain.vercel.app
LOG_LEVEL=INFO
ENABLE_DOCS=false
```

### Frontend (.env.production):
```bash
GENERATE_SOURCEMAP=false
REACT_APP_API_URL=https://apis-for-exam-transcripts.onrender.com
```

## Quick Fix
If you need an immediate fix, temporarily set `allow_origins=["*"]` in main.py, but **DO NOT** use this in production for security reasons.

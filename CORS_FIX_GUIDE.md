# CORS Configuration Fix Guide

## Your Actual Domains
- **Frontend**: https://api-is-for-exam-transcripts.vercel.app
- **Backend**: https://apis-for-exam-transcripts.onrender.com

## Problem
You're getting CORS errors when connecting your frontend to the backend deployed on Render.

## Fixes Applied ✅

### 1. Frontend Configuration ✅
Updated `/frontend/.env.production`:
```bash
REACT_APP_API_URL=https://apis-for-exam-transcripts.onrender.com
```

### 2. Backend CORS Configuration ✅
Enhanced `/backend/app/config/settings.py`:
- Added your actual frontend domain: `https://api-is-for-exam-transcripts.vercel.app`
- Added dynamic CORS origins support
- Added `frontend_url` environment variable support

### 3. FastAPI CORS Middleware ✅
Updated `/backend/app/main.py`:
- Added explicit HTTP methods
- Added `expose_headers` for better compatibility
- Using dynamic origins from settings

## Deployment Steps

### For Render Backend (CRITICAL):
1. **Add these environment variables in your Render dashboard**:
   ```
   ENVIRONMENT=production
   SECRET_KEY=your-production-secret-key-here
   FRONTEND_URL=https://api-is-for-exam-transcripts.vercel.app
   LOG_LEVEL=INFO
   ENABLE_DOCS=false
   ```

2. **If using PostgreSQL on Render**:
   ```
   DATABASE_URL=postgresql://username:password@hostname:port/database
   ```

3. **Redeploy your backend** after adding these environment variables

### For Vercel Frontend:
1. ✅ Environment is already configured correctly
2. **Redeploy your frontend** to pick up the new environment variables

## Testing Steps
1. ✅ CORS configuration is tested and working locally
2. Deploy backend to Render with new environment variables
3. Deploy frontend to Vercel (should already be correct)
4. Test the connection from: https://api-is-for-exam-transcripts.vercel.app

## If Still Having Issues

### Quick Debug:
1. Open browser dev tools on your frontend
2. Check if the API calls are going to the correct URL
3. Look at the Network tab for CORS error details

### Temporary Fix (NOT for production):
If you need immediate testing, you can temporarily set in `main.py`:
```python
allow_origins=["*"]  # REMOVE THIS AFTER TESTING
```

## Environment Variables Reference

### Backend (.env.render) - Use these in Render dashboard:
```bash
ENVIRONMENT=production
SECRET_KEY=your-production-secret-key-change-this
DATABASE_URL=postgresql://username:password@hostname:port/database
FRONTEND_URL=https://api-is-for-exam-transcripts.vercel.app
LOG_LEVEL=INFO
ENABLE_DOCS=false
```

### Frontend (.env.production) - Already configured:
```bash
GENERATE_SOURCEMAP=false
REACT_APP_API_URL=https://apis-for-exam-transcripts.onrender.com
```

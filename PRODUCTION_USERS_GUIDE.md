# User Creation Guide for Production

## ✅ Fixed! Users Now Created Successfully

The seed script has been updated to work in production mode and create the same users as development for easier testing.

## Production Login Credentials

You can now use these credentials to login to your production app:

### Admin User:
- **Email**: `admin@example.com`
- **Password**: `admin123`
- **Role**: Admin (full access)

### Supervisor User:
- **Email**: `supervisor@example.com`
- **Password**: `supervisor123`
- **Role**: Supervisor (can assign votes to users)

### Regular Users:
- **Email**: `user@example.com` / **Password**: `user123`
- **Email**: `john.doe@example.com` / **Password**: `password123`
- **Email**: `jane.smith@example.com` / **Password**: `password123`

## How to Run User Creation on Render

### Method 1: Via Render Shell (Recommended)
1. Go to your Render dashboard
2. Find your backend service
3. Click on the "Shell" tab
4. Run this command:
   ```bash
   python seed_users.py --production --force
   ```

### Method 2: Add to Build Command
In your Render service settings, update your build command to:
```bash
pip install -r requirements.txt && python seed_users.py --production
```

### Method 3: Manual Run (if needed)
If the above doesn't work, you can run it manually:
```bash
cd /opt/render/project/src
python seed_users.py --production --force
```

## Testing Your Production App

1. **Frontend**: https://api-is-for-exam-transcripts.vercel.app
2. **Backend API**: https://apis-for-exam-transcripts.onrender.com

Try logging in with any of the credentials above!

## Notes
- The `--force` flag will recreate users if they already exist
- The `--production` flag ensures it runs in production mode
- All users are created with the same passwords as development for consistency
- You can change passwords later through the admin interface if needed

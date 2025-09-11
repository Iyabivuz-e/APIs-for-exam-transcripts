# Exam Transcripts Frontend - Production Deployment

## 🚀 Vercel Deployment Guide (Monorepo)

### Prerequisites
- Node.js 18+
- Vercel account
- Backend API deployed and accessible

### Important: Monorepo Structure
This project uses a monorepo structure with separate `backend/` and `frontend/` directories. The deployment configuration is set up to deploy only the frontend from the root repository.

### Deployment Steps

1. **Update Environment Variables**
   ```bash
   # Update frontend/.env.production with your actual backend URL
   REACT_APP_API_URL=https://your-backend-api.vercel.app
   GENERATE_SOURCEMAP=false
   ```

2. **Build and Test Locally**
   ```bash
   cd frontend
   npm run build
   npm run build:analyze  # Test the build locally
   ```

3. **Deploy to Vercel**
   ```bash
   # From the ROOT directory (not frontend/)
   cd /path/to/APIs-for-exam-transcripts
   
   # Install Vercel CLI if not already installed
   npm i -g vercel
   
   # Deploy from root (Vercel will use the root vercel.json config)
   vercel --prod
   ```

4. **Set Environment Variables in Vercel Dashboard**
   - Go to your Vercel project settings
   - Add environment variables:
     - `REACT_APP_API_URL`: Your backend API URL
     - `GENERATE_SOURCEMAP`: `false`

### 🔧 Recent Fix Applied

**Issue**: Vercel deployment failed with "Could not find a required file: index.html"

**Root Cause**: Vercel was looking for the frontend files in the wrong directory due to the monorepo structure.

**Solution Applied**:
1. Created root-level `vercel.json` to configure monorepo deployment
2. Added `vercel-build` script to `package.json`
3. Created `.vercelignore` to exclude backend files
4. Updated deployment documentation for monorepo structure

**Files Modified**:
- `/vercel.json` (new) - Vercel monorepo configuration
- `/frontend/package.json` - Added vercel-build script
- `/.vercelignore` (new) - Exclude backend from deployment
- `/frontend/DEPLOYMENT.md` - Updated deployment instructions

### Monorepo Configuration Files

✅ **Security & Performance**
- All console.log statements removed
- Source maps disabled in production
- Security headers added
- Bundle size optimized

✅ **TypeScript Configuration**
- Strict type checking enabled
- Unused variables/parameters detection
- No implicit returns

✅ **Vercel Configuration**
- SPA routing configured
- Static asset caching optimized
- Proper redirects setup

✅ **SEO & Accessibility**
- Meta tags optimized
- Proper HTML structure
- Accessible noscript fallback

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API base URL | `https://api.example.com` |
| `GENERATE_SOURCEMAP` | Generate source maps | `false` (production) |

### Scripts

| Command | Description |
|---------|-------------|
| `npm start` | Development server |
| `npm run build` | Production build |
| `npm run build:analyze` | Build and serve locally |
| `npm run type-check` | TypeScript type checking |
| `npm test` | Run tests |

### Production Checklist

- [ ] Backend API URL updated in `.env.production`
- [ ] All console.log statements removed
- [ ] TypeScript strict mode enabled
- [ ] Bundle size optimized
- [ ] Security headers configured
- [ ] SEO meta tags added
- [ ] Error boundaries implemented
- [ ] Loading states properly handled
- [ ] Responsive design tested
- [ ] Cross-browser compatibility verified

### Monitoring & Maintenance

- Monitor Vercel analytics for performance
- Set up error tracking (consider Sentry)
- Regular dependency updates
- Performance monitoring with Web Vitals

### Support

For deployment issues, check:
1. Vercel build logs
2. Browser console for errors
3. Network tab for API calls
4. TypeScript compilation errors

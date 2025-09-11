# Backend Production Deployment Guide

## 🚀 Production Deployment Checklist

### 1. Environment Configuration

Create `.env` file with production values:
```bash
# Copy and modify .env.production template
cp .env.production .env

# Update with your actual values:
ENVIRONMENT=production
SECRET_KEY=your-super-secure-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/database
ALLOWED_ORIGINS=["https://your-frontend-domain.com"]
LOG_LEVEL=INFO
ENABLE_DOCS=false
```

### 2. Security Requirements

- [ ] Generate strong SECRET_KEY (use `openssl rand -hex 32`)
- [ ] Use PostgreSQL for production database
- [ ] Configure HTTPS/SSL
- [ ] Set up environment-specific CORS origins
- [ ] Disable API documentation (`ENABLE_DOCS=false`)
- [ ] Configure proper logging levels

### 3. Database Setup

```bash
# For PostgreSQL production setup
# Install dependencies
pip install psycopg2-binary

# Run migrations (if using Alembic)
alembic upgrade head

# Seed initial admin user (production mode)
python seed_users.py --production
```

### 🔧 Recent Fix Applied

**Issue**: Docker build was failing with "OSError: Readme file does not exist: README.md"

**Root Cause**: The `pyproject.toml` file referenced a README.md file that wasn't present during the Docker build process.

**Solution Applied**:
1. Removed `readme = "README.md"` from pyproject.toml to avoid build dependency
2. Simplified Dockerfile to use `requirements.txt` instead of UV/pyproject.toml for more reliable builds
3. Added proper PostgreSQL development libraries for psycopg2-binary
4. Maintained multi-stage build for production optimization

**Files Modified**:
- `pyproject.toml` - Removed readme reference
- `Dockerfile` - Simplified build process using pip and requirements.txt
- `Dockerfile.complex` - Kept original multi-stage UV build as alternative

### 4. Production Dependencies

Install production dependencies:
```bash
# Using uv (recommended)
uv sync --no-dev

# Or using pip
pip install -r requirements.txt --no-dev
```

### 5. Process Management

Use a process manager like systemd, supervisor, or Docker:

#### Using systemd (Linux)
```ini
# /etc/systemd/system/exam-transcripts-api.service
[Unit]
Description=Exam Transcripts API
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/path/to/backend
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Using Docker (Recommended)

**Build the image:**
```bash
# Simple, production-ready build
docker build -t exam-transcripts-api:latest .

# Test the build locally
docker run --rm -p 8000:8000 \
  -e ENVIRONMENT=development \
  -e SECRET_KEY=dev-secret-key \
  exam-transcripts-api:latest
```

**Production deployment with Docker Compose:**
```bash
# Copy environment template
cp .env.docker .env

# Update .env with production values
# Then start all services
docker-compose up -d

# Or for production profile with nginx
docker-compose --profile production up -d
```

**Alternative: Multi-stage UV build (advanced)**
```bash
# Use the complex Dockerfile for UV-based builds
docker build -f Dockerfile.complex -t exam-transcripts-api:uv .
```

### 6. Monitoring & Logging

- [ ] Set up log aggregation (ELK stack, Datadog, etc.)
- [ ] Configure health check monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Monitor database performance
- [ ] Set up alerts for critical errors

### 7. Performance Optimization

```bash
# Production server with multiple workers
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --access-log \
  --log-level info
```

### 8. Backup Strategy

- [ ] Database backups (automated)
- [ ] Configuration backups
- [ ] Log rotation policy
- [ ] Disaster recovery plan

### 9. Security Headers

Consider adding a reverse proxy (nginx) with security headers:
```nginx
server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 10. Health Checks

The API provides health check endpoints:
- `GET /health` - Detailed health status
- `GET /` - Basic API information

### 🔐 Security Best Practices Applied

✅ **Authentication & Authorization**
- JWT token-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Secure secret key validation

✅ **Data Protection**
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy ORM
- CORS configuration
- Environment-based configuration

✅ **Operational Security**
- Production logging configuration
- Error handling without information leakage
- Documentation disabled in production
- Secure database connection strings

### 📊 Monitoring Endpoints

- `/health` - Application health status
- `/` - Basic API information
- `/docs` - API documentation (disabled in production)

### 🚨 Post-Deployment Tasks

1. **Change default admin password immediately**
2. **Verify all environment variables are set correctly**
3. **Test authentication and authorization**
4. **Monitor logs for any errors**
5. **Set up automated backups**
6. **Configure monitoring and alerting**

### 🔧 Troubleshooting

#### Docker Build Issues

**Problem**: `OSError: Readme file does not exist: README.md`
**Solution**: Use the current Dockerfile that avoids pyproject.toml README dependency

**Problem**: `ModuleNotFoundError: No module named 'jose'`
**Solution**: Ensure all dependencies are installed via requirements.txt

**Problem**: Permission denied for database files
**Solution**: Check that the app user has proper permissions, or use PostgreSQL in production

#### Runtime Issues

**Problem**: Database connection failed
**Solution**: 
- Check DATABASE_URL environment variable
- Ensure PostgreSQL is running and accessible
- Verify database credentials

**Problem**: CORS errors from frontend
**Solution**: Update ALLOWED_ORIGINS in environment variables

**Problem**: JWT token issues
**Solution**: 
- Verify SECRET_KEY is properly set
- Check token expiration settings
- Ensure consistent SECRET_KEY across app restarts

### 📊 Health Check Commands

```bash
# Check if API is responding
curl http://localhost:8000/health

# Check Docker container status
docker ps
docker logs <container_id>

# Check database connectivity (PostgreSQL)
docker exec -it <postgres_container> psql -U <username> -d <database>

# View application logs
docker logs -f <api_container>
```

### 📞 Support

For deployment issues:
1. Check application logs
2. Verify database connectivity
3. Confirm environment variables
4. Test health endpoints
5. Review CORS configuration for frontend connectivity

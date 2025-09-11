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

#### Using Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
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

### 📞 Support

For deployment issues:
1. Check application logs
2. Verify database connectivity
3. Confirm environment variables
4. Test health endpoints
5. Review CORS configuration for frontend connectivity

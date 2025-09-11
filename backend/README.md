# Exam Transcripts API - Backend

## 🚀 Quick Production Deployment

### Prerequisites
- Docker and Docker Compose
- PostgreSQL database (recommended)
- Python 3.11+ (for local development)

### 1. Environment Setup
```bash
# Copy and configure environment variables
cp .env.production .env
# Edit .env with your production values
```

### 2. Docker Deployment (Recommended)
```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs api
```

### 3. Initialize Database
```bash
# Seed initial admin user
docker-compose exec api python seed_users.py --production
```

### 4. Verify Deployment
- Health check: `curl http://localhost:8000/health`
- API status: `curl http://localhost:8000/`

## 📖 Full Documentation

For complete deployment instructions, security configuration, and troubleshooting, see [DEPLOYMENT.md](./DEPLOYMENT.md).

## 🔗 API Endpoints

- `GET /health` - Health check
- `POST /auth/login` - User authentication
- `GET /public/exams` - Public exam listings
- `GET /private/admin/*` - Admin endpoints (authenticated)
- `GET /private/supervisor/*` - Supervisor endpoints (authenticated)
- `GET /private/users/*` - User endpoints (authenticated)

## 🔐 Security Features

- JWT-based authentication
- Role-based access control (Admin, Supervisor, User)
- Password hashing with bcrypt
- CORS protection
- Input validation
- Production logging

## 📞 Support

For deployment issues, check:
1. [DEPLOYMENT.md](./DEPLOYMENT.md) troubleshooting section
2. Docker container logs: `docker-compose logs api`
3. Database connectivity
4. Environment variable configuration

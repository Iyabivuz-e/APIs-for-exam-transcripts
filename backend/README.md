# Backend - Exam Transcripts API

FastAPI backend service for the Exam Transcripts application with role-based access control.

## Features

- RESTful API design with OpenAPI documentation
- JWT authentication and authorization
- Role-based permissions (Admin, Supervisor, User)
- SQLAlchemy ORM with PostgreSQL/SQLite support
- Input validation with Pydantic models
- Comprehensive test coverage

## Project Structure

```
app/
├── api/               # API route definitions
│   ├── auth/         # Authentication endpoints
│   ├── private/      # Protected endpoints
│   └── public/       # Public endpoints
├── core/             # Core application logic
│   ├── exceptions.py # Custom exception handlers
│   ├── permissions.py # Role-based permissions
│   └── security.py   # Authentication utilities
├── db/               # Database configuration
├── models/           # SQLAlchemy models
├── repositories/     # Data access layer
├── schemas/          # Pydantic schemas
└── services/         # Business logic layer
```

## Installation

1. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database**
   ```bash
   python seed_users.py
   ```

## Development

### Running the server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_auth_service.py -v
```

## Configuration

### Environment Variables

Required:
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT signing key (use secure random string)

Optional:
- `ENVIRONMENT`: development/production (default: development)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT expiration (default: 30)
- `ALLOWED_ORIGINS`: CORS origins (default: localhost)

### Database

Development uses SQLite by default. For production, use PostgreSQL:

```env
# Development
DATABASE_URL=sqlite:///./exam_transcripts.db

# Production
DATABASE_URL=postgresql://user:password@host:port/database
```

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user

### Public
- `GET /public/exams` - List public exams with filtering

### Private (Authenticated)
- `GET /private/users/exams` - Get user's exams
- `POST /private/admin/exams` - Create exam (Admin only)
- `GET /private/admin/users` - List users (Admin only)

## User Roles

1. **Admin**: Full system access, can create exams and manage users
2. **Supervisor**: Can assign grades and manage specific operations
3. **User**: Can view assigned exams and personal data

## Testing

The test suite includes:
- Unit tests for services and utilities
- Integration tests for API endpoints
- Database operation tests
- Authentication flow tests

Run tests with:
```bash
pytest tests/ -v
```

## Deployment

### Docker
```bash
docker build -t exam-transcripts-api .
docker run -p 8000:8000 exam-transcripts-api
```

### Production Environment
1. Set `ENVIRONMENT=production`
2. Configure PostgreSQL database
3. Set secure `SECRET_KEY`
4. Configure CORS origins
5. Use proper process manager (gunicorn)

## Security

- JWT tokens for stateless authentication
- Password hashing with bcrypt
- CORS protection
- Input validation and sanitization
- Role-based access control

## Contributing

1. Follow PEP 8 style guidelines
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass before submitting PR

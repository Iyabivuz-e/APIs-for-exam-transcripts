# 📚 Exam Transcripts API

A comprehensive RESTful API for managing exam transcripts with role-based access control, built with FastAPI and modern Python practices.

## 🎯 Project Overview

This API system manages exam transcripts with three distinct user roles:
- **Admin**: Can create new exams
- **Supervisor**: Can assign votes/grades to user exams  
- **User**: Can view their own exam results

## ✨ Features

### 🔐 Authentication & Authorization
- JWT-based authentication with Bearer tokens
- Role-based access control (Admin, Supervisor, User)
- Secure password hashing with bcrypt

### 📋 Exam Management
- Create exams (Admin only)
- Assign grades/votes (Supervisor only)
- View personal exam results (Users)
- Public exam listing with filtering and sorting

### 🔍 Filtering & Sorting
- Filter exams by title (partial match)
- Filter by date range
- Sort by date, title, or creation time
- Pagination support

### 📊 Data Validation
- Comprehensive input validation with Pydantic
- Business rule enforcement (no duplicate exam assignments)
- Grade validation (0-100 scale)

## 🏗️ Architecture

### Clean Architecture Principles
```
📁 app/
├── 📁 api/           # API routes and endpoints
│   ├── 📁 auth/      # Authentication routes
│   ├── 📁 public/    # Public endpoints
│   └── 📁 private/   # Protected endpoints
├── 📁 core/          # Cross-cutting concerns
├── 📁 db/            # Database configuration
├── 📁 models/        # SQLAlchemy models
├── 📁 schemas/       # Pydantic schemas
├── 📁 repositories/  # Data access layer
├── 📁 services/      # Business logic layer
└── 📁 config/        # Configuration settings
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- UV package manager
- SQLite (default) or PostgreSQL

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd APIs-for-exam-transcripts/backend
   ```

2. **Install dependencies with UV**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   uv run uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

### 📖 API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔑 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh token
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info

### Public Endpoints
- `GET /public/exams` - List all exams (with filtering/sorting)
- `GET /public/exams/{id}` - Get exam details

### Private Endpoints

#### User Endpoints
- `GET /private/users/me/exams` - Get user's exam results

#### Admin Endpoints (Admin only)
- `POST /private/admin/exams` - Create new exam

#### Supervisor Endpoints (Supervisor only)
- `PUT /private/supervisor/exams/{id}/vote` - Assign grade to user exam

## 📊 Database Schema

### User Model
```python
class User:
    id: int
    email: str (unique)
    hashed_password: str
    role: UserRole (admin, supervisor, user)
    created_at: datetime
    updated_at: datetime
```

### Exam Model
```python
class Exam:
    id: int
    title: str (unique)
    date: date
    created_at: datetime
    updated_at: datetime
```

### UserExam Association
```python
class UserExam:
    id: int
    user_id: int (FK)
    exam_id: int (FK)
    vote: float (0-100, nullable)
    created_at: datetime
    updated_at: datetime
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test types
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/e2e/
```

### Test Structure
- **Unit Tests**: Test individual components
- **Integration Tests**: Test API endpoints
- **E2E Tests**: Test complete workflows

## 🔧 Development

### Code Quality Tools
```bash
# Format code
uv run black .

# Lint code
uv run ruff check .

# Type checking
uv run mypy app/
```

### Database Operations
```bash
# Create migration
uv run alembic revision --autogenerate -m "migration message"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

## 🌍 Environment Configuration

### Environment Variables
```env
# Server
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./exam_transcripts.db
# For PostgreSQL: postgresql://user:pass@host/db

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=["http://localhost:3000"]
```

## 🚢 Deployment

### Using Docker (Coming Soon)
```bash
# Build image
docker build -t exam-transcripts-api .

# Run container
docker run -p 8000:8000 exam-transcripts-api
```

### Production Checklist
- [ ] Change `SECRET_KEY` in production
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure production database
- [ ] Set up HTTPS
- [ ] Configure logging
- [ ] Set up monitoring

## 📝 Usage Examples

### Authentication
```bash
# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password"}'

# Use token in subsequent requests
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <your-token>"
```

### Create Exam (Admin)
```bash
curl -X POST "http://localhost:8000/private/admin/exams" \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Mathematics Final", "date": "2024-06-15"}'
```

### Assign Grade (Supervisor)
```bash
curl -X PUT "http://localhost:8000/private/supervisor/exams/1/vote" \
  -H "Authorization: Bearer <supervisor-token>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "exam_id": 1, "vote": 85.5}'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛠️ Technology Stack

- **Framework**: FastAPI
- **Database**: SQLAlchemy + SQLite/PostgreSQL
- **Authentication**: JWT with python-jose
- **Validation**: Pydantic
- **Testing**: Pytest
- **Code Quality**: Ruff + Black
- **Package Management**: UV

## 📧 Support

For support or questions, please open an issue in the repository.

---

**Built with ❤️ using FastAPI and modern Python practices**
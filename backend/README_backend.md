# 📚 Exam Transcripts API

A robust RESTful API for managing exam transcripts with role-based access control, built with FastAPI and modern Python practices.

## 🎯 Project Overview

This API provides a comprehensive solution for managing exam transcripts with three distinct user roles:
- **Admin**: Can create and manage exams
- **Supervisor**: Can assign grades/votes to user exams
- **User**: Can view their own exam results

## ✨ Features

- 🔐 **JWT Authentication** with Bearer token support
- 👥 **Role-based Access Control** (Admin, Supervisor, User)
- 📊 **Public Exam Listings** with filtering and sorting
- 🎓 **Grade Management** with numerical and letter grades
- 🔍 **Advanced Filtering** by title, date, and status
- 📄 **Comprehensive API Documentation** with OpenAPI/Swagger
- 🧪 **Full Test Coverage** (unit, integration, e2e)
- 🐳 **Docker Ready** for easy deployment
- 📈 **Clean Architecture** with repository pattern

## 🏗️ Architecture

```
app/
├── 🔧 config/          # Application settings
├── 🛡️ core/            # Security, permissions, exceptions
├── 🌐 api/             # API routes and dependencies
│   ├── 🔓 public/      # Public endpoints
│   ├── 🔐 auth/        # Authentication endpoints
│   └── 🔒 private/     # Protected endpoints
├── 📊 models/          # SQLAlchemy ORM models
├── 📋 schemas/         # Pydantic schemas
├── 🗄️ repositories/    # Data access layer
├── 🔄 services/        # Business logic layer
└── 💾 db/             # Database configuration
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- UV package manager
- SQLite (default) or PostgreSQL

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Iyabivuz-e/APIs-for-exam-transcripts.git
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

## 📖 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Core Endpoints

#### 🔐 Authentication
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh token
- `GET /auth/me` - Get current user info

#### 🌍 Public Endpoints
- `GET /public/exams` - List all exams (with filtering/sorting)
- `GET /public/exams/{id}` - Get exam details

#### 👤 User Endpoints (Authenticated)
- `GET /private/users/me/exams` - Get my exam results

#### 👨‍💼 Admin Endpoints
- `POST /private/admin/exams` - Create new exam

#### 👨‍🏫 Supervisor Endpoints
- `PUT /private/supervisor/exams/{id}/vote` - Assign grade to user exam

## 🧪 Testing

### Run All Tests
```bash
uv run pytest
```

### Run with Coverage
```bash
uv run pytest --cov=app --cov-report=html
```

### Test Categories
- **Unit Tests**: `tests/unit/` - Test individual components
- **Integration Tests**: `tests/integration/` - Test API endpoints
- **E2E Tests**: `tests/e2e/` - Test complete workflows

## 🔨 Development

### Code Quality Tools

```bash
# Format code
uv run black .

# Lint code
uv run ruff check .

# Type checking (if using mypy)
uv run mypy app/
```

### Development Server
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🐳 Docker Deployment

### Build and Run
```bash
docker build -t exam-transcripts-api .
docker run -p 8000:8000 exam-transcripts-api
```

### Using Docker Compose
```bash
docker-compose up -d
```

## 🗄️ Database Configuration

### SQLite (Default)
```env
DATABASE_URL=sqlite:///./exam_transcripts.db
```

### PostgreSQL/NeonDB
```env
DATABASE_URL=postgresql://username:password@host:port/database
```

### Migrations
```bash
# Initialize Alembic (if needed)
uv run alembic init alembic

# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head
```

## 🔒 Security Features

- **JWT Token Authentication** with configurable expiration
- **Password Hashing** using bcrypt
- **Role-based Authorization** with decorators
- **Input Validation** using Pydantic schemas
- **CORS Protection** with configurable origins
- **Rate Limiting** (can be added with slowapi)

## 📊 Data Models

### User
- `id`: Primary key
- `email`: Unique email address
- `hashed_password`: Bcrypt hashed password
- `role`: User role (admin/supervisor/user)

### Exam
- `id`: Primary key
- `title`: Unique exam title
- `date`: Exam date
- `created_at/updated_at`: Timestamps

### UserExam (Association)
- `user_id`: Foreign key to User
- `exam_id`: Foreign key to Exam
- `vote`: Numerical grade (0-100)

## 🎯 Business Rules

1. **Users cannot have the same exam multiple times**
2. **Only admins can create exams**
3. **Only supervisors can assign grades**
4. **Users can only view their own exam results**
5. **Public endpoints show exam lists without sensitive data**

## 🔧 Configuration

Key environment variables:

```env
# Environment
ENVIRONMENT=development  # development/staging/production

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./exam_transcripts.db

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=["http://localhost:3000"]
```

## 📈 Performance Considerations

- **Database Indexing** on frequently queried fields
- **Pagination** for list endpoints
- **Query Optimization** with SQLAlchemy relationships
- **Caching** opportunities for public data
- **Background Tasks** for heavy operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`uv run pytest`)
6. Format code (`uv run black .`)
7. Commit changes (`git commit -m 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📋 TODO/Future Enhancements

- [ ] Email notifications for grade assignments
- [ ] Exam scheduling and reminders
- [ ] File upload for exam materials
- [ ] Advanced reporting and analytics
- [ ] Audit logging for admin actions
- [ ] Rate limiting and API throttling
- [ ] GraphQL endpoint option
- [ ] Redis caching layer
- [ ] Websocket support for real-time updates

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Dieudonne Iyabivuze**
- Email: 116635457+Iyabivuz-e@users.noreply.github.com
- GitHub: [@Iyabivuz-e](https://github.com/Iyabivuz-e)

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for robust ORM capabilities
- Pydantic for data validation
- UV for modern Python package management
- The open-source community for inspiration and tools

---

Built with ❤️ using FastAPI and modern Python practices

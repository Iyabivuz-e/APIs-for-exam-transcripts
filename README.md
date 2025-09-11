# Exam Transcripts API

A RESTful API for managing exam transcripts with role-based access control, built with FastAPI and React.

## Features

- **Authentication & Authorization**: JWT-based authentication with role-based access (Admin, Supervisor, User)
- **Exam Management**: CRUD operations for exam records
- **User Management**: User registration and profile management
- **Role-based Permissions**: Different access levels for different user types
- **Modern Architecture**: FastAPI backend with React frontend

## Architecture

```
├── backend/          # FastAPI REST API
├── frontend/         # React TypeScript application
└── docs/            # API documentation
```

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **PostgreSQL**: Production database
- **JWT**: Authentication tokens
- **Pytest**: Testing framework

### Frontend
- **React 18**: User interface library
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (for production)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd APIs-for-exam-transcripts
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Configure your .env file
   python seed_users.py  # Create test users
   uvicorn app.main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Default Test Users

- **Admin**: admin@example.com / admin123
- **Supervisor**: supervisor@example.com / supervisor123
- **User**: user@example.com / user123

## Production Deployment

### Backend (Render)
1. Connect your GitHub repository to Render
2. Set environment variables (DATABASE_URL, SECRET_KEY, etc.)
3. Deploy as web service

### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Set build command: `npm run build`
3. Deploy automatically on push

## API Documentation

Interactive API documentation is available at `/docs` when running the backend server.

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Environment Variables

### Backend
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT signing key
- `ENVIRONMENT`: development/production
- `ALLOWED_ORIGINS`: CORS allowed origins

### Frontend
- `REACT_APP_API_URL`: Backend API URL (auto-configured)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please use the GitHub Issues page.
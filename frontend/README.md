# Exam Transcripts Frontend

A React TypeScript application for the Exam Transcripts API system.

## Features

- 🔐 **Authentication**: JWT-based login with role management
- 🎯 **Role-based Access**: Admin, Supervisor, and User roles
- 📊 **Dashboard**: Personal and public exam views
- 🎨 **Modern UI**: Tailwind CSS with responsive design
- 🛡️ **Security**: Protected routes and secure API calls
- 📱 **Responsive**: Mobile-first design approach

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Basic UI components (Button, Input, Card)
│   └── LoginForm.tsx   # Authentication form
├── contexts/           # React contexts
│   └── AuthContext.tsx # Authentication state management
├── pages/              # Application pages
│   └── Dashboard.tsx   # Main dashboard
├── services/           # API services
│   └── api.ts          # API client with authentication
├── types/              # TypeScript type definitions
│   └── index.ts        # Core API types
├── App.tsx             # Main app with routing
├── index.tsx           # React app entry point
└── index.css           # Global styles with Tailwind
```

## Key Components

### Authentication
- JWT token management with automatic refresh
- Secure localStorage persistence
- Context-based state management

### UI Components
- **Button**: Multiple variants (primary, secondary, destructive)
- **Input**: Form inputs with validation styles
- **Card**: Container component with title support

### Dashboard
- Role-based content rendering
- User's assigned exams
- Public exam listings
- Quick action buttons for admins/supervisors

## Configuration

The app automatically proxies API requests to `http://localhost:8000` during development (configured in package.json).

## Development

Built with modern React patterns:
- Functional components with hooks
- TypeScript for type safety
- Context API for state management
- React Router for navigation
- Tailwind CSS for styling

## Architecture Principles

Following **KISS (Keep It Simple Stupid)** principles:
- Clear folder structure
- Simple component hierarchy
- Minimal but sufficient abstractions
- Senior-level patterns that are easy to understand
- 👨‍💼 Admin panel for exam creation
- 👨‍🏫 Supervisor interface for grading

## 🚀 Technology Stack

- **Framework**: React 18+
- **Build Tool**: Vite
- **State Management**: Context API or Zustand
- **UI Framework**: Chakra UI or Material-UI
- **HTTP Client**: Axios
- **Router**: React Router v6
- **Form Handling**: React Hook Form
- **Styling**: Styled Components or Emotion

## 🏗️ Planned Structure

```
frontend/
├── public/
├── src/
│   ├── components/         # Reusable UI components
│   ├── pages/             # Page components
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API service layer
│   ├── context/           # React context providers
│   ├── utils/             # Utility functions
│   ├── types/             # TypeScript type definitions
│   └── assets/            # Static assets
├── package.json
└── vite.config.ts
```

## 🔗 API Integration

The frontend will connect to the backend API at:
- **Development**: `http://localhost:8000`
- **Production**: TBD

## 📱 Responsive Design

The application will be fully responsive and work on:
- 💻 Desktop computers
- 📱 Mobile phones
- 📟 Tablets

## 🧪 Testing Strategy

- **Unit Tests**: Jest + React Testing Library
- **Integration Tests**: Cypress or Playwright
- **Component Tests**: Storybook

## 🚧 Development Status

**Status**: Planning Phase

**Next Steps**:
1. Set up React project with Vite
2. Configure TypeScript
3. Set up UI framework
4. Implement authentication flow
5. Create dashboard layouts
6. Build exam management interfaces

---

Check back soon for the React implementation! 🚀

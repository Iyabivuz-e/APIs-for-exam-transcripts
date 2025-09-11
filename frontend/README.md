# Frontend - Exam Transcripts

React TypeScript frontend application for the Exam Transcripts system.

## Features

- **Authentication**: JWT-based login with persistent sessions
- **Role-based Access**: Different views for Admin, Supervisor, and User roles
- **Dashboard**: Personal and public exam views
- **Modern UI**: Tailwind CSS with responsive design
- **Security**: Protected routes and secure API communication
- **Type Safety**: Full TypeScript implementation

## Tech Stack

- **React 18**: Modern hooks-based development
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Context API**: State management for authentication

## Project Structure

```
src/
├── components/        # Reusable UI components
│   ├── ui/           # Base UI components (Button, Input, Card)
│   └── [features]/   # Feature-specific components
├── contexts/         # React context providers
├── pages/            # Main application pages
├── services/         # API client and utilities
└── types/            # TypeScript type definitions
```

## Installation

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

3. **Access the application**
   - Development: http://localhost:3000
   - The backend API is expected at http://localhost:8000

## Development

### Available Scripts

```bash
# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build

# Run tests with coverage
npm test -- --coverage --watchAll=false
```

### Code Style

The project uses:
- ESLint for code linting
- Prettier for code formatting
- TypeScript for type checking

## Configuration

### Environment Variables

The application automatically detects the API URL:
- Development: http://localhost:8000 (proxied)
- Production: Uses the deployed backend URL

No additional configuration needed for basic setup.

### API Integration

The frontend communicates with the backend through a centralized API client located in `src/services/api.ts`.

## User Interface

### Authentication
- Login form with validation
- Persistent sessions across page refreshes
- Automatic logout on token expiration

### Dashboard Views

**Admin Users**:
- Create and manage exams
- View all users
- Assign exams to users

**Supervisor Users**:
- Assign grades to user exams
- View user progress
- Manage supervised content

**Regular Users**:
- View assigned exams
- See exam results
- Access personal dashboard

## Component Architecture

### Base Components (`src/components/ui/`)
- `Button`: Multiple variants (primary, secondary, destructive)
- `Input`: Form inputs with validation states
- `Card`: Container component for content sections

### Feature Components
- `LoginForm`: Authentication form with validation
- `Dashboard`: Role-specific dashboard content
- `CreateExamModal`: Exam creation interface
- `ManageUsersModal`: User management interface

## State Management

The application uses React Context API for:
- Authentication state
- User session management
- Global error handling

## Routing

Protected routes ensure users can only access authorized content:
- `/login`: Public login page
- `/`: Protected dashboard (redirects to login if not authenticated)

## Testing

The application includes:
- Component tests for UI elements
- Integration tests for user flows
- Mock API responses for testing

Run tests:
```bash
npm test
```

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.

## Deployment

### Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Vercel automatically detects Create React App
3. Deploy with automatic builds on push

### Manual Deployment
1. Build the application: `npm run build`
2. Serve the `build/` directory with any static file server

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Follow existing code patterns and naming conventions
2. Add tests for new features
3. Ensure TypeScript types are properly defined
4. Update documentation for significant changes

# Trakly Frontend

Modern React + TypeScript frontend for the Trakly bug and feature tracking platform.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router v6** - Client-side routing
- **Axios** - HTTP client
- **React Hot Toast** - Toast notifications

## Project Structure

```
src/
├── components/
│   ├── layout/          # Layout components (MainLayout, Sidebar, TopBar)
│   ├── ui/              # Reusable UI components
│   ├── issue/           # Issue-specific components
│   ├── project/         # Project-specific components
│   └── feature/         # Feature-specific components
├── contexts/            # React Context providers (Auth, etc.)
├── lib/
│   ├── services/        # API service modules
│   └── api.ts           # Axios client configuration
├── pages/               # Page components
├── routes/              # Routing configuration
├── types/               # TypeScript type definitions
├── App.tsx              # Root component
├── main.tsx             # Entry point
└── index.css            # Global styles
```

## Getting Started

### Prerequisites

- Node.js 20+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at http://localhost:3003

### Environment Variables

Create a `.env.development` file:

```
VITE_API_URL=http://localhost:8003/api/v1
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Features Implemented

### Phase 1: Core Infrastructure ✅
- ✅ Vite + React + TypeScript setup
- ✅ Tailwind CSS configuration
- ✅ TypeScript type definitions (matching backend schemas)
- ✅ Axios API client with JWT interceptors
- ✅ API service modules (auth, issues, features, projects, dashboard)
- ✅ Authentication context and protected routes
- ✅ React Router setup
- ✅ Main layout (Sidebar + TopBar)

### Phase 2: Authentication & Dashboard ✅
- ✅ Login page
- ✅ Dashboard with statistics
- ✅ Projects list page
- ✅ Auto-redirect on 401
- ✅ Toast notifications

### Phase 3: Advanced Features (Next)
- [ ] Issue management (list, create, detail)
- [ ] Real-time duplicate detection
- [ ] Feature tracking pages
- [ ] Project detail and management
- [ ] UI component library
- [ ] Search functionality

## API Integration

The frontend integrates with the Trakly backend API:

- **Base URL**: `http://localhost:8003/api/v1`
- **Authentication**: JWT Bearer tokens stored in localStorage
- **Auto-retry**: Automatic redirect to login on 401

### API Services

- `authService` - Login, logout, get current user
- `issuesService` - CRUD operations, duplicate detection, search
- `featuresService` - Feature management
- `projectsService` - Project management, members, components
- `dashboardService` - Statistics, recent issues, bugs per feature

## Authentication Flow

1. User submits login form
2. POST to `/auth/login` with email/password
3. Receive JWT token and user data
4. Store token in localStorage
5. Include token in all subsequent requests via Axios interceptor
6. On 401 response, clear token and redirect to /login

## Docker Deployment

Build and run with Docker:

```bash
# Build the image
docker build -t trakly-frontend .

# Run the container
docker run -p 3003:80 -e VITE_API_URL=http://localhost:8003/api/v1 trakly-frontend
```

Or use Docker Compose from the root directory:

```bash
docker-compose up frontend
```

## Type Safety

All API responses and requests are typed using TypeScript interfaces that match the backend Pydantic schemas. This ensures compile-time type checking and better IDE support.

## Development Notes

- The app uses React Context for authentication state management
- All routes except `/login` are protected and require authentication
- Error handling is centralized in the Axios interceptor
- Toast notifications are displayed for errors and success messages

## Demo Credentials

After running the backend seed script:

- **Admin**: admin@acme.com / admin123
- **PM**: pm@acme.com / pm123
- **Developer**: dev@acme.com / dev123

## Contributing

1. Create a feature branch
2. Make your changes
3. Ensure `npm run build` succeeds
4. Test the changes
5. Submit a pull request

## License

MIT

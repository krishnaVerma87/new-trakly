# Trakly - Bug & Feature Tracking Platform

> A modern task/bug tracking SaaS product with first-class bug↔feature linking and AI-powered duplicate detection.

## Features

- **Multi-tenant SaaS Architecture** - Organization → Projects → Teams → Users
- **First-Class Feature Tracking** - Features are separate entities with full roadmap support
- **Bug↔Feature Linking** - Explicit linking between bugs and features with backlinks
- **Duplicate Detection** - TF-IDF based similarity matching for automatic duplicate suggestions
- **All Issue Types** - Bug, Task, Sub-task, Story, Improvement
- **Bug-Specific Fields** - Repro steps, environment, stack trace, error signature
- **RBAC** - Role-based access control with 5 default roles
- **Real-time Duplicate Warnings** - See similar issues as you type
- **Dashboard Analytics** - Bug-per-feature metrics and health tracking
- **Comments & Activity** - Full audit trail of all changes

## Tech Stack

### Backend
- **Python 3.11+** with FastAPI (async)
- **SQLAlchemy 2.0** (async ORM)
- **MySQL 8.0**
- **Alembic** for migrations
- **Pydantic v2** for validation
- **JWT** authentication with bcrypt
- **scikit-learn** for TF-IDF duplicate detection

### Frontend
- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **React Router v6**
- **Axios** for HTTP client

### Infrastructure
- **Docker Compose** for local development
- MySQL on port **3309**
- Backend on port **8003**
- Frontend on port **3003**

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/squareops/Trakly.git
cd Trakly
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env if needed (defaults are fine for development)
```

3. **Start the stack**
```bash
docker-compose up -d
```

4. **Run database migrations**
```bash
docker-compose exec backend alembic upgrade head
```

5. **Seed sample data**
```bash
docker-compose exec backend python seed_data.py
```

6. **Access the application**
- **Frontend**: http://localhost:3003
- **Backend API**: http://localhost:8003
- **API Docs**: http://localhost:8003/api/docs

### Sample Login Credentials

After running the seed script, you can log in with:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@acme.com | admin123 |
| Project Manager | pm@acme.com | pm123 |
| Developer | dev@acme.com | dev123 |

## Project Structure

```
trakly/
├── docker-compose.yml
├── .env.example
├── README.md
├── trakly-backend/
│   ├── app/
│   │   ├── core/           # Config, security, exceptions
│   │   ├── db/             # Database session, base model
│   │   ├── models/         # SQLAlchemy models
│   │   ├── repositories/   # Data access layer
│   │   ├── services/       # Business logic
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── api/v1/         # FastAPI endpoints
│   │   └── main.py         # App entry point
│   ├── alembic/            # Database migrations
│   ├── requirements.txt
│   └── seed_data.py
└── trakly-frontend/
    └── src/
        ├── lib/            # API client, utils
        ├── types/          # TypeScript interfaces
        ├── contexts/       # React Context
        ├── routes/         # React Router
        ├── components/     # React components
        └── pages/          # Page components
```

## Core Concepts

### Organization Hierarchy
```
Organization (Acme Corp)
├── Users (with roles)
├── Teams
└── Projects (TRAK, MOBILE)
    ├── Components (Auth, API, UI)
    ├── Features (FEAT-1, FEAT-2)
    └── Issues (TRAK-1, TRAK-2)
        ├── Bugs
        ├── Tasks
        ├── Stories
        ├── Sub-tasks
        └── Improvements
```

### Bug↔Feature Linking

Issues can be linked to features with relationship types:
- **implements** - Issue implements part of the feature
- **blocks** - Issue blocks the feature
- **relates_to** - Issue is related to the feature
- **caused_by** - Bug was caused by the feature

### Duplicate Detection

**How it works:**
1. User fills in title and description
2. System calls `POST /api/v1/issues/check-duplicates`
3. TF-IDF vectorization of existing issues in same project
4. Cosine similarity calculation
5. Top 5 similar issues returned with scores
6. User sees warning if similarity > 70%

**Algorithm:**
- Uses scikit-learn's `TfidfVectorizer`
- Configurable threshold (default: 30%)
- Project-level isolation (duplicates only within same project)
- Fallback to Jaccard similarity if sklearn unavailable

## API Endpoints

### Authentication
```
POST   /api/v1/auth/login          # Login and get JWT token
GET    /api/v1/auth/me             # Get current user info
POST   /api/v1/auth/logout         # Logout
```

### Issues
```
POST   /api/v1/issues/check-duplicates  # Check for duplicates
POST   /api/v1/issues                   # Create issue
GET    /api/v1/issues                   # List issues (with filters)
GET    /api/v1/issues/{id}              # Get issue details
GET    /api/v1/issues/key/{key}         # Get issue by key (TRAK-123)
PATCH  /api/v1/issues/{id}              # Update issue
DELETE /api/v1/issues/{id}              # Delete issue
GET    /api/v1/issues/search            # Search issues
```

### Features
```
POST   /api/v1/features       # Create feature
GET    /api/v1/features       # List features
GET    /api/v1/features/{id}  # Get feature with linked issues
PATCH  /api/v1/features/{id}  # Update feature
DELETE /api/v1/features/{id}  # Delete feature
```

### Projects
```
POST   /api/v1/projects                        # Create project
GET    /api/v1/projects                        # List projects
GET    /api/v1/projects/{id}                   # Get project details
PATCH  /api/v1/projects/{id}                   # Update project
POST   /api/v1/projects/{id}/members           # Add member
GET    /api/v1/projects/{id}/members           # List members
DELETE /api/v1/projects/{id}/members/{user}    # Remove member
POST   /api/v1/projects/{id}/components        # Create component
GET    /api/v1/projects/{id}/components        # List components
```

### Dashboard
```
GET    /api/v1/dashboard/statistics      # Overall stats
GET    /api/v1/dashboard/bugs-per-feature # Bug counts per feature
GET    /api/v1/dashboard/recent-issues    # Recent issues
```

## Database Schema

### Core Tables
- `organizations` - Multi-tenant root
- `users` - Users with org membership
- `roles` - RBAC roles per org
- `permissions` - Resource.action permissions
- `user_roles` - Many-to-many user↔role
- `teams` - User groups
- `team_members` - Many-to-many team↔user
- `projects` - Container for features/issues
- `project_members` - Many-to-many project↔user
- `components` - Sub-modules within projects

### Feature & Issue Tables
- `features` - First-class feature entity
- `issues` - Core issue table (bug/task/story/etc)
- `labels` - Project-scoped labels
- `issue_labels` - Many-to-many issue↔label
- `feature_issue_links` - Links issues to features
- `issue_links` - Links between issues

### Bug-Specific Fields (in `issues` table)
```sql
repro_steps          TEXT
environment          VARCHAR(255)
stack_trace          TEXT
error_signature      VARCHAR(500)
is_regression        BOOLEAN
affected_version     VARCHAR(100)
```

### Duplicate Detection Fields
```sql
deduplication_hash   VARCHAR(64)   -- SHA256 hash
similarity_vector    TEXT          -- TF-IDF vector (JSON)
is_duplicate         BOOLEAN
duplicate_of_id      FK → issues
```

## Development

### Backend Development

```bash
# Install dependencies
cd trakly-backend
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Seed data
python seed_data.py

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

### Frontend Development

```bash
# Install dependencies
cd trakly-frontend
npm install

# Start dev server
npm run dev
```

### Creating Database Migrations

```bash
# Auto-generate migration from model changes
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback one migration
docker-compose exec backend alembic downgrade -1
```

## Environment Variables

Create a `.env` file in the root directory:

```env
# Database
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=trakly
MYSQL_USER=trakly_user
MYSQL_PASSWORD=trakly_pass
MYSQL_PORT=3309

# Backend
BACKEND_PORT=8003
DEBUG=true
ENVIRONMENT=development
JWT_SECRET_KEY=trakly-super-secret-jwt-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Frontend
FRONTEND_PORT=3003
VITE_API_URL=http://localhost:8003/api/v1
```

## Testing

```bash
# Backend tests
docker-compose exec backend pytest -v

# Frontend tests
cd trakly-frontend && npm test
```

## Production Deployment

1. Update environment variables for production
2. Change `JWT_SECRET_KEY` to a secure random value
3. Set `DEBUG=false`
4. Configure proper CORS origins
5. Use production database credentials
6. Enable HTTPS
7. Set up proper backup strategy

## Roadmap

### Phase 1 (MVP) ✅
- [x] Organization, Project, Team, User CRUD
- [x] Feature entity with linking
- [x] All 5 issue types (Bug, Task, Sub-task, Story, Improvement)
- [x] Bug-specific fields
- [x] TF-IDF duplicate detection
- [x] Comments and activity tracking
- [x] Basic workflow
- [x] Dashboard analytics

### Phase 2 (Planned)
- [ ] Custom workflow editor
- [ ] Story points and time tracking
- [ ] Bulk operations
- [ ] CSV import/export
- [ ] Advanced analytics
- [ ] Email notifications
- [ ] Frontend implementation (React + TypeScript)

### Phase 3 (Future)
- [ ] AI-powered bug classification
- [ ] Auto-assignment based on expertise
- [ ] Mobile apps (iOS/Android)
- [ ] Integrations (GitHub, Jira, Slack)
- [ ] Advanced reporting
- [ ] Webhooks

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For questions or issues, please open an issue on GitHub.

---

Built with ❤️ using FastAPI, React, and TypeScript

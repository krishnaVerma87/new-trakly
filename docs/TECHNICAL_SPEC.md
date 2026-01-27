# Trakly - Technical Specification

**Version**: 1.1
**Last Updated**: 2026-01-25
**Status**: MVP Complete, Phase 2 In Progress, Phase 3 (Enhanced Collaboration) Complete, Sprint Planning Complete

---

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [Business Rules](#business-rules)
6. [Security & Access Control](#security--access-control)
7. [Duplicate Detection](#duplicate-detection)
8. [Current Implementation Status](#current-implementation-status)

---

## Overview

Trakly is a modern bug and feature tracking SaaS platform designed for software development teams. It provides first-class feature tracking with bug-to-feature linking, AI-powered duplicate detection, and comprehensive RBAC.

### Key Differentiators
- **First-Class Feature Tracking**: Features are separate entities with full roadmap support
- **Bug↔Feature Linking**: Explicit linking with relationship types (implements, blocks, caused_by)
- **TF-IDF Duplicate Detection**: Real-time similarity matching with 70%+ warning threshold
- **Multi-Tenant Architecture**: Organization → Projects → Teams → Users hierarchy
- **5 Task Types**: Bug, Story, Task, Improvement, Sub-task
- **Sprint Planning**: Full Scrum support with sprint boards, backlog management, and drag-drop

### Terminology Note
**Backend/Database**: Uses "Issue" terminology throughout models, schemas, and API endpoints
**Frontend/UI**: Uses "Task" terminology for user-facing text and labels
- Example: Database table is `issues`, but UI displays "Tasks"
- Issue types remain: `bug`, `story`, `task`, `improvement`, `sub_task`

### Tech Stack
- **Backend**: Python 3.11+, FastAPI (async), SQLAlchemy 2.0 (async ORM), MySQL 8.0
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, React Router v6
- **Infrastructure**: Docker Compose, Alembic migrations
- **ML**: scikit-learn (TF-IDF vectorization)
- **Auth**: JWT with bcrypt

---

## Architecture

### Layered Architecture
```
┌─────────────────────────────────────────┐
│         Frontend (React + TS)           │
│  Port 3003                              │
└─────────────────────────────────────────┘
                    ↓ HTTP/REST
┌─────────────────────────────────────────┐
│      API Layer (FastAPI)                │
│  app/api/v1/*.py                        │
│  - Auth, Projects, Issues, Features     │
│  - Request validation (Pydantic)        │
│  - RBAC enforcement                     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Service Layer                      │
│  app/services/*.py                      │
│  - Business logic                       │
│  - Duplicate detection                  │
│  - Feature-issue linking                │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Repository Layer                   │
│  app/repositories/*.py                  │
│  - Database queries                     │
│  - ORM operations                       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Database (MySQL 8.0)               │
│  Port 3309                              │
└─────────────────────────────────────────┘
```

### Project Structure
```
trakly/
├── trakly-backend/
│   ├── app/
│   │   ├── core/              # Config, security, exceptions
│   │   │   ├── config.py      # Environment configuration
│   │   │   ├── security.py    # JWT, password hashing
│   │   │   └── exceptions.py  # Custom exceptions
│   │   ├── db/                # Database setup
│   │   │   ├── base.py        # BaseModel with UUID, timestamps
│   │   │   └── session.py     # Async session factory
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── user.py        # User, Role, Permission
│   │   │   ├── organization.py
│   │   │   ├── project.py     # Project, Component
│   │   │   ├── team.py
│   │   │   ├── issue.py       # Issue with bug fields
│   │   │   ├── feature.py     # Feature entity
│   │   │   ├── label.py
│   │   │   ├── comment.py
│   │   │   ├── comment_mention.py  # Phase 3: @mentions
│   │   │   ├── activity.py    # Audit log
│   │   │   ├── feature_issue_link.py
│   │   │   ├── issue_link.py
│   │   │   ├── watcher.py     # Issue & Feature watchers
│   │   │   ├── saved_search.py  # Phase 3: Saved searches
│   │   │   ├── attachment.py  # Phase 3: File attachments
│   │   │   ├── sprint.py
│   │   │   ├── notification.py
│   │   │   └── reminder_rule.py
│   │   ├── repositories/      # Data access layer
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── issue.py
│   │   │   ├── feature.py
│   │   │   ├── comment.py
│   │   │   ├── comment_mention.py  # Phase 3
│   │   │   ├── watcher.py
│   │   │   ├── saved_search.py  # Phase 3
│   │   │   └── attachment.py  # Phase 3
│   │   ├── services/          # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── duplicate_detection_service.py
│   │   │   ├── issue_service.py
│   │   │   ├── feature_service.py
│   │   │   ├── project_service.py
│   │   │   ├── comment_service.py  # Phase 3: Comment + mentions
│   │   │   ├── watcher_service.py
│   │   │   ├── search_service.py  # Phase 3: Advanced search
│   │   │   ├── bulk_operations_service.py  # Phase 3
│   │   │   ├── attachment_service.py  # Phase 3
│   │   │   └── notification_service.py
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── user.py
│   │   │   ├── issue.py
│   │   │   ├── feature.py
│   │   │   ├── comment.py
│   │   │   ├── search.py      # Phase 3
│   │   │   ├── bulk.py        # Phase 3
│   │   │   └── attachment.py  # Phase 3
│   │   ├── api/v1/            # FastAPI endpoints
│   │   │   ├── auth.py        # Login, logout
│   │   │   ├── users.py       # User CRUD
│   │   │   ├── organizations.py
│   │   │   ├── projects.py    # Project + members + components
│   │   │   ├── issues.py      # Issue CRUD + duplicate check
│   │   │   ├── features.py    # Feature CRUD + linking
│   │   │   ├── dashboard.py   # Analytics
│   │   │   ├── sprints.py
│   │   │   ├── watchers.py    # Issue & Feature watchers
│   │   │   ├── notifications.py
│   │   │   ├── reminder_rules.py
│   │   │   ├── comments.py    # Phase 3: Comment CRUD
│   │   │   ├── search.py      # Phase 3: Advanced search
│   │   │   ├── bulk.py        # Phase 3: Bulk operations
│   │   │   └── attachments.py  # Phase 3: File uploads
│   │   └── main.py            # FastAPI app initialization
│   ├── alembic/               # Database migrations
│   ├── seed_data.py           # Sample data generator
│   └── requirements.txt
└── trakly-frontend/
    └── src/
        ├── components/        # React components
        │   ├── layout/       # Layout components
        │   │   ├── MainLayout.tsx
        │   │   ├── Sidebar.tsx
        │   │   ├── TopBar.tsx
        │   │   └── ProtectedRoute.tsx
        │   ├── ui/          # UI components
        │   │   ├── Drawer.tsx       # Slide-out panel from right
        │   │   ├── Modal.tsx
        │   │   ├── Badge.tsx
        │   │   └── ...
        │   ├── sprint/      # Sprint components
        │   │   ├── CreateSprintModal.tsx
        │   │   ├── EditSprintModal.tsx
        │   │   └── SprintBoard.tsx
        │   └── issue/       # Task/Issue components
        ├── pages/            # Page components
        │   ├── LoginPage.tsx
        │   ├── SignupPage.tsx      # Organization signup
        │   ├── DashboardPage.tsx
        │   ├── ProjectsPage.tsx
        │   ├── IssuesPage.tsx      # Tasks list (UI: "Tasks")
        │   ├── CreateIssuePage.tsx # Create task (UI: "Create Task")
        │   ├── IssueDetailPage.tsx # Task detail
        │   ├── SprintsPage.tsx     # Sprint list
        │   └── SprintBoardPage.tsx # Sprint Kanban board
        ├── contexts/         # React Context
        │   └── AuthContext.tsx
        ├── lib/              # API client
        │   ├── api.ts       # Axios instance
        │   └── services/    # API service modules
        │       ├── auth.service.ts
        │       ├── projects.service.ts
        │       ├── issues.service.ts
        │       ├── sprints.service.ts
        │       ├── dashboard.service.ts
        │       └── organizations.service.ts
        ├── types/            # TypeScript interfaces
        │   └── index.ts     # All type definitions
        └── routes/           # React Router
            └── index.tsx     # Route configuration
```

---

## Database Schema

### Organization Hierarchy

#### organizations
```sql
CREATE TABLE organizations (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(255),
    plan_type VARCHAR(50) DEFAULT 'free',
    max_users INT DEFAULT 10,
    is_active BOOLEAN DEFAULT true,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### users
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    organization_id VARCHAR(36) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(500),
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT true,
    last_login_at DATETIME,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
```

#### roles
```sql
CREATE TABLE roles (
    id VARCHAR(36) PRIMARY KEY,
    organization_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    is_system_role BOOLEAN DEFAULT false,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
```

**System Roles**:
- `org_admin`: Full access to everything
- `project_manager`: Create/manage projects and issues
- `developer`: Create/edit issues, comment
- `reporter`: Create issues, comment (read-only on others)
- `viewer`: Read-only access

#### permissions
```sql
CREATE TABLE permissions (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,  -- Format: "resource.action"
    resource VARCHAR(50) NOT NULL,      -- "issue", "project", "feature"
    action VARCHAR(50) NOT NULL,        -- "create", "read", "update", "delete"
    description VARCHAR(500),
    created_at DATETIME,
    updated_at DATETIME
);
```

#### user_roles (Many-to-Many)
```sql
CREATE TABLE user_roles (
    user_id VARCHAR(36),
    role_id VARCHAR(36),
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    assigned_by VARCHAR(36),
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id)
);
```

#### role_permissions (Many-to-Many)
```sql
CREATE TABLE role_permissions (
    role_id VARCHAR(36),
    permission_id VARCHAR(36),
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);
```

### Project Structure

#### teams
```sql
CREATE TABLE teams (
    id VARCHAR(36) PRIMARY KEY,
    organization_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
```

#### team_members
```sql
CREATE TABLE team_members (
    team_id VARCHAR(36),
    user_id VARCHAR(36),
    role VARCHAR(50) DEFAULT 'member',  -- 'lead', 'member'
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (team_id, user_id),
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### projects
```sql
CREATE TABLE projects (
    id VARCHAR(36) PRIMARY KEY,
    organization_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    key VARCHAR(10) UNIQUE NOT NULL,     -- "TRAK", "MOBILE" (for issue keys)
    description TEXT,
    lead_user_id VARCHAR(36),
    default_assignee_id VARCHAR(36),
    is_active BOOLEAN DEFAULT true,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (lead_user_id) REFERENCES users(id),
    FOREIGN KEY (default_assignee_id) REFERENCES users(id)
);
```

#### project_members
```sql
CREATE TABLE project_members (
    project_id VARCHAR(36),
    user_id VARCHAR(36),
    role VARCHAR(50) DEFAULT 'member',   -- 'owner', 'member'
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    added_by VARCHAR(36),
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (added_by) REFERENCES users(id)
);
```

#### components
```sql
CREATE TABLE components (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    lead_user_id VARCHAR(36),
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (lead_user_id) REFERENCES users(id)
);
```

### Feature & Issue Tracking

#### features
```sql
CREATE TABLE features (
    id VARCHAR(36) PRIMARY KEY,
    organization_id VARCHAR(36) NOT NULL,
    project_id VARCHAR(36) NOT NULL,
    feature_number INT NOT NULL,         -- Auto-increment per project
    title VARCHAR(500) NOT NULL,
    description TEXT,
    owner_user_id VARCHAR(36),
    component_id VARCHAR(36),
    status VARCHAR(50) DEFAULT 'backlog',
    -- Status values: backlog, planning, in_progress, testing, completed, cancelled
    priority VARCHAR(50) DEFAULT 'medium',
    target_release VARCHAR(100),
    target_date DATE,
    actual_completion_date DATE,
    progress_percentage INT DEFAULT 0,
    created_by VARCHAR(36),
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (owner_user_id) REFERENCES users(id),
    FOREIGN KEY (component_id) REFERENCES components(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_project_status (project_id, status)
);
```

#### issues
```sql
CREATE TABLE issues (
    id VARCHAR(36) PRIMARY KEY,
    organization_id VARCHAR(36) NOT NULL,
    project_id VARCHAR(36) NOT NULL,
    issue_number INT NOT NULL,           -- Auto-increment per project
    issue_key VARCHAR(20) UNIQUE NOT NULL, -- "TRAK-123"

    -- Basic info
    title VARCHAR(500) NOT NULL,
    description TEXT,
    issue_type VARCHAR(50) NOT NULL,
    -- Type values: bug, task, sub_task, story, improvement

    -- Bug-specific fields (nullable for non-bugs)
    repro_steps TEXT,
    environment VARCHAR(255),
    stack_trace TEXT,
    error_signature VARCHAR(500),
    is_regression BOOLEAN DEFAULT false,
    affected_version VARCHAR(100),

    -- Status and priority
    status VARCHAR(50) DEFAULT 'new',
    -- Status values: new, in_progress, review, done, closed, wont_fix
    priority VARCHAR(50) DEFAULT 'medium',
    severity VARCHAR(50),                 -- For bugs: blocker, critical, major, minor, trivial

    -- Assignment
    reporter_id VARCHAR(36) NOT NULL,
    assignee_id VARCHAR(36),
    component_id VARCHAR(36),
    parent_issue_id VARCHAR(36),         -- For sub-tasks

    -- Estimation
    story_points INT,
    time_estimate_minutes INT,
    time_spent_minutes INT DEFAULT 0,

    -- Resolution
    resolution VARCHAR(50),               -- fixed, duplicate, wont_fix, cannot_reproduce
    resolved_at DATETIME,
    resolved_by VARCHAR(36),

    -- Duplicate detection
    deduplication_hash VARCHAR(64),       -- SHA256 of normalized content
    similarity_vector TEXT,               -- TF-IDF vector as JSON
    is_duplicate BOOLEAN DEFAULT false,
    duplicate_of_id VARCHAR(36),

    created_at DATETIME,
    updated_at DATETIME,

    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (reporter_id) REFERENCES users(id),
    FOREIGN KEY (assignee_id) REFERENCES users(id),
    FOREIGN KEY (component_id) REFERENCES components(id),
    FOREIGN KEY (parent_issue_id) REFERENCES issues(id),
    FOREIGN KEY (resolved_by) REFERENCES users(id),
    FOREIGN KEY (duplicate_of_id) REFERENCES issues(id),

    INDEX idx_project_type_status (project_id, issue_type, status),
    INDEX idx_assignee (assignee_id),
    INDEX idx_duplicate_hash (deduplication_hash)
);
```

#### feature_issue_links
```sql
CREATE TABLE feature_issue_links (
    id VARCHAR(36) PRIMARY KEY,
    feature_id VARCHAR(36) NOT NULL,
    issue_id VARCHAR(36) NOT NULL,
    link_type VARCHAR(50) NOT NULL,
    -- Link types: implements, blocks, relates_to, caused_by
    created_by VARCHAR(36),
    created_at DATETIME,
    FOREIGN KEY (feature_id) REFERENCES features(id) ON DELETE CASCADE,
    FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id),
    UNIQUE (feature_id, issue_id, link_type)
);
```

#### issue_links
```sql
CREATE TABLE issue_links (
    id VARCHAR(36) PRIMARY KEY,
    source_issue_id VARCHAR(36) NOT NULL,
    target_issue_id VARCHAR(36) NOT NULL,
    link_type VARCHAR(50) NOT NULL,
    -- Link types: blocks, is_blocked_by, duplicates, is_duplicated_by, relates_to
    created_by VARCHAR(36),
    created_at DATETIME,
    FOREIGN KEY (source_issue_id) REFERENCES issues(id) ON DELETE CASCADE,
    FOREIGN KEY (target_issue_id) REFERENCES issues(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id),
    UNIQUE (source_issue_id, target_issue_id, link_type)
);
```

#### labels
```sql
CREATE TABLE labels (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) DEFAULT '#808080',   -- Hex color code
    description VARCHAR(500),
    created_at DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE (project_id, name)
);
```

#### issue_labels
```sql
CREATE TABLE issue_labels (
    issue_id VARCHAR(36),
    label_id VARCHAR(36),
    PRIMARY KEY (issue_id, label_id),
    FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE,
    FOREIGN KEY (label_id) REFERENCES labels(id) ON DELETE CASCADE
);
```

### Comments & Activity

#### comments
```sql
CREATE TABLE comments (
    id VARCHAR(36) PRIMARY KEY,
    issue_id VARCHAR(36),
    feature_id VARCHAR(36),
    user_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT false,   -- Internal notes vs public comments
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE,
    FOREIGN KEY (feature_id) REFERENCES features(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    CHECK (issue_id IS NOT NULL OR feature_id IS NOT NULL)
);
```

#### activities
```sql
CREATE TABLE activities (
    id VARCHAR(36) PRIMARY KEY,
    organization_id VARCHAR(36) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,    -- issue, feature, project, comment
    entity_id VARCHAR(36) NOT NULL,
    action_type VARCHAR(50) NOT NULL,    -- created, status_changed, assigned, etc.
    user_id VARCHAR(36),                 -- NULL for system actions
    old_value TEXT,                      -- JSON
    new_value TEXT,                      -- JSON
    additional_data TEXT,                -- JSON
    created_at DATETIME,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_entity (entity_type, entity_id)
);
```

### Phase 3: Enhanced Collaboration Tables

#### comment_mentions
```sql
CREATE TABLE comment_mentions (
    id VARCHAR(36) PRIMARY KEY,
    comment_id VARCHAR(36) NOT NULL,
    mentioned_user_id VARCHAR(36) NOT NULL,
    created_at DATETIME,
    FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE,
    FOREIGN KEY (mentioned_user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (comment_id, mentioned_user_id),
    INDEX idx_comment_mentions_comment_id (comment_id),
    INDEX idx_comment_mentions_mentioned_user_id (mentioned_user_id)
);
```

#### feature_watchers
```sql
CREATE TABLE feature_watchers (
    id VARCHAR(36) PRIMARY KEY,
    feature_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    subscription_type VARCHAR(20) DEFAULT 'manual',  -- manual, auto
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (feature_id) REFERENCES features(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (feature_id, user_id),
    INDEX idx_feature_watchers_feature_id (feature_id),
    INDEX idx_feature_watchers_user_id (user_id)
);
```

#### saved_searches
```sql
CREATE TABLE saved_searches (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    created_by VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    filter_config JSON NOT NULL,         -- Stored filter criteria
    is_shared BOOLEAN DEFAULT false,     -- Team-wide vs personal
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_saved_searches_project_id (project_id),
    INDEX idx_saved_searches_created_by (created_by),
    INDEX idx_saved_searches_is_shared (is_shared)
);
```

**Filter Config JSON Example**:
```json
{
  "status": ["new", "in_progress"],
  "priority": ["high", "critical"],
  "severity": ["blocker", "critical"],
  "assignee_id": ["user-uuid"],
  "reporter_id": ["user-uuid"],
  "component_id": ["component-uuid"],
  "sprint_id": "current",
  "labels": ["label-uuid-1", "label-uuid-2"],
  "issue_type": ["bug", "task"],
  "is_regression": true,
  "created_after": "2024-01-01T00:00:00Z",
  "created_before": "2024-12-31T23:59:59Z",
  "story_points_min": 3,
  "story_points_max": 8,
  "text_search": "authentication bug"
}
```

#### attachments
```sql
CREATE TABLE attachments (
    id VARCHAR(36) PRIMARY KEY,
    issue_id VARCHAR(36),
    feature_id VARCHAR(36),
    uploaded_by VARCHAR(36) NOT NULL,
    filename VARCHAR(500) NOT NULL,           -- Sanitized filename
    original_filename VARCHAR(500) NOT NULL,
    file_size INT NOT NULL,                   -- Bytes
    content_type VARCHAR(100) NOT NULL,       -- MIME type
    storage_path VARCHAR(1000) NOT NULL,      -- Local or S3 path
    created_at DATETIME,
    FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE,
    FOREIGN KEY (feature_id) REFERENCES features(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE,
    CHECK (issue_id IS NOT NULL OR feature_id IS NOT NULL),
    INDEX idx_attachments_issue_id (issue_id),
    INDEX idx_attachments_feature_id (feature_id),
    INDEX idx_attachments_uploaded_by (uploaded_by)
);
```

**Attachment Rules**:
- Max file size: 10 MB
- Allowed types: Images (jpg, png, gif, svg), Documents (pdf, doc, txt), Archives (zip, tar), Logs (log), Code (json, xml, yaml)
- Storage: Local filesystem (`/app/uploads/{entity_type}/{entity_id}/`) or S3 in production

---

## API Endpoints

### Base URL
- Development: `http://localhost:8003/api/v1`
- Production: `https://api.trakly.com/api/v1`

### Authentication

#### POST /auth/login
Login and receive JWT token.

**Request**:
```json
{
  "email": "admin@acme.com",
  "password": "admin123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "admin@acme.com",
    "full_name": "Admin User",
    "organization_id": "uuid",
    "roles": ["org_admin"]
  }
}
```

#### GET /auth/me
Get current user info.

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "id": "uuid",
  "email": "admin@acme.com",
  "full_name": "Admin User",
  "organization": {
    "id": "uuid",
    "name": "Acme Corp",
    "slug": "acme"
  },
  "roles": ["org_admin"],
  "permissions": ["issue.create", "project.delete", ...]
}
```

### Issues

#### POST /issues/check-duplicates
Check for duplicate issues using TF-IDF similarity.

**Request**:
```json
{
  "title": "Login button not working",
  "description": "When clicking login, nothing happens",
  "project_id": "uuid"
}
```

**Response**:
```json
{
  "similar_issues": [
    {
      "issue_key": "TRAK-42",
      "title": "Login button unresponsive",
      "similarity_score": 0.85,
      "status": "in_progress"
    }
  ],
  "has_high_similarity": true,
  "threshold": 0.7
}
```

#### POST /issues
Create a new issue.

**Request**:
```json
{
  "project_id": "uuid",
  "title": "Login button not working",
  "description": "Detailed description",
  "issue_type": "bug",
  "priority": "high",
  "severity": "major",
  "assignee_id": "uuid",
  "component_id": "uuid",
  "repro_steps": "1. Go to login page\n2. Click login\n3. Nothing happens",
  "environment": "Chrome 120, macOS 14.2",
  "labels": ["auth", "frontend"]
}
```

**Response**:
```json
{
  "id": "uuid",
  "issue_key": "TRAK-123",
  "project_id": "uuid",
  "title": "Login button not working",
  "issue_type": "bug",
  "status": "new",
  "priority": "high",
  "severity": "major",
  "created_at": "2026-01-24T10:30:00Z"
}
```

#### GET /issues?project_id={id}&status={status}&assignee_id={id}
List issues with filters.

#### GET /issues/{id}
Get issue details.

#### GET /issues/key/{key}
Get issue by key (e.g., TRAK-123).

#### PATCH /issues/{id}
Update issue.

#### DELETE /issues/{id}
Delete issue.

### Features

#### POST /features
Create feature.

#### GET /features?project_id={id}
List features.

#### GET /features/{id}
Get feature with linked issues.

#### PATCH /features/{id}
Update feature.

#### DELETE /features/{id}
Delete feature.

#### POST /features/{id}/link-issue
Link issue to feature.

**Request**:
```json
{
  "issue_id": "uuid",
  "link_type": "implements"
}
```

### Projects

#### POST /projects
Create project.

#### GET /projects
List projects for current user.

#### GET /projects/{id}
Get project details.

#### PATCH /projects/{id}
Update project.

#### POST /projects/{id}/members
Add project member.

#### DELETE /projects/{id}/members/{user_id}
Remove project member.

#### POST /projects/{id}/components
Create component.

#### GET /projects/{id}/components
List components.

### Dashboard

#### GET /dashboard/statistics
Overall statistics.

**Response**:
```json
{
  "total_issues": 150,
  "open_issues": 45,
  "bugs": 30,
  "tasks": 20,
  "features": 12,
  "issues_by_status": {
    "new": 10,
    "in_progress": 25,
    "review": 10,
    "done": 105
  }
}
```

#### GET /dashboard/bugs-per-feature
Bug counts per feature.

#### GET /dashboard/recent-issues?limit=10
Recent issues.

### Sprints

#### POST /sprints
Create a new sprint.

**Request**:
```json
{
  "project_id": "uuid",
  "name": "Sprint 1",
  "goal": "Complete user authentication",
  "start_date": "2026-01-20",
  "end_date": "2026-02-03"
}
```

**Response**:
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "name": "Sprint 1",
  "goal": "Complete user authentication",
  "start_date": "2026-01-20",
  "end_date": "2026-02-03",
  "status": "planned",
  "created_at": "2026-01-25T10:00:00Z"
}
```

#### GET /sprints?project_id={id}
List sprints for a project.

**Query Params**:
- `project_id` (required): Filter by project
- `status`: Filter by status (planned, active, completed, cancelled)

#### GET /sprints/{id}
Get sprint details with associated tasks.

**Response**:
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "name": "Sprint 1",
  "goal": "Complete user authentication",
  "start_date": "2026-01-20",
  "end_date": "2026-02-03",
  "status": "active",
  "issues": [
    {
      "id": "uuid",
      "issue_key": "TRAK-123",
      "title": "Login page",
      "status": "in_progress",
      "assignee": {...}
    }
  ],
  "created_at": "2026-01-25T10:00:00Z"
}
```

#### PATCH /sprints/{id}
Update sprint.

**Request**:
```json
{
  "name": "Sprint 1 - Updated",
  "status": "active",
  "end_date": "2026-02-05"
}
```

#### DELETE /sprints/{id}
Delete sprint.

#### POST /sprints/{id}/add-issue
Add task to sprint.

**Request**:
```json
{
  "issue_id": "uuid"
}
```

#### POST /sprints/{id}/remove-issue
Remove task from sprint.

**Request**:
```json
{
  "issue_id": "uuid"
}
```

#### GET /sprints/{id}/board
Get sprint board data grouped by status.

**Response**:
```json
{
  "sprint": {...},
  "columns": [
    {
      "status": "new",
      "issues": [...]
    },
    {
      "status": "in_progress",
      "issues": [...]
    },
    {
      "status": "done",
      "issues": [...]
    }
  ]
}
```

### Organizations

#### POST /organizations/signup
Create new organization with admin user (public endpoint).

**Request**:
```json
{
  "organization_name": "Acme Corp",
  "organization_slug": "acme",
  "admin_email": "admin@acme.com",
  "admin_password": "securepass123",
  "admin_full_name": "Admin User"
}
```

**Response**:
```json
{
  "organization": {
    "id": "uuid",
    "name": "Acme Corp",
    "slug": "acme",
    "created_at": "2026-01-25T10:00:00Z"
  },
  "user": {
    "id": "uuid",
    "email": "admin@acme.com",
    "full_name": "Admin User",
    "organization_id": "uuid"
  },
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Phase 3: Enhanced Collaboration Endpoints

#### Comments with @Mentions

**POST /comments**
Create comment with @mention support.

**Request**:
```json
{
  "issue_id": "uuid",
  "content": "Hey @[John Doe](user-uuid), please review this!",
  "parent_comment_id": null
}
```

**Response**:
```json
{
  "id": "uuid",
  "issue_id": "uuid",
  "user_id": "uuid",
  "content": "Hey @[John Doe](user-uuid), please review this!",
  "mentions": [
    {
      "id": "user-uuid",
      "full_name": "John Doe",
      "email": "john@example.com"
    }
  ],
  "author": {...},
  "created_at": "2026-01-25T10:00:00Z"
}
```

**GET /comments/{comment_id}**
Get comment details.

**PATCH /comments/{comment_id}**
Update comment.

**DELETE /comments/{comment_id}**
Delete comment (author only).

#### Feature Watchers

**POST /watchers/features/{feature_id}/subscribe**
Subscribe to feature notifications.

**DELETE /watchers/features/{feature_id}/unsubscribe**
Unsubscribe from feature.

**GET /watchers/features/{feature_id}**
Get all watchers for a feature.

**Response**:
```json
[
  {
    "id": "user-uuid",
    "full_name": "John Doe",
    "email": "john@example.com",
    "avatar_url": null
  }
]
```

#### Advanced Search & Saved Searches

**POST /search/advanced**
Execute advanced search with complex filters.

**Request**:
```json
{
  "project_id": "uuid",
  "filter_config": {
    "status": ["in_progress", "review"],
    "priority": ["high", "critical"],
    "assignee_id": ["user-uuid"],
    "created_after": "2024-01-01T00:00:00Z",
    "text_search": "authentication"
  },
  "skip": 0,
  "limit": 100
}
```

**Response**: List of IssueResponse objects

**POST /search/save**
Save a search for reuse.

**Request**:
```json
{
  "project_id": "uuid",
  "name": "High Priority Backend Issues",
  "description": "All high/critical backend bugs",
  "filter_config": {...},
  "is_shared": true
}
```

**GET /search/saved?project_id={id}**
List saved searches (personal + shared).

**GET /search/saved/{search_id}**
Get saved search details.

**GET /search/saved/{search_id}/execute?skip=0&limit=100**
Execute a saved search.

**PATCH /search/saved/{search_id}**
Update saved search (owner only).

**DELETE /search/saved/{search_id}**
Delete saved search (owner only).

#### Bulk Operations

**POST /bulk/update**
Bulk update issues.

**Request**:
```json
{
  "project_id": "uuid",
  "filter_config": {
    "status": ["new"],
    "issue_type": ["bug"]
  },
  "update_data": {
    "status": "in_progress",
    "assignee_id": "developer-uuid"
  }
}
```

**Response**:
```json
{
  "affected_count": 15,
  "issue_ids": ["issue-1", "issue-2", ...]
}
```

**POST /bulk/delete**
Bulk delete issues (Admin only).

**POST /bulk/transition**
Bulk status transition.

**Request**:
```json
{
  "project_id": "uuid",
  "filter_config": {...},
  "new_status": "done"
}
```

#### File Attachments

**POST /attachments/issues/{issue_id}**
Upload file to issue.

**Request**: `multipart/form-data` with `file` field

**Response**:
```json
{
  "id": "uuid",
  "issue_id": "uuid",
  "filename": "abc123-xyz.png",
  "original_filename": "screenshot.png",
  "file_size": 154234,
  "content_type": "image/png",
  "download_url": "/api/v1/attachments/{id}/download",
  "uploaded_by": {...},
  "created_at": "2026-01-25T10:30:00Z"
}
```

**POST /attachments/features/{feature_id}**
Upload file to feature.

**GET /attachments/{attachment_id}**
Get attachment metadata.

**GET /attachments/{attachment_id}/download**
Download file (returns `FileResponse`).

**DELETE /attachments/{attachment_id}**
Delete attachment (uploader only).

---

## Business Rules

### Project-Level Isolation

**Critical**: All data operations MUST respect project boundaries.

1. **Duplicate Detection**:
   - ONLY search within the same `project_id`
   - Never show duplicates from other projects
   - Include project_id in deduplication_hash calculation

2. **Issue Keys**:
   - Format: `{PROJECT_KEY}-{NUMBER}`
   - Issue numbers auto-increment per project
   - Example: TRAK-1, TRAK-2, MOBILE-1

3. **Components & Labels**:
   - Scoped to projects
   - Cannot be shared across projects

### Organization-Level Isolation

**Critical**: Users can ONLY access data from their organization.

1. **All queries** MUST filter by `organization_id`
2. **Cross-organization access** is NEVER allowed
3. **JWT tokens** include organization_id claim

### Issue Workflow

#### Status Transitions
```
new → in_progress → review → done → closed
                           ↓
                        wont_fix
```

**Rules**:
- Only assignee or project manager can transition to "in_progress"
- Only reporter or assignee can transition to "review"
- Only project manager can transition to "done" or "wont_fix"
- "closed" is final state (cannot reopen without admin permission)

#### Bug-Specific Rules

1. **Required Fields for Bugs**:
   - `repro_steps` (recommended, not enforced)
   - `environment` (recommended)
   - `severity` (required)

2. **Regression Detection**:
   - If `is_regression=true`, must provide `affected_version`

3. **Duplicate Marking**:
   - When marked as duplicate, must set `duplicate_of_id`
   - Automatically sets `is_duplicate=true`
   - Resolution becomes "duplicate"

### Feature-Issue Linking

#### Link Types

1. **implements**: Issue implements part of the feature
   - Use for: Tasks, Stories that build the feature

2. **blocks**: Issue blocks the feature from completion
   - Use for: Critical bugs, blockers

3. **relates_to**: Issue is related to the feature
   - Use for: General association

4. **caused_by**: Bug was caused by the feature
   - Use for: Regressions, bugs introduced by feature

#### Rules

- One issue can link to multiple features
- Link type must be specified
- Cannot create duplicate links (same feature + issue + type)
- Deleting feature removes all links (CASCADE)

### Access Control Rules

See [Security & Access Control](#security--access-control) section.

---

## Security & Access Control

### Role-Based Access Control (RBAC)

#### System Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| **org_admin** | Organization administrator | Full access to everything |
| **project_manager** | Manages projects | Create/edit projects, issues, features; Assign users; Manage workflow |
| **developer** | Development team member | Create/edit issues, Comment, Transition states |
| **reporter** | Bug reporter (QA, Customer Support) | Create issues, Comment on own issues, Read-only on others |
| **viewer** | Read-only user | View projects, issues, features (no modifications) |

#### Permission Format

Permissions follow the pattern: `resource.action`

**Resources**: `organization`, `project`, `feature`, `issue`, `comment`, `user`
**Actions**: `create`, `read`, `update`, `delete`, `assign`, `transition`

**Examples**:
- `issue.create` - Can create issues
- `project.delete` - Can delete projects
- `issue.transition` - Can change issue status
- `project.assign` - Can assign users to projects

#### Permission Checking

**In Service Layer**:
```python
def check_permission(user: User, permission: str):
    if not user.has_permission(permission):
        raise ForbiddenException(f"Missing permission: {permission}")
```

**In API Layer**:
```python
@router.post("/issues")
async def create_issue(
    data: IssueCreate,
    current_user: User = Depends(get_current_user)
):
    check_permission(current_user, "issue.create")
    # ... implementation
```

### Data Access Rules

#### Organization-Level Access

**Rule**: Users can ONLY access data from their own organization.

**Implementation**:
1. JWT token includes `organization_id` claim
2. All database queries filter by `organization_id`
3. Cross-organization queries return 403 Forbidden

**Example**:
```python
async def get_issues(project_id: str, current_user: User):
    project = await project_repo.get_by_id(project_id)
    if project.organization_id != current_user.organization_id:
        raise ForbiddenException("Access denied")
    # ... proceed
```

#### Project-Level Access

**Rule**: Users must be project members to access project data.

**Exceptions**:
- `org_admin`: Has access to all projects in organization
- `project_manager`: Can create new projects and access assigned projects

**Implementation**:
```python
async def check_project_access(project_id: str, user: User):
    # Admins have access to everything
    if user.has_role("org_admin"):
        return True

    # Check project membership
    member = await project_repo.get_member(project_id, user.id)
    if not member:
        raise ForbiddenException("Not a project member")
```

### JWT Authentication

**Token Structure**:
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "organization_id": "org_uuid",
  "exp": 1640000000
}
```

**Token Expiration**: 60 minutes (configurable)
**Refresh Strategy**: Frontend handles re-authentication on 401 response

---

## Duplicate Detection

### Algorithm: TF-IDF Similarity

#### How It Works

1. **Vectorization**:
   - Combine title + description into single text
   - Apply TF-IDF vectorization using scikit-learn
   - Store vector in `similarity_vector` field (JSON)

2. **Similarity Calculation**:
   - Fetch all issues in same project (exclude closed/duplicate)
   - Compute cosine similarity between new issue vector and existing vectors
   - Return top 5 matches with scores

3. **Thresholds**:
   - **30%**: Show in suggestions list
   - **70%**: Display warning to user

#### Implementation

**Service**: `app/services/duplicate_detection_service.py`

```python
class DuplicateDetectionService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )

    async def check_duplicates(
        self,
        title: str,
        description: str,
        project_id: str
    ) -> List[SimilarIssue]:
        # Combine text
        new_text = f"{title} {description or ''}"

        # Fetch existing issues in project
        existing = await issue_repo.get_by_project(
            project_id,
            exclude_status=['closed', 'wont_fix'],
            exclude_duplicate=True
        )

        if not existing:
            return []

        # Vectorize
        texts = [f"{i.title} {i.description or ''}" for i in existing]
        texts.append(new_text)

        vectors = self.vectorizer.fit_transform(texts)

        # Calculate similarity
        new_vector = vectors[-1]
        similarities = cosine_similarity(new_vector, vectors[:-1])[0]

        # Return top 5 matches
        results = []
        for idx, score in enumerate(similarities):
            if score >= 0.3:  # 30% threshold
                results.append({
                    'issue': existing[idx],
                    'score': float(score)
                })

        return sorted(results, key=lambda x: x['score'], reverse=True)[:5]
```

#### API Endpoint

**POST /api/v1/issues/check-duplicates**

**Request**:
```json
{
  "title": "Login button not working",
  "description": "When I click login, nothing happens",
  "project_id": "uuid"
}
```

**Response**:
```json
{
  "similar_issues": [
    {
      "issue_key": "TRAK-42",
      "title": "Login button unresponsive",
      "description": "Clicking login does not trigger action",
      "similarity_score": 0.85,
      "status": "in_progress",
      "assignee": {
        "id": "uuid",
        "full_name": "John Doe"
      }
    }
  ],
  "has_high_similarity": true,  // Any match >= 70%
  "threshold": 0.7
}
```

#### Fallback: Jaccard Similarity

If scikit-learn is unavailable, use Jaccard similarity:

```python
def jaccard_similarity(text1: str, text2: str) -> float:
    set1 = set(text1.lower().split())
    set2 = set(text2.lower().split())
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0
```

#### Performance Optimization

1. **Caching**: Cache vectorizer model per project
2. **Indexing**: Index on `deduplication_hash` for quick lookups
3. **Async**: All database queries use async/await
4. **Filtering**: Only check non-closed, non-duplicate issues

---

## Current Implementation Status

### ✅ Completed (MVP - Phase 1)

#### Backend
- [x] Database schema with all tables
- [x] SQLAlchemy models (Organization, User, Role, Project, Issue, Feature, etc.)
- [x] Alembic migrations setup
- [x] Repository layer (CRUD operations)
- [x] Service layer (business logic)
- [x] JWT authentication with bcrypt
- [x] RBAC implementation (5 system roles)
- [x] API endpoints:
  - [x] Auth (login, logout, me)
  - [x] Organizations (CRUD)
  - [x] Projects (CRUD + members + components)
  - [x] Issues (CRUD + duplicate check)
  - [x] Features (CRUD + linking)
  - [x] Users (CRUD)
  - [x] Dashboard (statistics, bugs-per-feature)
  - [x] Sprints (CRUD + issue assignment)
  - [x] Watchers (issue subscription)
  - [x] Notifications (multi-channel: in-app, email, Slack)
  - [x] Reminder Rules (scheduled notifications)
- [x] TF-IDF duplicate detection service
- [x] Feature-issue linking
- [x] Comments and activity logging
- [x] Docker Compose setup
- [x] Seed data script

#### Database
- [x] MySQL 8.0 setup
- [x] All tables created with proper relationships
- [x] Foreign keys and indexes
- [x] Cascade delete rules

#### Documentation
- [x] README with quick start
- [x] API documentation (Swagger/OpenAPI)
- [x] System prompt (this file)

### ✅ Completed (Phase 3 - Enhanced Collaboration)

**Completion Date**: 2026-01-25

#### Comments & Mentions
- [x] Comment CRUD API endpoints (POST, GET, PATCH, DELETE)
- [x] @mention parsing in comments (`@[Name](user-id)` format)
- [x] Auto-subscription for mentioned users
- [x] Notification on mention (`ISSUE_MENTIONED` event)
- [x] Comment mention tracking (`comment_mentions` table)
- [x] Parent-child comment threading support

#### Feature Watchers
- [x] Feature watcher model and repository
- [x] Subscribe/unsubscribe to features
- [x] Auto-subscription on feature comment
- [x] Get feature watchers endpoint
- [x] Notification support for feature changes

#### Advanced Search & Saved Searches
- [x] Advanced search with 20+ filter types:
  - Status, priority, severity, issue type filters
  - User filters (assignee, reporter)
  - Component, sprint, label filters
  - Date range filters (created, updated)
  - Story points range filter
  - Text search across title/description/key
  - Boolean filters (is_regression, is_duplicate)
- [x] IssueFilterBuilder with query composition
- [x] Saved searches (personal and team-wide)
- [x] Saved search CRUD operations
- [x] Execute saved searches
- [x] JSON filter configuration storage

#### Bulk Operations
- [x] Bulk update issues (status, priority, assignee, etc.)
- [x] Bulk delete issues (Admin only)
- [x] Bulk status transition
- [x] Field validation (whitelist approach)
- [x] Activity logging for bulk changes
- [x] Result tracking (affected_count, issue_ids)

#### File Attachments
- [x] Upload files to issues and features
- [x] File validation (10 MB limit, type whitelisting)
- [x] Supported types: Images, Documents, Archives, Logs, Code files
- [x] Download attachments with proper headers
- [x] Delete attachments (owner only)
- [x] Attachment metadata tracking
- [x] Local filesystem storage (`/app/uploads/`)
- [x] Cascade delete with parent entity

**New Database Tables**:
- `comment_mentions` - Track @mentions in comments
- `feature_watchers` - Feature subscription tracking
- `saved_searches` - Reusable search configurations
- `attachments` - File attachment metadata

**New API Endpoints**: 18 endpoints across 5 features
- Comments: 4 endpoints
- Feature Watchers: 3 endpoints
- Search: 6 endpoints
- Bulk Operations: 3 endpoints
- Attachments: 4 endpoints (including 2 POST for issues/features)

### ✅ Completed (Frontend Sprint Planning & Signup)

**Completion Date**: 2026-01-25

#### Sprint Planning Frontend
- [x] Sprint list page with project navigation tabs
- [x] Create sprint modal with form validation
- [x] Edit sprint modal with pre-filled data
- [x] Sprint board (Kanban view) with drag-and-drop
- [x] Backlog management
- [x] Sprint status badges (Planned, Active, Completed, Cancelled)
- [x] Assign/remove tasks from sprints
- [x] Sprint detail view with task list
- [x] Integration with tasks page (tab navigation)

**Key Components**:
- `SprintsPage.tsx` - Sprint list with create/edit modals
- `SprintBoardPage.tsx` - Kanban board with drag-drop (react-beautiful-dnd)
- `CreateSprintModal.tsx` - Create sprint form
- `EditSprintModal.tsx` - Edit sprint form

**API Integration**:
- Sprint service (`lib/services/sprints.service.ts`)
- Endpoints: list, create, update, delete, add-issue, remove-issue, get-board

#### Organization Signup
- [x] Signup page with organization creation
- [x] Multi-step form (org details + admin user)
- [x] Slug validation and formatting
- [x] Automatic login after signup
- [x] Integration with auth context
- [x] Redirect to dashboard on success

**Key Component**:
- `SignupPage.tsx` - Organization and admin user registration

**API Integration**:
- Organizations service (`lib/services/organizations.service.ts`)
- Endpoint: `POST /organizations/signup`

#### UI Component Library
- [x] **Drawer Component** (`components/ui/Drawer.tsx`)
  - Slide-out panel from right side
  - Backdrop with click-to-close
  - ESC key support
  - 4 size options (sm, md, lg, xl)
  - Scroll locking when open
  - Designed for task creation, settings, etc.

#### Terminology Update
All user-facing text updated from "Issue" to "Task":
- Dashboard: "Total Tasks", "Open Tasks", "Recent Tasks"
- Projects: "Tasks" button (instead of "Issues")
- Tasks page: "Create Task" button, "Tasks" header
- Search placeholder: "Search tasks..."
- Tab navigation: "Tasks" (instead of "Issues")

**Backend Terminology Unchanged**:
- Database: `issues` table
- API: `/issues` endpoints
- Models: `Issue` model
- Schemas: `IssueCreate`, `IssueResponse`, etc.

### 🚧 In Progress (Phase 2)

#### Frontend
- [x] React 18 + TypeScript setup with Vite
- [x] Tailwind CSS component library
- [x] Authentication flow (Login + Signup)
  - [x] Login page
  - [x] Signup page with organization creation
  - [x] JWT token management
  - [x] Protected routes
  - [x] Auth context
- [x] Dashboard
  - [x] Statistics cards (Total Projects, Total Tasks, Open Tasks, Total Features)
  - [x] Recent tasks table
- [x] Projects
  - [x] Projects list page with cards
  - [x] Navigation to Tasks and Sprints from project cards
  - [x] Project members display
- [x] Tasks (formerly "Issues" in UI)
  - [x] Tasks list page with filters and search
  - [x] Task creation page with duplicate detection
  - [x] Task detail page with full CRUD
  - [x] Task type icons and badges
  - [x] Status, priority, and severity badges
- [x] Sprint Planning
  - [x] Sprints list page
  - [x] Create sprint modal
  - [x] Edit sprint modal
  - [x] Sprint board (Kanban view with drag-drop)
  - [x] Sprint backlog management
  - [x] Assign tasks to sprints
  - [x] Sprint status tracking
- [x] UI Components
  - [x] Drawer component (slide-out from right)
  - [x] Modal component
  - [x] Badge components
  - [x] Form components
  - [x] Navigation tabs
- [x] Routing
  - [x] React Router v6 setup
  - [x] Protected routes
  - [x] Main layout with sidebar and top bar
  - [x] Project-scoped routes
- [x] API Integration
  - [x] Axios client with interceptors
  - [x] Auth service
  - [x] Projects service
  - [x] Issues/Tasks service
  - [x] Sprints service
  - [x] Dashboard service
  - [x] Organizations service
- [ ] User Management UI (Backend ready, frontend pending)
  - [ ] User list and invite
  - [ ] Role assignment
  - [ ] Project member management UI
- [ ] Features UI (Backend ready, frontend pending)
  - [ ] Feature list/roadmap view
  - [ ] Feature creation form
  - [ ] Feature-task linking UI

#### Backend Enhancements
- [ ] CSV import/export
- [ ] Webhook support
- [ ] Rate limiting
- [ ] API versioning strategy

#### User Management (Backend Complete, Frontend Pending)
The backend fully supports user management and RBAC:
- ✅ User CRUD endpoints (`POST /users`, `GET /users`, `PATCH /users/{id}`, `DELETE /users/{id}`)
- ✅ Project member management (`POST /projects/{id}/members`, `GET /projects/{id}/members`, `DELETE /projects/{id}/members/{user_id}`)
- ✅ Role-based access control with 5 system roles
- ✅ User creation with role assignment (`role_ids` parameter)
- ❌ Frontend UI not implemented (pending)

**Pending Frontend Work**:
- [ ] User management page (list users in organization)
- [ ] Invite user modal (create user with email/role)
- [ ] Project members UI (assign users to projects)
- [ ] Role selector component
- [ ] User profile settings page

### 📋 Planned (Phase 4)

#### Advanced Features
- [ ] Custom workflow editor
- [ ] Custom fields per project
- [ ] Burndown charts
- [ ] Advanced analytics and reporting
- [ ] AI-powered bug classification
- [ ] Auto-assignment based on expertise
- [ ] GitHub integration (sync issues)
- [ ] Mobile apps (iOS/Android)
- [ ] SSO/SAML authentication
- [ ] Audit log viewer

---

## Development Guidelines

### Adding a New Feature

1. **Update this document** with feature details
2. **Create database migration** if schema changes
3. **Implement in layers**:
   - Model (if new entity)
   - Repository (data access)
   - Service (business logic)
   - Schema (Pydantic validation)
   - API (endpoint)
4. **Add RBAC checks** in API layer
5. **Test** with sample data
6. **Update ROADMAP.md**

### Database Migrations

```bash
# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Review generated migration (IMPORTANT!)
cat trakly-backend/alembic/versions/{revision}.py

# Apply migration
docker-compose exec backend alembic upgrade head

# Rollback
docker-compose exec backend alembic downgrade -1
```

### Running Tests

```bash
# Backend tests
docker-compose exec backend pytest -v

# Frontend tests
cd trakly-frontend && npm test
```

---

## Deployment

### Environment Variables

**Production**:
- `DEBUG=false`
- `JWT_SECRET_KEY` = Strong random value (32+ chars)
- `MYSQL_PASSWORD` = Strong password
- `CORS_ORIGINS` = Comma-separated allowed origins
- `ENVIRONMENT=production`

### Docker Compose (Production)

Use separate `docker-compose.prod.yml` with:
- External MySQL (managed service)
- HTTPS/SSL termination
- Health checks
- Restart policies
- Volume backups

### Checklist

- [ ] Strong JWT secret
- [ ] Database backups configured
- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Monitoring and logging
- [ ] Error tracking (Sentry)

---

## Frontend Feature Summary

### ✅ Implemented Features
1. **Authentication**
   - Login with email/password
   - Organization signup (creates org + admin user)
   - JWT token management
   - Auto-redirect on unauthorized

2. **Dashboard**
   - Statistics cards (Projects, Tasks, Features)
   - Recent tasks table
   - Quick navigation

3. **Projects**
   - Project cards with member count
   - Navigate to Tasks and Sprints
   - Project filtering

4. **Tasks** (Issue Management)
   - Task list with filters (status, type, priority, assignee)
   - Search functionality
   - Create task with duplicate detection
   - Task detail view
   - Full CRUD operations
   - Type badges (Bug, Story, Task, Improvement, Sub-task)
   - Status, priority, severity indicators

5. **Sprint Planning**
   - Sprint list with status tracking
   - Create/edit sprints
   - Sprint board (Kanban)
   - Drag-and-drop task assignment
   - Backlog management
   - Sprint status: Planned, Active, Completed, Cancelled

6. **UI Components**
   - Drawer (slide-out panel)
   - Modal dialogs
   - Badges and status indicators
   - Navigation tabs
   - Form components
   - Loading states

### ❌ Not Yet Implemented
1. **User Management**
   - User list and invite
   - Project member assignment UI
   - Role management interface
   - User profile settings

2. **Features/Roadmap**
   - Feature list view
   - Feature creation
   - Feature-task linking UI
   - Roadmap timeline view

3. **Advanced Features**
   - Comments and mentions
   - File attachments UI
   - Advanced search interface
   - Saved searches
   - Bulk operations UI
   - Analytics and charts
   - Activity timeline

---

**Last Updated**: 2026-01-25
**Maintainer**: Engineering Team

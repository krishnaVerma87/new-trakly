# Trakly - Product Roadmap

**Last Updated**: 2026-01-25
**Current Phase**: Phase 2 (Frontend Development), Phase 3 Backend ✅ Complete

---

## Legend

- ✅ **Completed**: Feature is fully implemented and tested
- 🚧 **In Progress**: Currently being worked on
- 📋 **Planned**: Scheduled for future development
- 🎯 **Backlog**: Nice to have, not yet scheduled

---

## Phase 1: MVP (Backend Foundation) ✅

**Goal**: Build core backend infrastructure with all essential features for bug and feature tracking.

**Status**: Completed ✅
**Duration**: Weeks 1-4
**Completion Date**: 2026-01-24

### Organization & User Management ✅

- ✅ Multi-tenant organization model
- ✅ User authentication (JWT + bcrypt)
- ✅ RBAC with 5 system roles (Admin, PM, Developer, Reporter, Viewer)
- ✅ Role-permission mapping
- ✅ Team creation and management
- ✅ User profile management

### Project Management ✅

- ✅ Project CRUD operations
- ✅ Project key generation (e.g., TRAK, MOBILE)
- ✅ Project members management
- ✅ Component (sub-module) support
- ✅ Project-level isolation
- ✅ Default assignee configuration

### Issue Tracking ✅

- ✅ 5 issue types: Bug, Task, Sub-task, Story, Improvement
- ✅ Bug-specific fields (repro_steps, environment, stack_trace, severity)
- ✅ Issue workflow (new → in_progress → review → done → closed)
- ✅ Priority and severity levels
- ✅ Issue linking (blocks, relates_to, duplicates)
- ✅ Parent-child relationship (sub-tasks)
- ✅ Assignee and reporter tracking
- ✅ Story points and time estimation
- ✅ Resolution tracking
- ✅ Issue key generation (TRAK-123)

### Feature Tracking ✅

- ✅ First-class feature entity
- ✅ Feature lifecycle (backlog → planning → in_progress → testing → completed)
- ✅ Feature-issue linking with relationship types
- ✅ Target release and date tracking
- ✅ Progress percentage
- ✅ Feature ownership

### Duplicate Detection ✅

- ✅ TF-IDF vectorization
- ✅ Cosine similarity calculation
- ✅ Project-level duplicate search
- ✅ Real-time duplicate check API
- ✅ Configurable similarity threshold (30% suggestion, 70% warning)
- ✅ Fallback to Jaccard similarity
- ✅ Deduplication hash storage

### Labels & Comments ✅

- ✅ Project-scoped labels with colors
- ✅ Issue labeling (many-to-many)
- ✅ Comments on issues and features
- ✅ Internal vs public comments

### Activity & Audit ✅

- ✅ Activity logging for all changes
- ✅ Audit trail (old_value, new_value tracking)
- ✅ Action types (created, status_changed, assigned, etc.)

### Dashboard & Analytics ✅

- ✅ Overall statistics (total issues, open issues, by type)
- ✅ Bugs per feature metrics
- ✅ Recent issues feed
- ✅ Status distribution

### Infrastructure ✅

- ✅ FastAPI async application
- ✅ SQLAlchemy 2.0 async ORM
- ✅ MySQL 8.0 database
- ✅ Alembic migrations
- ✅ Docker Compose setup
- ✅ Seed data script
- ✅ API documentation (Swagger/OpenAPI)

---

## Phase 2: Frontend Application 🚧

**Goal**: Build complete React frontend with modern UI/UX.

**Status**: In Progress 🚧
**Duration**: Weeks 5-8
**Expected Completion**: 2026-02-21

### Authentication & Layout 🚧

- [ ] Login/logout flow
- [ ] JWT token management
- [ ] Protected routes
- [ ] User context provider
- [ ] Main layout with sidebar
- [ ] Navigation menu
- [ ] User profile dropdown
- [ ] Organization switcher (for future multi-org users)

### Project Management 📋

- [ ] Project list view
- [ ] Project creation form
- [ ] Project settings page
- [ ] Component management UI
- [ ] Project member management
- [ ] Project dashboard (overview stats)

### Issue Management 📋

- [ ] Issue list view with filters
  - [ ] Filter by status, type, priority, assignee
  - [ ] Search by title/description
  - [ ] Pagination
- [ ] Issue detail page
  - [ ] Full issue information
  - [ ] Edit inline
  - [ ] Status transitions
  - [ ] Comments section
  - [ ] Activity timeline
  - [ ] Link to features
  - [ ] Link to other issues
- [ ] Issue creation form
  - [ ] Dynamic fields based on issue type
  - [ ] Bug-specific fields (repro steps, environment, etc.)
  - [ ] Real-time duplicate detection warnings
  - [ ] Assignee picker
  - [ ] Component picker
  - [ ] Label picker with color coding
- [ ] Issue board view (Kanban)
  - [ ] Drag-and-drop status transitions
  - [ ] Swimlanes by assignee/priority

### Feature Tracking 📋

- [ ] Feature roadmap view
  - [ ] Timeline visualization
  - [ ] Progress indicators
  - [ ] Status-based grouping
- [ ] Feature detail page
  - [ ] Linked issues display
  - [ ] Bug-per-feature metrics
  - [ ] Progress tracking
  - [ ] Comments
- [ ] Feature creation/edit form
- [ ] Feature-issue link management

### User & Team Management 📋

- [ ] User list and invite
- [ ] Role assignment UI
- [ ] Team creation and management
- [ ] Team member assignment

### Dashboard 📋

- [ ] Home dashboard with widgets
  - [ ] My assigned issues
  - [ ] Recent activity
  - [ ] Quick stats
  - [ ] Bugs per feature chart
  - [ ] Issue status distribution
- [ ] Charts using Chart.js or Recharts

### UI/UX Components 📋

- [ ] Component library setup (Tailwind CSS)
- [ ] Reusable components:
  - [ ] Button, Input, Select, Textarea
  - [ ] Modal, Dropdown, Tooltip
  - [ ] Card, Badge, Tag
  - [ ] Avatar, UserPicker
  - [ ] DatePicker, ColorPicker
  - [ ] Loading states and skeletons
  - [ ] Error boundaries
  - [ ] Toast notifications

---

## Phase 3: Enhanced Collaboration (Backend) ✅

**Goal**: Add collaboration features for teams (Backend Implementation).

**Status**: Backend Complete ✅
**Duration**: 1 week
**Completion Date**: 2026-01-25

### Notifications ✅

- ✅ Multi-channel notification service (in-app, email, Slack)
- ✅ Notification preferences per user
- ✅ Event types:
  - ✅ Issue assigned to you
  - ✅ Comment on your issue
  - ✅ Mention in comment (`ISSUE_MENTIONED`)
  - ✅ Status changed on watched issue
  - ✅ New issue in watched project
- ✅ In-app notification storage
- ✅ Notification repository and service
- [ ] Real-time notifications (WebSocket or SSE) - Frontend pending

### Advanced Search ✅

- ✅ Full-text search across issues (title, description, key)
- ✅ Advanced filter builder with 20+ filter types:
  - ✅ Status, priority, severity, issue type
  - ✅ User filters (assignee, reporter)
  - ✅ Component, sprint, label filters
  - ✅ Date range filters (created, updated)
  - ✅ Story points range
  - ✅ Boolean filters (is_regression, is_duplicate)
- ✅ Saved searches (personal and team-wide)
- ✅ Execute saved searches
- ✅ IssueFilterBuilder with query composition
- [ ] Search history - Frontend pending
- [ ] Search by custom fields - Phase 4

### Bulk Operations ✅

- ✅ Bulk edit issues
  - ✅ Change status
  - ✅ Reassign
  - ✅ Change priority
  - ✅ Change severity
  - ✅ Update sprint
  - ✅ Update component
- ✅ Bulk delete (Admin only)
- ✅ Bulk transition workflow
- ✅ Activity logging for bulk changes
- ✅ Field validation (whitelist approach)

### Mentions & Watching ✅

- ✅ @mention users in comments
  - ✅ Markdown-style mention parsing (`@[Name](user-id)`)
  - ✅ CommentMention tracking table
  - ✅ Auto-subscription for mentioned users
  - ✅ Notifications on mention
- ✅ Watch/unwatch issues (implemented in Phase 2)
- ✅ Watch/unwatch features
- ✅ Watchers list on issue/feature detail
- ✅ Notify watchers on changes
- ✅ Auto-subscription on comment

### File Attachments ✅

- ✅ Upload files to issues/features
- ✅ File validation (10 MB limit, type whitelisting)
- ✅ Supported types:
  - ✅ Images: jpg, png, gif, svg, webp, bmp
  - ✅ Documents: pdf, doc, docx, txt, md, rtf
  - ✅ Spreadsheets: xls, xlsx, csv
  - ✅ Archives: zip, tar, gz, 7z, rar
  - ✅ Logs: log
  - ✅ Code: json, xml, yaml
- ✅ File storage (local filesystem: `/app/uploads/`)
- ✅ Download attachments with proper headers
- ✅ Delete attachments (owner only)
- ✅ Attachment metadata tracking
- ✅ Cascade delete with parent entity
- [ ] Image preview - Frontend pending
- [ ] S3 storage - Production deployment

**Backend Implementation**:
- ✅ 4 new database tables: `comment_mentions`, `feature_watchers`, `saved_searches`, `attachments`
- ✅ 18 new API endpoints across 5 features
- ✅ 8 new models, repositories, and services
- ✅ Complete backend infrastructure for Phase 3 features

---

## Phase 4: Workflows & Customization 📋

**Goal**: Allow teams to customize workflows and fields.

**Status**: Planned 📋
**Duration**: Weeks 13-16

### Custom Workflows 📋

- [ ] Workflow editor UI
- [ ] Custom status definitions per project
- [ ] Workflow transition rules
- [ ] Condition-based transitions
- [ ] Status categories (To Do, In Progress, Done)
- [ ] Workflow visualization

### Custom Fields 📋

- [ ] Custom field definitions per project
- [ ] Field types: text, number, date, dropdown, multi-select
- [ ] Required vs optional fields
- [ ] Field validation rules
- [ ] Custom fields in issue create/edit forms
- [ ] Custom fields in search/filter

### Templates 📋

- [ ] Issue templates
- [ ] Bug report template
- [ ] Feature request template
- [ ] Template selection on issue creation

### Time Tracking 📋

- [ ] Log time spent on issues
- [ ] Time tracking history
- [ ] Estimated vs actual time reports
- [ ] Time tracking by user
- [ ] Burndown charts

---

## Phase 5: Advanced Analytics 📋

**Goal**: Provide insights and reports for teams.

**Status**: Planned 📋
**Duration**: Weeks 17-20

### Reports & Charts 📋

- [ ] Issue velocity report
- [ ] Burndown chart
- [ ] Cumulative flow diagram
- [ ] Bug resolution time
- [ ] Feature completion rate
- [ ] Team productivity metrics
- [ ] Time-to-resolution by priority
- [ ] Regression rate tracking

### Custom Dashboards 📋

- [ ] Dashboard builder
- [ ] Widget library
- [ ] Drag-and-drop dashboard layout
- [ ] Share dashboards with team
- [ ] Export dashboard as PDF

### Export & Import 📋

- [ ] CSV export (issues, features)
- [ ] CSV import
- [ ] Bulk import validation
- [ ] Excel export
- [ ] JSON export/import

---

## Phase 6: Integrations 📋

**Goal**: Integrate with external tools.

**Status**: Planned 📋
**Duration**: Weeks 21-24

### GitHub Integration 📋

- [ ] OAuth authentication
- [ ] Sync issues with GitHub Issues
- [ ] Link pull requests to issues
- [ ] Auto-transition status on PR merge
- [ ] Show PR status on issue detail
- [ ] Bidirectional sync

### Slack Integration 📋

- [ ] Slack bot
- [ ] Post issue updates to channels
- [ ] Create issues from Slack
- [ ] Notification to Slack channels
- [ ] Slash commands (/trakly create-issue)

### Webhooks 📋

- [ ] Webhook configuration UI
- [ ] Event types (issue.created, issue.updated, etc.)
- [ ] Webhook payload customization
- [ ] Retry logic
- [ ] Webhook logs
- [ ] Webhook testing

### Jira Import 📋

- [ ] Import Jira projects
- [ ] Map Jira fields to Trakly fields
- [ ] Import issues with history
- [ ] Import users and assign roles

---

## Phase 7: AI & Automation 🎯

**Goal**: Use AI to improve productivity.

**Status**: Backlog 🎯

### AI-Powered Features 🎯

- 🎯 Auto-classify issue type (bug vs feature request)
- 🎯 Auto-assign issues based on expertise
- 🎯 Smart duplicate detection (beyond TF-IDF)
- 🎯 Suggested labels based on description
- 🎯 Sentiment analysis on comments
- 🎯 Priority prediction
- 🎯 Time estimation prediction
- 🎯 Root cause analysis suggestions

### Automation Rules 🎯

- 🎯 If-then automation rules
- 🎯 Auto-transition on conditions
- 🎯 Auto-assign based on component
- 🎯 Auto-close stale issues
- 🎯 Auto-escalate high-priority bugs
- 🎯 Scheduled automation runs

---

## Phase 8: Mobile & Enterprise 🎯

**Goal**: Expand platform reach.

**Status**: Backlog 🎯

### Mobile Apps 🎯

- 🎯 iOS app (React Native or SwiftUI)
- 🎯 Android app (React Native or Kotlin)
- 🎯 Push notifications
- 🎯 Offline mode
- 🎯 Mobile-optimized UI

### Enterprise Features 🎯

- 🎯 SSO/SAML authentication
- 🎯 Active Directory integration
- 🎯 Advanced audit logs
- 🎯 Compliance reports (SOC 2, GDPR)
- 🎯 Data retention policies
- 🎯 Multi-factor authentication (MFA)
- 🎯 IP whitelisting
- 🎯 Custom SLA definitions
- 🎯 Escalation policies

### Performance & Scale 🎯

- 🎯 Redis caching layer
- 🎯 Elasticsearch for search
- 🎯 Database read replicas
- 🎯 CDN for static assets
- 🎯 Background job queue (Celery)
- 🎯 Rate limiting per organization

---

## Summary by Status

### ✅ Completed: 103+ Features
**Phase 1 (MVP Backend)**:
- Organization & user management
- Project management (with components)
- Issue tracking (5 types: Bug, Task, Sub-task, Story, Improvement)
- Feature tracking
- Duplicate detection (TF-IDF)
- Labels, comments, activity logging
- Dashboard analytics
- Infrastructure setup (Docker, MySQL, FastAPI)

**Phase 2 (Additional Backend)**:
- Sprints management
- Issue watchers
- Multi-channel notifications (in-app, email, Slack)
- Reminder rules and scheduled jobs

**Phase 3 (Enhanced Collaboration - Backend)**:
- Comment CRUD with @mentions
- Feature watchers
- Advanced search with 20+ filters
- Saved searches (personal and shared)
- Bulk operations (update, delete, transition)
- File attachments (10 MB, multiple file types)
- 4 new database tables
- 18 new API endpoints

### 🚧 In Progress: Frontend Development
- React + TypeScript setup (Phase 2)
- Authentication flow
- Project & issue management UI
- Feature roadmap views
- Integration with Phase 3 backend APIs

### 📋 Planned: 80+ Features
- Frontend application completion (Phase 2)
- Custom workflows (Phase 4)
- Advanced analytics (Phase 5)
- Integrations (Phase 6)

### 🎯 Backlog: 20+ Features
- AI-powered features (Phase 7)
- Mobile apps (Phase 8)
- Enterprise features (Phase 8)

---

## Release Schedule

| Version | Phase | Target Date | Status |
|---------|-------|-------------|--------|
| v0.1 | MVP Backend (Phase 1) | 2026-01-24 | ✅ Released |
| v0.1.5 | Enhanced Collaboration Backend (Phase 3) | 2026-01-25 | ✅ Released |
| v0.2 | Frontend Alpha (Phase 2) | 2026-02-07 | 🚧 In Progress |
| v0.3 | Frontend Beta | 2026-02-21 | 📋 Planned |
| v1.0 | Public Launch | 2026-03-15 | 📋 Planned |
| v1.1 | Custom Workflows (Phase 4) | 2026-05-30 | 📋 Planned |
| v2.0 | Analytics (Phase 5) | 2026-07-15 | 📋 Planned |
| v2.1 | Integrations (Phase 6) | 2026-09-01 | 📋 Planned |

**Release Notes**:

**v0.1.5 - Enhanced Collaboration Backend (2026-01-25)** ✅
- Comment CRUD with @mentions and auto-subscription
- Feature watchers (subscribe/unsubscribe)
- Advanced search with 20+ filter types
- Saved searches (personal and shared)
- Bulk operations (update, delete, transition)
- File attachments (upload, download, delete)
- 4 new database tables
- 18 new API endpoints
- Complete backend infrastructure for collaboration features

**v0.1 - MVP Backend (2026-01-24)** ✅
- Multi-tenant organization model with RBAC
- Project management with components
- Issue tracking (5 types) with duplicate detection
- Feature tracking with issue linking
- Sprints and watchers
- Multi-channel notifications
- Dashboard analytics
- 56 API endpoints

---

## Feature Requests & Feedback

To request a feature or provide feedback:
1. Open an issue on GitHub
2. Tag with `feature-request` or `enhancement`
3. Provide clear use case and expected behavior

**Feature request template**:
```
**Feature**: [Short title]
**Use Case**: [Why is this needed?]
**Expected Behavior**: [What should happen?]
**Priority**: [Low/Medium/High]
```

---

**Maintained by**: Product & Engineering Team
**Review Cycle**: Bi-weekly

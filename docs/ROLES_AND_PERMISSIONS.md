# Roles and Permissions System

## Overview

Trakly uses a Role-Based Access Control (RBAC) system with predefined system roles and granular permissions. When an organization is created, 5 system roles are automatically created with specific permissions.

## System Roles

### 1. **Organization Admin** (`org_admin`)
**Description**: Organization administrator with full access

**Permissions**: ALL - Complete access to all resources and actions
- Create, read, update, delete all resources
- Manage users and assign roles
- Full organization management

**Use Case**: Organization owners, C-level executives

---

### 2. **Project Manager** (`project_manager`)
**Description**: Can manage projects, sprints, and issues

**Permissions**:
- **Issues**: create, read, update, delete, assign
- **Features**: create, read, update, delete
- **Projects**: read, update, manage_members
- **Users**: read
- **Sprints**: create, read, update, delete

**Use Case**: Team leads, scrum masters, project managers who oversee projects and teams

---

### 3. **Developer** (`developer`)
**Description**: Can create and update issues and features

**Permissions**:
- **Issues**: create, read, update
- **Features**: read, update
- **Projects**: read
- **Users**: read
- **Sprints**: read

**Use Case**: Software developers, engineers who work on issues and tasks

---

### 4. **Reporter** (`reporter`)
**Description**: Can report and view issues

**Permissions**:
- **Issues**: create, read
- **Features**: read
- **Projects**: read
- **Users**: read
- **Sprints**: read

**Use Case**: QA testers, support team, stakeholders who can report bugs and view progress

---

### 5. **Viewer** (`viewer`)
**Description**: Read-only access to projects and issues

**Permissions**:
- **Issues**: read
- **Features**: read
- **Projects**: read
- **Users**: read
- **Sprints**: read

**Use Case**: Clients, external stakeholders, observers who need visibility but not editing rights

---

## Permission Model

Permissions follow the format: `resource.action`

### Resources
- `issue` - Bug reports, tasks, stories
- `feature` - Feature requests and epics
- `project` - Projects and project settings
- `user` - User management
- `organization` - Organization settings
- `sprint` - Agile sprints

### Actions
- `create` - Create new entities
- `read` - View entities
- `update` - Modify existing entities
- `delete` - Remove entities
- `assign` - Assign issues to users
- `manage_members` - Add/remove project members
- `manage_roles` - Assign roles to users
- `manage` - Full management capabilities

## How It Works

### On Organization Creation
When a new organization is created (during signup), the system automatically:
1. Creates all 5 system roles
2. Defines permissions for each role
3. Assigns the `org_admin` role to the first user

### On Subsequent User Invites
When inviting new users, admins can assign appropriate roles based on the user's responsibilities.

### Permission Checking
The system provides helper methods to check permissions:

```python
# Check if user has specific permission
has_permission = await role_service.has_permission(
    user_roles=user.roles,
    required_permission="issue.create"
)

# Check if user can perform action on resource
can_delete = await role_service.check_permission(
    user_roles=user.roles,
    resource="project",
    action="delete"
)
```

## Custom Roles

In addition to system roles, organization admins can create custom roles with specific permission combinations to meet unique organizational needs.

**Note**: System roles cannot be deleted or renamed, but custom roles can be fully managed.

## Role Assignment Matrix

| Role | Issues | Features | Projects | Users | Organization | Sprints |
|------|--------|----------|----------|-------|--------------|---------|
| **org_admin** | Full | Full | Full | Full | Full | Full |
| **project_manager** | Full | Full | Update + Members | Read | - | Full |
| **developer** | Create/Update | Update | Read | Read | - | Read |
| **reporter** | Create/Read | Read | Read | Read | - | Read |
| **viewer** | Read | Read | Read | Read | - | Read |

## Implementation Details

### Auto-Creation Service
File: `app/services/role_service.py`

The `RoleService` class handles:
- Creating system permissions
- Creating system roles with associated permissions
- Permission checking logic

### Integration Points
1. **Signup Flow** (`app/services/auth_service.py`): Creates roles during organization creation
2. **Seed Data** (`seed_data.py`): Creates roles for development/testing
3. **API Endpoints** (`app/api/v1/roles.py`): Manages custom roles

### Database Schema
- `permissions` table: Stores all available permissions
- `roles` table: Stores roles (system and custom)
- `role_permissions` table: Many-to-many relationship
- `user_roles` table: Many-to-many relationship between users and roles

## Best Practices

1. **Assign Minimal Permissions**: Give users only the permissions they need for their role
2. **Use System Roles First**: Before creating custom roles, check if a system role fits
3. **Review Regularly**: Periodically review and audit role assignments
4. **Document Custom Roles**: When creating custom roles, clearly document their purpose and permissions

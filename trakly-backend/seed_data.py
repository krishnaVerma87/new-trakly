"""Seed data script for Trakly development."""
import asyncio
from datetime import datetime

from app.db.session import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.organization import Organization
from app.models.user import User, Role, Permission
from app.models.project import Project, Component
from app.models.team import Team
from app.core.logger import logger


async def seed_permissions():
    """Create system permissions."""
    async with AsyncSessionLocal() as db:
        permissions_data = [
            # Issue permissions
            {"name": "issue.create", "resource": "issue", "action": "create"},
            {"name": "issue.read", "resource": "issue", "action": "read"},
            {"name": "issue.update", "resource": "issue", "action": "update"},
            {"name": "issue.delete", "resource": "issue", "action": "delete"},
            # Feature permissions
            {"name": "feature.create", "resource": "feature", "action": "create"},
            {"name": "feature.read", "resource": "feature", "action": "read"},
            {"name": "feature.update", "resource": "feature", "action": "update"},
            {"name": "feature.delete", "resource": "feature", "action": "delete"},
            # Project permissions
            {"name": "project.create", "resource": "project", "action": "create"},
            {"name": "project.read", "resource": "project", "action": "read"},
            {"name": "project.update", "resource": "project", "action": "update"},
            {"name": "project.delete", "resource": "project", "action": "delete"},
            {"name": "project.manage_members", "resource": "project", "action": "manage_members"},
            # User permissions
            {"name": "user.create", "resource": "user", "action": "create"},
            {"name": "user.read", "resource": "user", "action": "read"},
            {"name": "user.update", "resource": "user", "action": "update"},
            {"name": "user.delete", "resource": "user", "action": "delete"},
        ]

        permissions = []
        for perm_data in permissions_data:
            permission = Permission(**perm_data)
            db.add(permission)
            permissions.append(permission)

        await db.commit()
        logger.info(f"Created {len(permissions)} permissions")
        return permissions


async def seed_organizations():
    """Create sample organizations."""
    async with AsyncSessionLocal() as db:
        org1 = Organization(
            name="Acme Corporation",
            slug="acme-corp",
            description="Sample organization for testing",
        )
        org2 = Organization(
            name="TechStart Inc",
            slug="techstart",
            description="Startup technology company",
        )

        db.add(org1)
        db.add(org2)
        await db.commit()
        await db.refresh(org1)
        await db.refresh(org2)

        logger.info(f"Created organizations: {org1.name}, {org2.name}")
        return [org1, org2]


async def seed_roles_and_users(organizations, permissions):
    """Create roles and users."""
    async with AsyncSessionLocal() as db:
        org1, org2 = organizations

        # Create roles for org1
        admin_role = Role(
            organization_id=org1.id,
            name="org_admin",
            description="Organization administrator",
            is_system_role=True,
        )
        db.add(admin_role)

        pm_role = Role(
            organization_id=org1.id,
            name="project_manager",
            description="Project manager",
            is_system_role=True,
        )
        db.add(pm_role)

        dev_role = Role(
            organization_id=org1.id,
            name="developer",
            description="Developer",
            is_system_role=True,
        )
        db.add(dev_role)

        await db.commit()
        await db.refresh(admin_role)
        await db.refresh(pm_role)
        await db.refresh(dev_role)

        # Assign all permissions to admin role
        for permission in permissions:
            admin_role.permissions.append(permission)

        # Assign limited permissions to PM and Dev roles
        for permission in permissions:
            if permission.resource in ["issue", "feature", "project"]:
                pm_role.permissions.append(permission)
                if permission.action != "delete":
                    dev_role.permissions.append(permission)

        await db.commit()

        # Create users
        admin_user = User(
            organization_id=org1.id,
            email="admin@acme.com",
            password_hash=get_password_hash("admin123"),
            full_name="Admin User",
        )
        admin_user.roles.append(admin_role)
        db.add(admin_user)

        pm_user = User(
            organization_id=org1.id,
            email="pm@acme.com",
            password_hash=get_password_hash("pm123"),
            full_name="Project Manager",
        )
        pm_user.roles.append(pm_role)
        db.add(pm_user)

        dev_user = User(
            organization_id=org1.id,
            email="dev@acme.com",
            password_hash=get_password_hash("dev123"),
            full_name="Developer User",
        )
        dev_user.roles.append(dev_role)
        db.add(dev_user)

        await db.commit()
        await db.refresh(admin_user)
        await db.refresh(pm_user)
        await db.refresh(dev_user)

        logger.info(f"Created users: {admin_user.email}, {pm_user.email}, {dev_user.email}")
        return admin_user, pm_user, dev_user


async def seed_projects_and_teams(organizations, users):
    """Create sample projects and teams."""
    async with AsyncSessionLocal() as db:
        org1 = organizations[0]
        admin_user, pm_user, dev_user = users

        # Create team
        team = Team(
            organization_id=org1.id,
            name="Engineering Team",
            description="Core engineering team",
            team_type="engineering",
        )
        db.add(team)
        await db.commit()
        await db.refresh(team)

        # Create projects
        project1 = Project(
            organization_id=org1.id,
            name="Trakly Platform",
            slug="trakly-platform",
            key="TRAK",
            description="Main Trakly bug tracking platform",
            lead_user_id=pm_user.id,
        )
        db.add(project1)

        project2 = Project(
            organization_id=org1.id,
            name="Mobile App",
            slug="mobile-app",
            key="MOBILE",
            description="Trakly mobile application",
            lead_user_id=pm_user.id,
        )
        db.add(project2)

        await db.commit()
        await db.refresh(project1)
        await db.refresh(project2)

        # Create components
        comp1 = Component(
            project_id=project1.id,
            name="Authentication",
            description="User authentication and authorization",
            lead_user_id=dev_user.id,
        )
        comp2 = Component(
            project_id=project1.id,
            name="Issue Tracking",
            description="Core issue tracking functionality",
            lead_user_id=dev_user.id,
        )
        db.add(comp1)
        db.add(comp2)

        await db.commit()

        logger.info(f"Created projects: {project1.name}, {project2.name}")
        logger.info(f"Created team: {team.name}")


async def main():
    """Run all seed functions."""
    logger.info("Starting seed data creation...")

    try:
        # Create in order of dependencies
        permissions = await seed_permissions()
        organizations = await seed_organizations()
        users = await seed_roles_and_users(organizations, permissions)
        await seed_projects_and_teams(organizations, users)

        logger.info("✅ Seed data created successfully!")
        logger.info("\n" + "="*50)
        logger.info("Sample Login Credentials:")
        logger.info("="*50)
        logger.info("Admin:    admin@acme.com / admin123")
        logger.info("PM:       pm@acme.com / pm123")
        logger.info("Dev:      dev@acme.com / dev123")
        logger.info("="*50 + "\n")

    except Exception as e:
        logger.error(f"Error creating seed data: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())

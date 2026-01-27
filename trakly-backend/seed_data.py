"""Seed data script for Trakly development."""
import asyncio
from datetime import datetime
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.organization import Organization
from app.models.user import User, Role, Permission
from app.models.project import Project, ProjectMember, Component
from app.models.team import Team
from app.core.logger import logger
from app.services.role_service import RoleService


async def seed_permissions():
    """Create system permissions if not exist."""
    async with AsyncSessionLocal() as db:
        # Check if exists
        stmt = select(Permission)
        result = await db.execute(stmt)
        existing_permissions = result.scalars().all()
        if existing_permissions:
            logger.info(f"Permissions already exist: {len(existing_permissions)}")
            return existing_permissions

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
        # Check existing
        stmt = select(Organization).where(Organization.slug == "acme-corp")
        result = await db.execute(stmt)
        existing = result.scalars().first()
        if existing:
            # Need both orgs for downstream functions 
            stmt2 = select(Organization).where(Organization.slug == "techstart")
            result2 = await db.execute(stmt2)
            existing2 = result2.scalars().first()
            logger.info("Organizations already exist")
            return [existing, existing2] if existing and existing2 else [existing] # Basic fallback

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
        org1 = organizations[0] # Acme

        # Use RoleService to create system roles with proper permissions
        role_service = RoleService(db)
        system_roles = await role_service.create_system_roles(org1.id)

        admin_role = system_roles.get("org_admin")
        pm_role = system_roles.get("project_manager")
        dev_role = system_roles.get("developer")

        # Check Users
        stmt_u = select(User).where(User.email == "admin@acme.com")
        admin_user = (await db.execute(stmt_u)).scalars().first()
        
        stmt_pm_u = select(User).where(User.email == "pm@acme.com")
        pm_user = (await db.execute(stmt_pm_u)).scalars().first()

        stmt_dev_u = select(User).where(User.email == "dev@acme.com")
        dev_user = (await db.execute(stmt_dev_u)).scalars().first()

        if not admin_user:
            admin_user = User(
                organization_id=org1.id,
                email="admin@acme.com",
                password_hash=get_password_hash("admin123"),
                full_name="Admin User",
            )
            admin_user.roles.append(admin_role)
            db.add(admin_user)
        
        if not pm_user:
            pm_user = User(
                organization_id=org1.id,
                email="pm@acme.com",
                password_hash=get_password_hash("pm123"),
                full_name="Project Manager",
            )
            pm_user.roles.append(pm_role)
            db.add(pm_user)

        if not dev_user:
            dev_user = User(
                organization_id=org1.id,
                email="dev@acme.com",
                password_hash=get_password_hash("dev123"),
                full_name="Developer User",
            )
            dev_user.roles.append(dev_role)
            db.add(dev_user)

        await db.commit()
        if admin_user: await db.refresh(admin_user)
        if pm_user: await db.refresh(pm_user)
        if dev_user: await db.refresh(dev_user)

        logger.info(f"Users ensured: {admin_user.email}, {pm_user.email}, {dev_user.email}")
        return admin_user, pm_user, dev_user


async def seed_projects_and_teams(organizations, users):
    """Create sample projects and teams."""
    async with AsyncSessionLocal() as db:
        org1 = organizations[0]
        admin_user, pm_user, dev_user = users

        # Create team
        stmt = select(Team).where(Team.name == "Engineering Team", Team.organization_id == org1.id)
        team = (await db.execute(stmt)).scalars().first()
        if not team:
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
        stmt_p1 = select(Project).where(Project.slug == "trakly-platform")
        project1 = (await db.execute(stmt_p1)).scalars().first()
        
        stmt_p2 = select(Project).where(Project.slug == "mobile-app")
        project2 = (await db.execute(stmt_p2)).scalars().first()

        if not project1:
            project1 = Project(
                organization_id=org1.id,
                name="Trakly Platform",
                slug="trakly-platform",
                key="TRAK",
                description="Main Trakly bug tracking platform",
                lead_user_id=pm_user.id,
            )
            db.add(project1)
        
        if not project2:
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
        if project1: await db.refresh(project1)
        if project2: await db.refresh(project2)

        # Create memberships if they don't exist
        for u in users:
            stmt_m = select(ProjectMember).where(ProjectMember.project_id == project1.id, ProjectMember.user_id == u.id)
            existing_m = (await db.execute(stmt_m)).scalars().first()
            if not existing_m:
                m = ProjectMember(
                    project_id=project1.id,
                    user_id=u.id,
                    role="admin" if u == admin_user else "member"
                )
                db.add(m)
        
        await db.commit()
        logger.info(f"Projects and memberships ensured for: {project1.name}")



async def main():
    """Run all seed functions."""
    logger.info("Starting seed data creation...")

    try:
        # Create in order of dependencies
        permissions = await seed_permissions()
        organizations = await seed_organizations()
        users = await seed_roles_and_users(organizations, permissions)
        await seed_projects_and_teams(organizations, users)

        logger.info("✅ Seed data ensured successfully!")
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

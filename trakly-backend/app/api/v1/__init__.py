"""API v1 router aggregation."""
from fastapi import APIRouter

from app.api.v1 import auth, users, organizations, projects, features, issues, dashboard, sprints, watchers, notifications, reminder_rules, comments, search, bulk, attachments, roles, time_logs, activities, saved_searches, wiki_pages, workflows

api_router = APIRouter(prefix="/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(organizations.router)
api_router.include_router(projects.router)
api_router.include_router(features.router)
api_router.include_router(issues.router)
api_router.include_router(dashboard.router)
api_router.include_router(sprints.router)
api_router.include_router(watchers.router)
api_router.include_router(notifications.router)
api_router.include_router(reminder_rules.router)
api_router.include_router(comments.router, prefix="/comments", tags=["Comments"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(bulk.router, prefix="/bulk", tags=["Bulk Operations"])
api_router.include_router(attachments.router, prefix="/attachments", tags=["Attachments"])
api_router.include_router(time_logs.router)
api_router.include_router(activities.router)
api_router.include_router(saved_searches.router)
api_router.include_router(wiki_pages.router)
api_router.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])

__all__ = ["api_router"]

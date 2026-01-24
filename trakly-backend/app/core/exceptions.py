"""Custom exception classes for Trakly."""


class TraklyException(Exception):
    """Base exception for all Trakly errors."""

    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(TraklyException):
    """Raised when a requested resource is not found (404)."""
    pass


class PermissionDeniedError(TraklyException):
    """Raised when user lacks permission for an action (403)."""
    pass


class AuthenticationError(TraklyException):
    """Raised when authentication fails (401)."""
    pass


class ValidationError(TraklyException):
    """Raised when input validation fails (400)."""
    pass


class DuplicateError(TraklyException):
    """Raised when attempting to create a duplicate resource (409)."""
    pass

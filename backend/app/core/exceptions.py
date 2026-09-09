from typing import Any, Optional
from fastapi import HTTPException, status


class NexusException(Exception):
    """Base exception for all Nexus AI errors."""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details


class EntityNotFoundException(NexusException):
    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(f"{entity_name} with identifier '{identifier}' not found.")
        self.entity_name = entity_name
        self.identifier = identifier


class TenantIsolationException(NexusException):
    """Raised when cross-tenant access is attempted or tenant context is missing."""
    def __init__(self, message: str = "Unauthorized cross-tenant access attempt detected."):
        super().__init__(message)


class PermissionDeniedException(NexusException):
    """Raised when an actor lacks the required permission for an action."""
    def __init__(self, required_permission: str):
        super().__init__(f"Permission denied: Requires '{required_permission}'.")
        self.required_permission = required_permission


class HITLApprovalRequiredException(NexusException):
    """Raised when an AI-initiated mutating action requires human sign-off."""
    def __init__(self, approval_request_id: str, message: str = "Action requires human approval."):
        super().__init__(message)
        self.approval_request_id = approval_request_id

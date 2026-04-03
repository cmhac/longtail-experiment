"""Contract models and error envelopes for auth/account workflows."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AuthErrorPayload(BaseModel):
    """Error payload returned by auth/account endpoints."""

    code: str = Field(min_length=1)
    message: str = Field(min_length=1)


class AuthErrorEnvelope(BaseModel):
    """Standardized error envelope for auth/account workflows."""

    error: AuthErrorPayload


class CurrentUserSummary(BaseModel):
    """Current authenticated account snapshot."""

    user_id: str = Field(min_length=1)
    email: str = Field(min_length=3)
    display_name: str | None = None
    account_status: Literal["active", "deactivated", "deletion_pending", "deleted"]
    is_admin: bool


class SessionSummary(BaseModel):
    """Serialized auth-session metadata for API responses."""

    session_id: str = Field(min_length=1)
    created_at: str = Field(min_length=1)
    expires_at: str = Field(min_length=1)
    session_status: Literal["active", "revoked", "expired"]
    client_label: str | None = None


class AuthSessionResponse(BaseModel):
    """Login/register response payload containing account and session metadata."""

    user: CurrentUserSummary
    session: SessionSummary


class SessionListResponse(BaseModel):
    """Authenticated user active-session listing payload."""

    items: list[SessionSummary]


class ProfileResponse(CurrentUserSummary):
    """Authenticated account profile payload."""

    updated_at: str = Field(min_length=1)


class RegisterRequest(BaseModel):
    """Registration input payload."""

    email: str = Field(min_length=3)
    password: str = Field(min_length=12)
    display_name: str | None = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    """Sign-in input payload."""

    email: str = Field(min_length=3)
    password: str = Field(min_length=1)


class UpdateProfileRequest(BaseModel):
    """Profile update input payload."""

    display_name: str | None = Field(default=None, max_length=255)


class ChangePasswordRequest(BaseModel):
    """Password change input payload."""

    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=12)


class DeletionRequestResponse(BaseModel):
    """Deletion-request acknowledgment payload."""

    user_id: str = Field(min_length=1)
    account_status: Literal["active", "deactivated", "deletion_pending", "deleted"]
    deletion_due_at: str = Field(min_length=1)


class AdminUserSummary(BaseModel):
    """Admin-visible user account metadata."""

    user_id: str = Field(min_length=1)
    email: str = Field(min_length=3)
    display_name: str | None = None
    account_status: Literal["active", "deactivated", "deletion_pending", "deleted"]
    is_admin: bool
    updated_at: str = Field(min_length=1)


class AdminUserListResponse(BaseModel):
    """Admin user-list envelope."""

    items: list[AdminUserSummary]


class UpdateUserStatusRequest(BaseModel):
    """Admin account-status update payload."""

    account_status: Literal["active", "deactivated"]


def auth_error(code: str, message: str) -> AuthErrorEnvelope:
    """Create a standard auth/account error envelope."""
    return AuthErrorEnvelope(error=AuthErrorPayload(code=code, message=message))


def validation_error(message: str) -> AuthErrorEnvelope:
    """Create a standard validation error envelope."""
    return auth_error("invalid_request", message)


def unauthorized_error(message: str = "Authentication required") -> AuthErrorEnvelope:
    """Create a standard authentication error envelope."""
    return auth_error("unauthorized", message)


def forbidden_error(message: str = "Forbidden") -> AuthErrorEnvelope:
    """Create a standard authorization error envelope."""
    return auth_error("forbidden", message)


def not_found_error(message: str) -> AuthErrorEnvelope:
    """Create a standard not-found error envelope."""
    return auth_error("not_found", message)


def conflict_error(message: str) -> AuthErrorEnvelope:
    """Create a standard conflict error envelope."""
    return auth_error("conflict", message)


def locked_error(message: str) -> AuthErrorEnvelope:
    """Create a standard lockout-state error envelope."""
    return auth_error("account_locked", message)

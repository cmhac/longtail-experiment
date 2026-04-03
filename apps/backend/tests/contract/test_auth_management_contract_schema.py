"""Foundational schema coverage for auth/account contract models."""

from __future__ import annotations

from src.contract.query.auth_management_query import (
    AdminUserListResponse,
    AuthSessionResponse,
    ChangePasswordRequest,
    DeletionRequestResponse,
    LoginRequest,
    RegisterRequest,
    SessionListResponse,
    UpdateProfileRequest,
    UpdateUserStatusRequest,
    forbidden_error,
    locked_error,
    unauthorized_error,
    validation_error,
)


def test_auth_request_models_validate_expected_shapes() -> None:
    """Validate auth/account request contracts accept expected payload shapes."""
    register = RegisterRequest.model_validate(
        {
            "email": "user@example.com",
            "password": "verysecure123",
            "display_name": "User",
        }
    )
    login = LoginRequest.model_validate(
        {
            "email": "user@example.com",
            "password": "verysecure123",
        }
    )
    profile = UpdateProfileRequest.model_validate({"display_name": "Updated"})
    password = ChangePasswordRequest.model_validate(
        {
            "current_password": "oldpassword123",
            "new_password": "newpassword123",
        }
    )
    status = UpdateUserStatusRequest.model_validate({"account_status": "deactivated"})

    assert register.email == "user@example.com"
    assert login.password == "verysecure123"
    assert profile.display_name == "Updated"
    assert password.new_password == "newpassword123"
    assert status.account_status == "deactivated"


def test_auth_response_models_validate_expected_shapes() -> None:
    """Validate auth/account response contracts serialize expected payloads."""
    session_response = AuthSessionResponse.model_validate(
        {
            "user": {
                "user_id": "user-1",
                "email": "user@example.com",
                "display_name": "User",
                "account_status": "active",
                "is_admin": False,
            },
            "session": {
                "session_id": "session-1",
                "created_at": "2026-04-02T00:00:00+00:00",
                "expires_at": "2026-05-02T00:00:00+00:00",
                "session_status": "active",
                "client_label": "Browser",
            },
        }
    )
    session_list = SessionListResponse.model_validate(
        {
            "items": [session_response.session.model_dump()],
        }
    )
    admin_users = AdminUserListResponse.model_validate(
        {
            "items": [
                {
                    "user_id": "user-1",
                    "email": "admin@example.com",
                    "display_name": "Admin",
                    "account_status": "active",
                    "is_admin": True,
                    "updated_at": "2026-04-02T00:00:00+00:00",
                }
            ]
        }
    )
    deletion_response = DeletionRequestResponse.model_validate(
        {
            "user_id": "user-1",
            "account_status": "deletion_pending",
            "deletion_due_at": "2026-04-09T00:00:00+00:00",
        }
    )

    assert session_response.user.user_id == "user-1"
    assert session_list.items[0].session_id == "session-1"
    assert admin_users.items[0].is_admin is True
    assert deletion_response.account_status == "deletion_pending"


def test_auth_error_envelopes_are_standardized() -> None:
    """Validate auth/account error envelopes expose stable error-code fields."""
    unauthorized = unauthorized_error().model_dump()
    forbidden = forbidden_error().model_dump()
    locked = locked_error("Account locked").model_dump()
    invalid = validation_error("invalid_request").model_dump()

    assert unauthorized["error"]["code"] == "unauthorized"
    assert forbidden["error"]["code"] == "forbidden"
    assert locked["error"]["code"] == "account_locked"
    assert invalid["error"]["code"] == "invalid_request"

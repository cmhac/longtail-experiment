"""Auth/account model placeholders for setup-phase imports.

Concrete SQLAlchemy entities are introduced in a later foundational task.
"""


class UserAccount:
    """Placeholder for the future user-account SQLAlchemy model."""


class CredentialRecord:
    """Placeholder for the future credential-record SQLAlchemy model."""


class AuthSession:
    """Placeholder for the future auth-session SQLAlchemy model."""


class RoleAssignment:
    """Placeholder for the future role-assignment SQLAlchemy model."""


class AccountAuditEvent:
    """Placeholder for the future account-audit-event SQLAlchemy model."""


__all__ = [
    "AccountAuditEvent",
    "AuthSession",
    "CredentialRecord",
    "RoleAssignment",
    "UserAccount",
]

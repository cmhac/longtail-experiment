"""Pipeline contract validation error types."""


class ContractValidationError(ValueError):
    """Raised when canonical payload validation fails."""


class ContractQuarantineError(ContractValidationError):
    """Raised when a payload must be quarantined for manual review."""

class DomainError(ValueError):
    """Base domain error."""


class InvalidStateTransition(DomainError):
    """Raised for invalid status transitions."""


class InvariantViolation(DomainError):
    """Raised when cross-entity invariants are violated."""


class AuthorizationError(DomainError):
    """Raised when actor is unauthorized."""

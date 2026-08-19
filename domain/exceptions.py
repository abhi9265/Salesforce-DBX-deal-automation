class InvalidTransitionError(ValueError):
    """Raised when a registration request attempts an invalid state change."""


class DomainValidationError(ValueError):
    """Raised when canonical deal data violates domain expectations."""

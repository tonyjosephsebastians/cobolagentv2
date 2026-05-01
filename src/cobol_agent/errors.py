"""SDK exceptions."""


class CobolAgentError(Exception):
    """Base exception for COBOL Agent failures."""


class ConfigurationError(CobolAgentError):
    """Raised when provider or runtime configuration is invalid."""


class UnsupportedTargetError(CobolAgentError):
    """Raised when a migration target is not supported."""

class DjsonError(Exception):
    """Base exception for djson parsing/serialization errors."""


class DjsonParseError(DjsonError):
    """Raised when djson syntax is invalid before JSON decoding."""

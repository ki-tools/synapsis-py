class SynapsisError(Exception):
    """Generic exception."""


class LoginError(SynapsisError):
    """Error raised logging into Synapse fails."""


class NotFoundError(SynapsisError):
    """Error raised when something is not found."""

class OneShotAPIError(Exception):
    """Base exception for all OneShot API errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ValidationError(OneShotAPIError):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class DatabaseError(OneShotAPIError):
    """Raised when database operations fail."""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class AuthenticationError(OneShotAPIError):
    """Raised when authentication fails."""

    def __init__(self, message: str):
        super().__init__(message, status_code=401)


class AuthorizationError(OneShotAPIError):
    """Raised when authorization fails."""

    def __init__(self, message: str):
        super().__init__(message, status_code=403)


class ServiceError(OneShotAPIError):
    """Raised when business logic fails."""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class ExternalServiceError(OneShotAPIError):
    """Raised when third-party service calls fail."""

    def __init__(self, message: str):
        super().__init__(message, status_code=502)


class ResourceNotFoundError(OneShotAPIError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str):
        super().__init__(message, status_code=404)

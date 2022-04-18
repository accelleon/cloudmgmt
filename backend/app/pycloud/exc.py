class AuthorizationError(Exception):
    """
    Exception raised when the user is not authorized to perform an action.
    """

    pass


class UnknownError(Exception):
    """
    Exception raised when the API returns an unknown error.
    """

    pass


class RateLimit(Exception):
    """
    Exception raised when the API returns a rate limit error.
    """

    pass

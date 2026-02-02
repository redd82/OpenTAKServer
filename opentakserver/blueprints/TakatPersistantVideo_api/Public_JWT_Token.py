#stored variable for access token
_TascommAccessToken: str | None = None


def get_TascommAccessToken() -> str | None:
    """Return the current JWT token (may be None)."""
    return _TascommAccessToken

def set_TascommAccessToken(token: str) -> None:
    """Update the JWT token."""
    global _TascommAccessToken
    _TascommAccessToken = token
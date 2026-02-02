#stored variable for access token
_TascommAccessToken: str | None = None
_TasscommFQDN: str = "127.0.0.1"
_Prefix_TascommAPI: str = "/devapi"

def get_TascommAccessToken() -> str | None:
    """Return the current JWT token (may be None)."""
    return _TascommAccessToken

def set_TascommAccessToken(token: str) -> None:
    """Update the JWT token."""
    global _TascommAccessToken
    _TascommAccessToken = token
    
def get_TascommFQDN() -> str:
    """Return the current Tasscomm FQDN."""
    return _TasscommFQDN

def set_TascommFQDN(fqdn: str) -> None:
    """Update the Tasscomm FQDN."""
    global _TasscommFQDN
    _TasscommFQDN = fqdn
       
def get_Prefix_TascommAPI() -> str:
    """Return the current Tasscomm API prefix."""
    return _Prefix_TascommAPI

def set_Prefix_TascommAPI(prefix: str) -> None:
    """Update the Tasscomm API prefix."""
    global _Prefix_TascommAPI
    _Prefix_TascommAPI = prefix

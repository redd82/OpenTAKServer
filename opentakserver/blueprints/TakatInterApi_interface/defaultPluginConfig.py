
import string
from pathlib import Path
import os


class DefaultPluginConfig:
    # Toggle to temporarily bypass TAKAT API auth hook
    DISABLE_TAKAT_API_AUTH: bool = True
    
    JWT_JWKS_URL: str = "https://tascomm.takat.nl/devapi/.well-known/jwks.json"
    JWT_EXPECTED_ISS: str = "https://tascomm.takat.nl"
    JWT_EXPECTED_AUD: str = "ots-api-cluster-1"
    
    # Stored variable for access token and username
    TascommAccessToken: str | None = None
    #TasscommUsername: str | None = None
    
    # Default values for Tasscomm connection
    TasscommFQDN: str = "tascomm.takat.nl"
    TasscommPort: int = 0
    verified_ssl: bool = True
    TasscommInternalIP: str = "192.168.18.102"
    TasscommInternalPort: int = 10301    
    
    # Default API prefix
    Prefix_TascommAPI: str = "/devapi"
from functools import wraps
from typing import Dict

from flask import request, abort, current_app, g
from jwt import decode, PyJWKClient

from opentakserver.blueprints.TakatInterApi_interface.defaultPluginConfig import DefaultPluginConfig as pluginConfig

_JWK_CLIENTS: Dict[str, PyJWKClient] = {}

def _get_client(jwks_url: str, cache_ttl: int = 300) -> PyJWKClient:
    if jwks_url not in _JWK_CLIENTS:
        _JWK_CLIENTS[jwks_url] = PyJWKClient(jwks_url, cache_keys=True, lifespan=cache_ttl)
    return _JWK_CLIENTS[jwks_url]


def verify_token(token: str, jwks_url: str, expected_iss: str, expected_aud: str, cache_ttl: int = 300) -> dict:
    try:
        client = _get_client(jwks_url, cache_ttl=cache_ttl)
        signing_key = client.get_signing_key_from_jwt(token)
        return decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=expected_aud,
            issuer=expected_iss,
            options={"require": ["exp", "iss", "aud", "nbf"]},
        )
    except Exception:
        abort(401)

def require_scope(required_scope: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            authz = request.headers.get("Authorization", "")
            if not authz.startswith("Bearer "):
                abort(401)
            token = authz.split(" ", 1)[1]

            cfg = current_app.config
            jwks_url = cfg.get("JWT_JWKS_URL") or pluginConfig.JWT_JWKS_URL
            expected_iss = cfg.get("JWT_EXPECTED_ISS") or pluginConfig.JWT_EXPECTED_ISS
            expected_aud = cfg.get("JWT_EXPECTED_AUD") or pluginConfig.JWT_EXPECTED_AUD

            if not jwks_url or not expected_iss or not expected_aud:
                abort(500)

            claims = verify_token(
                token,
                jwks_url=jwks_url,
                expected_iss=expected_iss,
                expected_aud=expected_aud,
            )

            scopes = claims.get("scope", []) or claims.get("scopes", [])
            if isinstance(scopes, str):
                scopes = scopes.split()
            if required_scope not in scopes:
                abort(403)

            g.claims = claims
            return fn(*args, **kwargs)
        return wrapper
    return decorator
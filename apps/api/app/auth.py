import json
import logging
from functools import lru_cache
from urllib.error import URLError
from urllib.request import urlopen

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _fetch_jwks(jwks_url: str) -> dict:
    """Fetch and cache Clerk JWKS for token signature validation."""
    with urlopen(jwks_url, timeout=5) as response:  # nosec: B310 - trusted config URL
        return json.loads(response.read().decode("utf-8"))


def _resolve_signing_key(token: str, jwks: dict):
    try:
        header = jwt.get_unverified_header(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired bearer token",
        ) from exc

    kid = header.get("kid")
    if not kid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token header missing key id",
        )

    for jwk in jwks.get("keys", []):
        if jwk.get("kid") == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to resolve signing key",
    )


def _decode_clerk_token(token: str) -> dict:
    if not settings.clerk_jwks_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server auth verification is not configured",
        )

    try:
        jwks = _fetch_jwks(settings.clerk_jwks_url)
        signing_key = _resolve_signing_key(token, jwks)
    except HTTPException:
        raise
    except (URLError, TimeoutError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to load auth signing keys",
        ) from exc

    decode_kwargs: dict = {
        "key": signing_key,
        "algorithms": ["RS256"],
        "leeway": 60,
        "options": {
            "verify_aud": bool(settings.clerk_audience),
            "verify_iss": bool(settings.clerk_issuer),
        },
    }

    if settings.clerk_audience:
        decode_kwargs["audience"] = settings.clerk_audience
    if settings.clerk_issuer:
        decode_kwargs["issuer"] = settings.clerk_issuer

    try:
        return jwt.decode(token, **decode_kwargs)
    except InvalidTokenError as exc:
        logger.warning(
            "Clerk token decode failed: %s (%s)",
            exc,
            exc.__class__.__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired bearer token",
        ) from exc


def get_current_auth_identity(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    return _decode_clerk_token(credentials.credentials)

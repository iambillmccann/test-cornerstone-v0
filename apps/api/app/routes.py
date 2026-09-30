from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_auth_identity
from app.core.config import settings
from app.db.session import get_db_session
from app.schemas import (
    AppUserProfile,
    AuthIdentityResponse,
    HealthResponse,
    VersionResponse,
)
from app.services.clerk_profile import (
    extract_display_name_from_clerk_user,
    extract_email_from_clerk_user,
    fetch_clerk_user_profile,
)
from app.services.user_bootstrap import get_or_create_local_user_with_default_workspace

router = APIRouter(prefix="/api/v1", tags=["v1"])
canonical_router = APIRouter(prefix="/api", tags=["canonical"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok")


@router.get("/ready", response_model=HealthResponse)
async def ready() -> HealthResponse:
    """Readiness check endpoint."""
    return HealthResponse(status="ready")


@router.get("/version", response_model=VersionResponse)
async def version() -> VersionResponse:
    """API version endpoint."""
    return VersionResponse(name=settings.app_name, version=settings.app_version)


@router.get("/auth/me", response_model=AuthIdentityResponse)
async def auth_me(
    identity: dict = Depends(get_current_auth_identity),
) -> AuthIdentityResponse:
    """Return the authenticated identity from the verified Clerk token."""
    return AuthIdentityResponse(
        sub=identity["sub"],
        sid=identity.get("sid"),
        iss=identity.get("iss"),
        azp=identity.get("azp"),
        email=identity.get("email"),
    )


def _resolve_identity_profile(
    identity: dict,
) -> tuple[str | None, str | None, str | None]:
    """Resolve profile fields from token claims, then fallback to Clerk API."""
    import logging

    logger = logging.getLogger(__name__)

    email = identity.get("email")
    display_name = identity.get("name")
    avatar_url = identity.get("picture")

    logger.info(
        f"[PROFILE] Initial JWT claims - email: {email}, name: {display_name}, picture: {avatar_url}"
    )

    if email and display_name and avatar_url:
        logger.info(
            "[PROFILE] All fields present in JWT claims, skipping Clerk API fallback"
        )
        return email, display_name, avatar_url

    logger.info(
        f"[PROFILE] Missing fields in JWT, attempting Clerk API fallback. clerk_secret_key: {bool(settings.clerk_secret_key)}"
    )
    if not settings.clerk_secret_key:
        logger.warning(
            "[PROFILE] CLERK_SECRET_KEY not configured, cannot fallback to Clerk API"
        )
        return email, display_name, avatar_url

    user_id = identity["sub"]
    logger.info(f"[PROFILE] Fetching profile from Clerk API for user_id: {user_id}")
    clerk_user = fetch_clerk_user_profile(user_id, settings.clerk_secret_key)
    if not clerk_user:
        logger.warning(f"[PROFILE] Clerk API returned no user for {user_id}")
        return email, display_name, avatar_url

    logger.info("[PROFILE] Clerk API returned user data, extracting fields")
    if not email:
        email = extract_email_from_clerk_user(clerk_user)
        logger.info(f"[PROFILE] Extracted email from Clerk: {email}")
    if not display_name:
        display_name = extract_display_name_from_clerk_user(clerk_user)
        logger.info(f"[PROFILE] Extracted display_name from Clerk: {display_name}")
    if not avatar_url:
        avatar_url = clerk_user.get("image_url")
        logger.info(f"[PROFILE] Extracted avatar_url from Clerk: {avatar_url}")

    logger.info(
        f"[PROFILE] Resolved profile - email: {email}, display_name: {display_name}, avatar_url: {bool(avatar_url)}"
    )
    return email, display_name, avatar_url


# Canonical app user profile endpoint (unversioned) with v1 compatibility alias.
@router.get("/me", response_model=AppUserProfile)
@canonical_router.get("/me", response_model=AppUserProfile)
async def me(
    identity: dict = Depends(get_current_auth_identity),
    db: Session = Depends(get_db_session),
) -> AppUserProfile:
    """
    Return the authenticated app user profile from local persistence.

    Ensures user is bootstrapped on first authenticated request with Clerk identity,
    then returns the persisted local user profile (id, email, display_name, avatar_url).
    """
    import logging

    logger = logging.getLogger(__name__)

    logger.info(f"[/api/me] Handling request for user: {identity['sub']}")

    email, display_name, avatar_url = _resolve_identity_profile(identity)
    logger.info(
        f"[/api/me] Profile resolution complete - email: {email}, display_name: {display_name}, avatar_url: {bool(avatar_url)}"
    )

    user = get_or_create_local_user_with_default_workspace(
        db,
        auth_provider="clerk",
        auth_provider_user_id=identity["sub"],
        email=email,
        display_name=display_name,
        avatar_url=avatar_url,
    )
    logger.info(
        f"[/api/me] User object: id={user.id}, email={user.email}, display_name={user.display_name}, avatar_url={bool(user.avatar_url)}"
    )

    profile_updated = False
    if email and not user.email:
        logger.info(f"[/api/me] Backfilling email: {email}")
        user.email = email
        profile_updated = True
    if display_name and not user.display_name:
        logger.info(f"[/api/me] Backfilling display_name: {display_name}")
        user.display_name = display_name
        profile_updated = True
    if avatar_url and not user.avatar_url:
        logger.info("[/api/me] Backfilling avatar_url")
        user.avatar_url = avatar_url
        profile_updated = True

    if profile_updated:
        logger.info("[/api/me] Profile updated, committing to DB")
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("[/api/me] DB commit successful")
    else:
        logger.info("[/api/me] No profile updates needed")

    logger.info(
        f"[/api/me] Returning profile: id={user.id}, email={user.email}, display_name={user.display_name}, avatar_url={bool(user.avatar_url)}"
    )
    return AppUserProfile(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
    )

import json
import logging
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)
API_NAME = os.getenv("API_NAME", os.getenv("APP_NAME", "cornerstone-api"))
API_VERSION = os.getenv("API_VERSION", "0.1.0")


def fetch_clerk_user_profile(user_id: str, secret_key: str) -> dict | None:
    """Fetch a Clerk user profile via Clerk backend API."""
    logger.info(f"[CLERK_API] Fetching profile for user_id: {user_id}")
    request = Request(
        url=f"https://api.clerk.com/v1/users/{user_id}",
        headers={
            "Authorization": f"Bearer {secret_key}",
            "User-Agent": f"{API_NAME}/{API_VERSION}",
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=5) as response:  # nosec: B310
            data = json.loads(response.read().decode("utf-8"))
            logger.info(f"[CLERK_API] Successfully fetched profile for {user_id}")
            return data
    except HTTPError as e:
        logger.error(
            f"[CLERK_API] HTTP error fetching profile for {user_id}: {e.code} {e.reason}"
        )
        return None
    except URLError as e:
        logger.error(
            f"[CLERK_API] URL error fetching profile for {user_id}: {e.reason}"
        )
        return None
    except TimeoutError:
        logger.error(f"[CLERK_API] Timeout fetching profile for {user_id}")
        return None
    except ValueError as e:
        logger.error(
            f"[CLERK_API] JSON decode error fetching profile for {user_id}: {e}"
        )
        return None


def extract_email_from_clerk_user(clerk_user: dict) -> str | None:
    """Extract primary email from Clerk user payload."""
    primary_id = clerk_user.get("primary_email_address_id")
    email_addresses = clerk_user.get("email_addresses", [])

    logger.info(
        f"[CLERK_EXTRACT] Extracting email - primary_id: {primary_id}, total addresses: {len(email_addresses)}"
    )

    if primary_id:
        for email in email_addresses:
            if email.get("id") == primary_id:
                extracted = email.get("email_address")
                logger.info(f"[CLERK_EXTRACT] Found primary email: {extracted}")
                return extracted

    if email_addresses:
        extracted = email_addresses[0].get("email_address")
        logger.info(f"[CLERK_EXTRACT] Using first email: {extracted}")
        return extracted

    logger.warning("[CLERK_EXTRACT] No email found in Clerk user")
    return None


def extract_display_name_from_clerk_user(clerk_user: dict) -> str | None:
    """Extract a display name from Clerk user payload."""
    first_name = clerk_user.get("first_name")
    last_name = clerk_user.get("last_name")
    username = clerk_user.get("username")

    logger.info(
        f"[CLERK_EXTRACT] Extracting name - first: {first_name}, last: {last_name}, username: {username}"
    )

    if first_name and last_name:
        display_name = f"{first_name} {last_name}"
        logger.info(f"[CLERK_EXTRACT] Using full name: {display_name}")
        return display_name
    if first_name:
        logger.info(f"[CLERK_EXTRACT] Using first name: {first_name}")
        return first_name
    if username:
        logger.info(f"[CLERK_EXTRACT] Using username: {username}")
        return username

    logger.warning("[CLERK_EXTRACT] No name found in Clerk user")
    return None

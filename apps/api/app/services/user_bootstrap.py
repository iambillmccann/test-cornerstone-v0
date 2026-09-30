from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.models.workspace import Workspace
from app.db.models.workspace_member import WorkspaceMember


def get_or_create_local_user_with_default_workspace(
    session: Session,
    *,
    auth_provider: str | None = None,
    auth_provider_user_id: str | None = None,
    email: str | None = None,
    display_name: str | None = None,
    avatar_url: str | None = None,
) -> User:
    """Get an existing app user or create one with an owner workspace membership."""

    existing_user = _find_existing_user(
        session,
        auth_provider=auth_provider,
        auth_provider_user_id=auth_provider_user_id,
        email=email,
    )
    if existing_user:
        return existing_user

    workspace_name = f"{display_name}'s Workspace" if display_name else "My Workspace"

    user = User(
        auth_provider=auth_provider,
        auth_provider_user_id=auth_provider_user_id,
        email=email,
        display_name=display_name,
        avatar_url=avatar_url,
    )
    workspace = Workspace(name=workspace_name)

    try:
        session.add(user)
        session.add(workspace)
        session.flush()

        membership = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=user.id,
            role="owner",
        )
        session.add(membership)
        session.commit()
    except IntegrityError:
        session.rollback()
        existing_user = _find_existing_user(
            session,
            auth_provider=auth_provider,
            auth_provider_user_id=auth_provider_user_id,
            email=email,
        )
        if existing_user:
            return existing_user
        raise

    session.refresh(user)
    return user


def _find_existing_user(
    session: Session,
    *,
    auth_provider: str | None,
    auth_provider_user_id: str | None,
    email: str | None,
) -> User | None:
    if auth_provider and auth_provider_user_id:
        provider_stmt = select(User).where(
            User.auth_provider == auth_provider,
            User.auth_provider_user_id == auth_provider_user_id,
        )
        provider_match = session.execute(provider_stmt).scalar_one_or_none()
        if provider_match:
            return provider_match

    if email:
        email_stmt = select(User).where(User.email == email)
        return session.execute(email_stmt).scalar_one_or_none()

    return None

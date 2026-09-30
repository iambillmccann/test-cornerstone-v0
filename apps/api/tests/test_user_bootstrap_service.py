from app.db.models.user import User
from app.db.models.workspace import Workspace
from app.db.models.workspace_member import WorkspaceMember
from app.services.user_bootstrap import get_or_create_local_user_with_default_workspace
from sqlalchemy import select


class TestUserBootstrapService:
    def test_create_new_user_creates_workspace_and_owner_membership(self, db_session):
        user = get_or_create_local_user_with_default_workspace(
            db_session,
            auth_provider="clerk",
            auth_provider_user_id="user_123",
            email="new@example.com",
            display_name="New User",
            avatar_url="https://example.com/avatar.png",
        )

        members = (
            db_session.execute(
                select(WorkspaceMember).where(WorkspaceMember.user_id == user.id)
            )
            .scalars()
            .all()
        )
        assert user.id is not None
        assert len(members) == 1
        assert members[0].role == "owner"

        workspace = db_session.execute(
            select(Workspace).where(Workspace.id == members[0].workspace_id)
        ).scalar_one()
        assert workspace.name == "New User's Workspace"

    def test_returns_existing_user_when_provider_identity_matches(self, db_session):
        first = get_or_create_local_user_with_default_workspace(
            db_session,
            auth_provider="clerk",
            auth_provider_user_id="user_abc",
            email="owner@example.com",
            display_name="Owner",
        )

        second = get_or_create_local_user_with_default_workspace(
            db_session,
            auth_provider="clerk",
            auth_provider_user_id="user_abc",
            email="different@example.com",
            display_name="Ignored",
        )

        users = db_session.execute(select(User)).scalars().all()
        workspaces = db_session.execute(select(Workspace)).scalars().all()
        memberships = db_session.execute(select(WorkspaceMember)).scalars().all()

        assert first.id == second.id
        assert len(users) == 1
        assert len(workspaces) == 1
        assert len(memberships) == 1

    def test_falls_back_to_email_lookup_when_provider_match_missing(self, db_session):
        existing = get_or_create_local_user_with_default_workspace(
            db_session,
            email="fallback@example.com",
            display_name="Fallback",
        )

        matched = get_or_create_local_user_with_default_workspace(
            db_session,
            auth_provider="clerk",
            auth_provider_user_id="user_nonexistent",
            email="fallback@example.com",
            display_name="Other Name",
        )

        users = db_session.execute(select(User)).scalars().all()
        assert existing.id == matched.id
        assert len(users) == 1

import pytest
from app.db.models.user import User
from app.db.models.workspace import Workspace
from app.db.models.workspace_member import WorkspaceMember
from sqlalchemy.exc import IntegrityError


class TestPersistenceModels:
    def test_create_user_workspace_and_membership(self, db_session):
        user = User(email="owner@example.com", display_name="Owner")
        workspace = Workspace(name="Owner's Workspace")
        db_session.add_all([user, workspace])
        db_session.flush()

        membership = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=user.id,
            role="owner",
        )
        db_session.add(membership)
        db_session.commit()

        assert user.id is not None
        assert workspace.id is not None
        assert membership.id is not None
        assert membership.role == "owner"

    def test_workspace_member_unique_constraint(self, db_session):
        user = User(email="dupe@example.com")
        workspace = Workspace(name="Duplicate Membership Workspace")
        db_session.add_all([user, workspace])
        db_session.flush()

        first = WorkspaceMember(
            workspace_id=workspace.id, user_id=user.id, role="owner"
        )
        second = WorkspaceMember(
            workspace_id=workspace.id, user_id=user.id, role="owner"
        )
        db_session.add_all([first, second])

        with pytest.raises(IntegrityError):
            db_session.flush()

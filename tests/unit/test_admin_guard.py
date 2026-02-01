"""Unit tests for admin authorization guard

Tests the admin guard dependency logic that protects admin-only endpoints.
"""
import pytest
from fastapi import HTTPException
from app.api.dependencies import get_current_admin_user
from app.models.user import User


class TestAdminGuard:
    """Test admin authorization guard dependency"""

    def test_admin_user_passes_guard(self, test_db):
        """Admin users should pass the admin guard"""
        # Create admin user
        admin_user = User(
            email="admin@example.com",
            hashed_password="hashed",
            is_admin=True
        )
        test_db.add(admin_user)
        test_db.commit()
        test_db.refresh(admin_user)

        # Admin guard should return the user
        result = get_current_admin_user(admin_user)
        assert result == admin_user
        assert result.is_admin is True

    def test_non_admin_user_blocked_by_guard(self, test_db):
        """Non-admin users should be blocked by the admin guard"""
        # Create regular user
        regular_user = User(
            email="user@example.com",
            hashed_password="hashed",
            is_admin=False
        )
        test_db.add(regular_user)
        test_db.commit()
        test_db.refresh(regular_user)

        # Admin guard should raise 403 Forbidden
        with pytest.raises(HTTPException) as exc_info:
            get_current_admin_user(regular_user)

        assert exc_info.value.status_code == 403
        assert "admin" in exc_info.value.detail.lower()

    def test_user_without_admin_field_blocked(self, test_db):
        """Users without is_admin field should be treated as non-admin"""
        # Create user with explicitly False is_admin
        user = User(
            email="user@example.com",
            hashed_password="hashed"
        )
        # Ensure is_admin defaults to False
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.is_admin is False

        # Admin guard should raise 403
        with pytest.raises(HTTPException) as exc_info:
            get_current_admin_user(user)

        assert exc_info.value.status_code == 403

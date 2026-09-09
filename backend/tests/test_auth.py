import uuid
import pytest
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.services.rbac_seeder import DEFAULT_PERMISSIONS, DEFAULT_ROLES


def test_password_hashing():
    password = "SuperSecretPassword123!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_access_token_claims():
    user_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())
    permissions = ["sales.read", "finance.create"]

    token = create_access_token(
        subject=user_id,
        organization_id=org_id,
        permissions=permissions,
    )

    claims = decode_token(token)
    assert claims["sub"] == user_id
    assert claims["org_id"] == org_id
    assert claims["permissions"] == permissions
    assert claims["type"] == "access"
    assert "exp" in claims


def test_jwt_refresh_token_claims():
    user_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())

    token = create_refresh_token(subject=user_id, organization_id=org_id)
    claims = decode_token(token)

    assert claims["sub"] == user_id
    assert claims["org_id"] == org_id
    assert claims["type"] == "refresh"
    assert "permissions" not in claims


def test_rbac_default_permissions_completeness():
    """Ensure all core modules have essential permissions registered."""
    modules = {p["module"] for p in DEFAULT_PERMISSIONS}
    expected_modules = {
        "organization",
        "users",
        "crm",
        "sales",
        "procurement",
        "inventory",
        "finance",
        "hr",
        "projects",
        "documents",
        "ai",
    }
    assert expected_modules.issubset(modules)

    # Ensure role definitions reference existing permissions
    all_perm_codes = {p["code"] for p in DEFAULT_PERMISSIONS}
    for role_name, role_info in DEFAULT_ROLES.items():
        if role_info["permissions"] != "*":
            for perm in role_info["permissions"]:
                assert perm in all_perm_codes, f"Permission {perm} in {role_name} not defined in DEFAULT_PERMISSIONS"

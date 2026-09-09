import re
import uuid
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.exceptions import NexusException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.auth import Organization, Role, User
from app.repositories.organization import OrganizationRepository
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.rbac_seeder import seed_system_permissions_and_roles


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "-", text)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.org_repo = OrganizationRepository(session)
        self.role_repo = RoleRepository(session)

    async def register_company(self, req: RegisterRequest) -> Tuple[User, Organization, TokenResponse]:
        """Atomically register a new organization and its primary Company Admin user."""
        # Check if email is taken
        existing_user = await self.user_repo.get_by_email(req.email)
        if existing_user:
            raise NexusException(f"A user with email '{req.email}' already exists.")

        # Ensure system roles/permissions exist
        await seed_system_permissions_and_roles(self.session)

        # Generate unique slug
        base_slug = slugify(req.organization_name)
        slug = base_slug
        counter = 1
        while await self.org_repo.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Create organization
        org = await self.org_repo.create(
            name=req.organization_name,
            slug=slug,
            currency=req.currency,
            timezone=req.timezone,
        )

        # Fetch Company Admin role
        admin_role = await self.role_repo.get_by_name("Company Admin")
        assigned_roles = [admin_role] if admin_role else []

        # Create user
        user = await self.user_repo.create(
            email=req.email,
            hashed_password=get_password_hash(req.password),
            first_name=req.first_name,
            last_name=req.last_name,
            organization_id=org.id,
            is_active=True,
            is_superuser=True,
            roles=assigned_roles,
        )

        # Collect permissions
        permissions = self._extract_permissions(user)

        # Issue tokens
        access_token = create_access_token(
            subject=str(user.id),
            organization_id=str(org.id),
            permissions=permissions,
        )
        refresh_token = create_refresh_token(
            subject=str(user.id),
            organization_id=str(org.id),
        )

        token_resp = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        return user, org, token_resp

    async def authenticate(self, req: LoginRequest) -> Tuple[User, TokenResponse]:
        user = await self.user_repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.hashed_password):
            raise NexusException("Invalid email or password.")

        if not user.is_active:
            raise NexusException("Account is disabled. Please contact your organization administrator.")

        permissions = self._extract_permissions(user)

        access_token = create_access_token(
            subject=str(user.id),
            organization_id=str(user.organization_id),
            permissions=permissions,
        )
        refresh_token = create_refresh_token(
            subject=str(user.id),
            organization_id=str(user.organization_id),
        )

        token_resp = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        return user, token_resp

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise NexusException("Invalid token type. Refresh token required.")

            user_id = uuid.UUID(payload["sub"])
            org_id = uuid.UUID(payload["org_id"])
        except Exception:
            raise NexusException("Invalid or expired refresh token.")

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active or user.organization_id != org_id:
            raise NexusException("User session is no longer active.")

        permissions = self._extract_permissions(user)

        new_access_token = create_access_token(
            subject=str(user.id),
            organization_id=str(org_id),
            permissions=permissions,
        )
        new_refresh_token = create_refresh_token(
            subject=str(user.id),
            organization_id=str(org_id),
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def _extract_permissions(self, user: User) -> List[str]:
        if user.is_superuser:
            return ["*"]
        perm_codes = set()
        for role in user.roles:
            for perm in role.permissions:
                perm_codes.add(perm.code)
        return sorted(list(perm_codes))

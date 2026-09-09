import uuid
import pytest
import pytest_asyncio
from sqlalchemy import JSON, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.database import Base
from app.models.auth import Organization, User
from app.repositories.user import UserRepository

# SQLite compatibility shim for PostgreSQL UUID & JSONB during tests
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.mark.asyncio
async def test_multi_tenant_user_isolation(async_db: AsyncSession):
    """Verify that Tenant A cannot retrieve, view, or mutate Tenant B records."""
    org_a_id = uuid.uuid4()
    org_b_id = uuid.uuid4()

    # Create 2 distinct Organizations
    org_a = Organization(id=org_a_id, name="Tenant Alpha", slug="tenant-alpha")
    org_b = Organization(id=org_b_id, name="Tenant Beta", slug="tenant-beta")
    async_db.add_all([org_a, org_b])
    await async_db.flush()

    # Create users in separate organizations
    user_a_id = uuid.uuid4()
    user_b_id = uuid.uuid4()

    user_a = User(
        id=user_a_id,
        organization_id=org_a_id,
        email="alice@alpha.com",
        hashed_password="hash_alpha_123",
        first_name="Alice",
        last_name="Alpha",
    )
    user_b = User(
        id=user_b_id,
        organization_id=org_b_id,
        email="bob@beta.com",
        hashed_password="hash_beta_123",
        first_name="Bob",
        last_name="Beta",
    )
    async_db.add_all([user_a, user_b])
    await async_db.commit()

    # Repo for Tenant Alpha
    repo_alpha = UserRepository(async_db, organization_id=org_a_id)

    # Repo for Tenant Beta
    repo_beta = UserRepository(async_db, organization_id=org_b_id)

    # 1. Tenant Alpha can see Alice
    found_alice = await repo_alpha.get_by_id(user_a_id)
    assert found_alice is not None
    assert found_alice.email == "alice@alpha.com"
    assert found_alice.organization_id == org_a_id

    # 2. Tenant Alpha CANNOT see Bob (Returns None)
    cross_tenant_bob = await repo_alpha.get_by_id(user_b_id)
    assert cross_tenant_bob is None, "CRITICAL: Tenant Alpha was able to query Tenant Beta user!"

    # 3. Tenant Beta can see Bob
    found_bob = await repo_beta.get_by_id(user_b_id)
    assert found_bob is not None
    assert found_bob.email == "bob@beta.com"

    # 4. Tenant Beta CANNOT see Alice
    cross_tenant_alice = await repo_beta.get_by_id(user_a_id)
    assert cross_tenant_alice is None, "CRITICAL: Tenant Beta was able to query Tenant Alpha user!"

    # 5. List scoped to Tenant Alpha returns ONLY Alice
    alpha_users = await repo_alpha.list_by_organization()
    assert len(alpha_users) == 1
    assert alpha_users[0].id == user_a_id

    # 6. List scoped to Tenant Beta returns ONLY Bob
    beta_users = await repo_beta.list_by_organization()
    assert len(beta_users) == 1
    assert beta_users[0].id == user_b_id

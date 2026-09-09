import uuid
from decimal import Decimal
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.database import Base
from app.models.auth import Organization
from app.models.crm import Customer, Lead, Opportunity
from app.schemas.crm import ContactCreate, CustomerCreate
from app.services.crm import CRMService

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
async def test_crm_customer_creation_and_contacts(async_db: AsyncSession):
    org_id = uuid.uuid4()
    org = Organization(id=org_id, name="Nexus Retail", slug="nexus-crm-test")
    async_db.add(org)
    await async_db.flush()

    service = CRMService(async_db, org_id)

    payload = CustomerCreate(
        name="Tata Consumer Products",
        email="contact@tataconsumer.com",
        customer_segment="ENTERPRISE",
        credit_limit=Decimal("2000000.00"),
        contacts=[
            ContactCreate(
                first_name="Ratan",
                last_name="Verma",
                email="ratan@tataconsumer.com",
                designation="Procurement Director",
                is_primary=True,
            )
        ],
    )

    customer = await service.create_customer(payload)
    assert customer.id is not None
    assert customer.name == "Tata Consumer Products"
    assert customer.organization_id == org_id
    assert len(customer.contacts) == 1
    assert customer.contacts[0].first_name == "Ratan"
    assert customer.contacts[0].is_primary is True


@pytest.mark.asyncio
async def test_lead_conversion_and_ai_summary(async_db: AsyncSession):
    org_id = uuid.uuid4()
    org = Organization(id=org_id, name="Nexus Retail", slug="nexus-lead-test")
    async_db.add(org)
    await async_db.flush()

    service = CRMService(async_db, org_id)

    # 1. Create a qualified Lead
    lead = await service.lead_repo.create(
        first_name="Sunil",
        last_name="Mittal",
        company_name="Bharti Retail Ltd",
        email="sunil@bhartiretail.com",
        source="REFERRAL",
        status="QUALIFIED",
        score=92.5,
    )
    assert lead.id is not None
    assert lead.status == "QUALIFIED"

    # 2. Convert Lead to Customer
    customer, updated_lead = await service.convert_lead_to_customer(lead.id)
    assert updated_lead.status == "CONVERTED"
    assert updated_lead.converted_customer_id == customer.id
    assert customer.name == "Bharti Retail Ltd"
    assert customer.email == "sunil@bhartiretail.com"

    # 3. Add an open Opportunity for customer
    opp = await service.opp_repo.create(
        customer_id=customer.id,
        title="Q4 POS Hardware Rollout",
        stage="PROPOSAL",
        amount=Decimal("1500000.00"),
        probability=75.0,
    )
    assert opp.id is not None

    # 4. Generate AI Customer 360 Summary
    ai_summary = await service.generate_customer_ai_summary(customer.id)
    assert ai_summary.customer_id == customer.id
    assert ai_summary.total_opportunities == 1
    assert ai_summary.open_pipeline_value == Decimal("1500000.00")
    assert len(ai_summary.recommended_actions) >= 1
    assert "Bharti Retail Ltd" in ai_summary.ai_summary

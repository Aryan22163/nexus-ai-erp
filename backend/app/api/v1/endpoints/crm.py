import uuid
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import RequirePermissions, get_current_tenant
from app.core.database import get_db_session
from app.models.auth import Organization
from app.repositories.crm import (
    ActivityRepository,
    CustomerRepository,
    LeadRepository,
    OpportunityRepository,
)
from app.schemas.crm import (
    ActivityCreate,
    ActivityResponse,
    CustomerAISummaryResponse,
    CustomerCreate,
    CustomerResponse,
    LeadCreate,
    LeadResponse,
    OpportunityCreate,
    OpportunityResponse,
)
from app.services.crm import CRMService

router = APIRouter(prefix="/crm", tags=["CRM & Customer 360"])


# --- Customers ---
@router.get(
    "/customers",
    response_model=List[CustomerResponse],
    dependencies=[Depends(RequirePermissions("crm.read"))],
)
async def list_customers(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    skip: int = 0,
    limit: int = 50,
) -> List[CustomerResponse]:
    repo = CustomerRepository(db, tenant.id)
    customers = await repo.list_all(skip=skip, limit=limit)
    return [CustomerResponse.model_validate(c) for c in customers]


@router.post(
    "/customers",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("crm.create"))],
)
async def create_customer(
    payload: CustomerCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> CustomerResponse:
    service = CRMService(db, tenant.id)
    customer = await service.create_customer(payload)
    return CustomerResponse.model_validate(customer)


@router.get(
    "/customers/{customer_id}",
    response_model=CustomerResponse,
    dependencies=[Depends(RequirePermissions("crm.read"))],
)
async def get_customer(
    customer_id: uuid.UUID,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> CustomerResponse:
    repo = CustomerRepository(db, tenant.id)
    customer = await repo.get_with_details(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return CustomerResponse.model_validate(customer)


@router.get(
    "/customers/{customer_id}/ai-summary",
    response_model=CustomerAISummaryResponse,
    dependencies=[Depends(RequirePermissions("crm.read"))],
)
async def get_customer_ai_summary(
    customer_id: uuid.UUID,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> CustomerAISummaryResponse:
    """Proactive AI Customer 360 overview synthesizing pipeline, touchpoints, and churn risk."""
    service = CRMService(db, tenant.id)
    return await service.generate_customer_ai_summary(customer_id)


# --- Leads ---
@router.get(
    "/leads",
    response_model=List[LeadResponse],
    dependencies=[Depends(RequirePermissions("crm.read"))],
)
async def list_leads(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[LeadResponse]:
    repo = LeadRepository(db, tenant.id)
    leads = await repo.list_all()
    return [LeadResponse.model_validate(l) for l in leads]


@router.get(
    "/leads/top-scored",
    response_model=List[LeadResponse],
    dependencies=[Depends(RequirePermissions("crm.read"))],
)
async def list_top_scored_leads(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    limit: int = 20,
) -> List[LeadResponse]:
    """AI Lead Scoring endpoint: retrieves leads ranked by closing probability."""
    repo = LeadRepository(db, tenant.id)
    leads = await repo.list_top_scored(limit=limit)
    return [LeadResponse.model_validate(l) for l in leads]


@router.post(
    "/leads",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("crm.create"))],
)
async def create_lead(
    payload: LeadCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> LeadResponse:
    repo = LeadRepository(db, tenant.id)
    lead = await repo.create(**payload.model_dump())
    return LeadResponse.model_validate(lead)


@router.post(
    "/leads/{lead_id}/convert",
    response_model=CustomerResponse,
    dependencies=[Depends(RequirePermissions("crm.update"))],
)
async def convert_lead(
    lead_id: uuid.UUID,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> CustomerResponse:
    service = CRMService(db, tenant.id)
    customer, _ = await service.convert_lead_to_customer(lead_id)
    return CustomerResponse.model_validate(customer)


# --- Opportunities ---
@router.get(
    "/opportunities",
    response_model=List[OpportunityResponse],
    dependencies=[Depends(RequirePermissions("sales.read", "crm.read"))],
)
async def list_opportunities(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[OpportunityResponse]:
    repo = OpportunityRepository(db, tenant.id)
    opps = await repo.list_all()
    return [OpportunityResponse.model_validate(o) for o in opps]


@router.post(
    "/opportunities",
    response_model=OpportunityResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("crm.create", "sales.create"))],
)
async def create_opportunity(
    payload: OpportunityCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> OpportunityResponse:
    repo = OpportunityRepository(db, tenant.id)
    opp = await repo.create(**payload.model_dump())
    return OpportunityResponse.model_validate(opp)


# --- Activities ---
@router.get(
    "/activities/{entity_type}/{entity_id}",
    response_model=List[ActivityResponse],
    dependencies=[Depends(RequirePermissions("crm.read"))],
)
async def list_entity_activities(
    entity_type: str,
    entity_id: uuid.UUID,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[ActivityResponse]:
    repo = ActivityRepository(db, tenant.id)
    activities = await repo.list_timeline(entity_type, entity_id)
    return [ActivityResponse.model_validate(a) for a in activities]


@router.post(
    "/activities",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("crm.create"))],
)
async def create_activity(
    payload: ActivityCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ActivityResponse:
    repo = ActivityRepository(db, tenant.id)
    act = await repo.create(**payload.model_dump())
    return ActivityResponse.model_validate(act)

from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import RequirePermissions, get_current_tenant
from app.core.database import get_db_session
from app.models.auth import Organization
from app.repositories.organization_masters import (
    BranchRepository,
    DepartmentRepository,
    FiscalYearRepository,
    TaxConfigurationRepository,
    WarehouseRepository,
)
from app.schemas.master_data import (
    BranchCreate,
    BranchResponse,
    DepartmentCreate,
    DepartmentResponse,
    FiscalYearCreate,
    FiscalYearResponse,
    TaxConfigurationCreate,
    TaxConfigurationResponse,
    WarehouseCreate,
    WarehouseResponse,
)

router = APIRouter(tags=["Organization Structure & Masters"])


# --- Branches ---
@router.get("/branches", response_model=List[BranchResponse])
async def list_branches(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[BranchResponse]:
    repo = BranchRepository(db, tenant.id)
    branches = await repo.list_all()
    return [BranchResponse.model_validate(b) for b in branches]


@router.post(
    "/branches",
    response_model=BranchResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("organization.update"))],
)
async def create_branch(
    payload: BranchCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> BranchResponse:
    repo = BranchRepository(db, tenant.id)
    branch = await repo.create(**payload.model_dump())
    return BranchResponse.model_validate(branch)


# --- Departments ---
@router.get("/departments", response_model=List[DepartmentResponse])
async def list_departments(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[DepartmentResponse]:
    repo = DepartmentRepository(db, tenant.id)
    departments = await repo.list_all()
    return [DepartmentResponse.model_validate(d) for d in departments]


@router.post(
    "/departments",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("organization.update"))],
)
async def create_department(
    payload: DepartmentCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> DepartmentResponse:
    repo = DepartmentRepository(db, tenant.id)
    dept = await repo.create(**payload.model_dump())
    return DepartmentResponse.model_validate(dept)


# --- Warehouses ---
@router.get("/warehouses", response_model=List[WarehouseResponse])
async def list_warehouses(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[WarehouseResponse]:
    repo = WarehouseRepository(db, tenant.id)
    warehouses = await repo.list_all()
    return [WarehouseResponse.model_validate(w) for w in warehouses]


@router.post(
    "/warehouses",
    response_model=WarehouseResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("inventory.update", "organization.update"))],
)
async def create_warehouse(
    payload: WarehouseCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> WarehouseResponse:
    repo = WarehouseRepository(db, tenant.id)
    warehouse = await repo.create(**payload.model_dump())
    return WarehouseResponse.model_validate(warehouse)


# --- Fiscal Years ---
@router.get("/fiscal-years", response_model=List[FiscalYearResponse])
async def list_fiscal_years(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[FiscalYearResponse]:
    repo = FiscalYearRepository(db, tenant.id)
    years = await repo.list_all()
    return [FiscalYearResponse.model_validate(y) for y in years]


@router.post(
    "/fiscal-years",
    response_model=FiscalYearResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("finance.approve"))],
)
async def create_fiscal_year(
    payload: FiscalYearCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> FiscalYearResponse:
    repo = FiscalYearRepository(db, tenant.id)
    fy = await repo.create(**payload.model_dump())
    return FiscalYearResponse.model_validate(fy)


# --- Taxes ---
@router.get("/taxes", response_model=List[TaxConfigurationResponse])
async def list_taxes(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[TaxConfigurationResponse]:
    repo = TaxConfigurationRepository(db, tenant.id)
    taxes = await repo.list_all()
    return [TaxConfigurationResponse.model_validate(t) for t in taxes]


@router.post(
    "/taxes",
    response_model=TaxConfigurationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("finance.approve"))],
)
async def create_tax(
    payload: TaxConfigurationCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TaxConfigurationResponse:
    repo = TaxConfigurationRepository(db, tenant.id)
    tax = await repo.create(**payload.model_dump())
    return TaxConfigurationResponse.model_validate(tax)

from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import RequirePermissions, get_current_tenant
from app.core.database import get_db_session
from app.models.auth import Organization
from app.repositories.procurement import (
    PurchaseOrderRepository,
    PurchaseReceiptRepository,
    PurchaseRequestRepository,
    SupplierRepository,
)
from app.schemas.procurement import (
    PurchaseOrderCreate,
    PurchaseOrderResponse,
    PurchaseReceiptCreate,
    PurchaseReceiptResponse,
    PurchaseRequestCreate,
    PurchaseRequestResponse,
    SupplierCreate,
    SupplierPerformanceItem,
    SupplierResponse,
)
from app.services.procurement import ProcurementService

router = APIRouter(prefix="/procurement", tags=["Procurement & Purchasing"])


# --- Suppliers ---
@router.get(
    "/suppliers",
    response_model=List[SupplierResponse],
    dependencies=[Depends(RequirePermissions("procurement.read"))],
)
async def list_suppliers(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    skip: int = 0,
    limit: int = 50,
) -> List[SupplierResponse]:
    repo = SupplierRepository(db, tenant.id)
    suppliers = await repo.list_all(skip=skip, limit=limit)
    return [SupplierResponse.model_validate(s) for s in suppliers]


@router.post(
    "/suppliers",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("procurement.create"))],
)
async def create_supplier(
    payload: SupplierCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> SupplierResponse:
    repo = SupplierRepository(db, tenant.id)
    supplier = await repo.create(**payload.model_dump())
    return SupplierResponse.model_validate(supplier)


# --- Purchase Requests ---
@router.get(
    "/requests",
    response_model=List[PurchaseRequestResponse],
    dependencies=[Depends(RequirePermissions("procurement.read"))],
)
async def list_purchase_requests(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[PurchaseRequestResponse]:
    repo = PurchaseRequestRepository(db, tenant.id)
    requests = await repo.list_all()
    return [PurchaseRequestResponse.model_validate(r) for r in requests]


@router.post(
    "/requests",
    response_model=PurchaseRequestResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("procurement.create"))],
)
async def create_purchase_request(
    payload: PurchaseRequestCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> PurchaseRequestResponse:
    service = ProcurementService(db, tenant.id)
    req = await service.create_purchase_request(payload)
    return PurchaseRequestResponse.model_validate(req)


# --- Purchase Orders ---
@router.get(
    "/orders",
    response_model=List[PurchaseOrderResponse],
    dependencies=[Depends(RequirePermissions("procurement.read"))],
)
async def list_purchase_orders(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[PurchaseOrderResponse]:
    repo = PurchaseOrderRepository(db, tenant.id)
    orders = await repo.list_all()
    return [PurchaseOrderResponse.model_validate(o) for o in orders]


@router.post(
    "/orders",
    response_model=PurchaseOrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("procurement.create"))],
)
async def create_purchase_order(
    payload: PurchaseOrderCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> PurchaseOrderResponse:
    service = ProcurementService(db, tenant.id)
    order = await service.create_purchase_order(payload)
    return PurchaseOrderResponse.model_validate(order)


# --- Purchase Receipts (GRN) ---
@router.post(
    "/receipts",
    response_model=PurchaseReceiptResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("procurement.update", "inventory.create"))],
)
async def create_purchase_receipt(
    payload: PurchaseReceiptCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> PurchaseReceiptResponse:
    service = ProcurementService(db, tenant.id)
    receipt = await service.receive_goods(payload)
    return PurchaseReceiptResponse.model_validate(receipt)


# --- Analytics ---
@router.get(
    "/analytics/supplier-performance",
    response_model=List[SupplierPerformanceItem],
    dependencies=[Depends(RequirePermissions("procurement.read"))],
)
async def get_supplier_performance(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[SupplierPerformanceItem]:
    service = ProcurementService(db, tenant.id)
    return await service.get_supplier_performance()

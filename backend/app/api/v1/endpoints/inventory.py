from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import RequirePermissions, get_current_tenant
from app.core.database import get_db_session
from app.models.auth import Organization
from app.repositories.inventory import StockEntryRepository
from app.schemas.inventory import (
    LowStockAlertItem,
    StockBalanceItem,
    StockEntryCreate,
    StockEntryResponse,
)
from app.services.inventory import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory & Warehouse Operations"])


# --- Stock Entries (Receipts, Transfers, Issues) ---
@router.get(
    "/entries",
    response_model=List[StockEntryResponse],
    dependencies=[Depends(RequirePermissions("inventory.read"))],
)
async def list_stock_entries(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[StockEntryResponse]:
    repo = StockEntryRepository(db, tenant.id)
    entries = await repo.list_all()
    return [StockEntryResponse.model_validate(e) for e in entries]


@router.post(
    "/entries",
    response_model=StockEntryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("inventory.create"))],
)
async def create_stock_entry(
    payload: StockEntryCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> StockEntryResponse:
    service = InventoryService(db, tenant.id)
    entry = await service.create_stock_entry(payload)
    return StockEntryResponse.model_validate(entry)


# --- Current Stock Balances & Valuation ---
@router.get(
    "/balances",
    response_model=List[StockBalanceItem],
    dependencies=[Depends(RequirePermissions("inventory.read"))],
)
async def get_stock_balances(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[StockBalanceItem]:
    service = InventoryService(db, tenant.id)
    return await service.get_stock_balance()


# --- Proactive AI Stockout Alerts ---
@router.get(
    "/alerts/low-stock",
    response_model=List[LowStockAlertItem],
    dependencies=[Depends(RequirePermissions("inventory.read"))],
)
async def get_low_stock_alerts(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[LowStockAlertItem]:
    """AI Low Stock Forecasting: detects products at or below reorder threshold."""
    service = InventoryService(db, tenant.id)
    return await service.get_low_stock_alerts()

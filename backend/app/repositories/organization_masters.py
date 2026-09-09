import uuid
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.organization import (
    Branch,
    Department,
    FiscalYear,
    TaxConfiguration,
    Warehouse,
)
from app.repositories.base import BaseTenantRepository


class BranchRepository(BaseTenantRepository[Branch]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Branch, session, organization_id)

    async def get_by_code(self, code: str) -> Optional[Branch]:
        stmt = select(Branch).where(
            Branch.organization_id == self.organization_id,
            Branch.code == code.upper(),
            Branch.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class DepartmentRepository(BaseTenantRepository[Department]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Department, session, organization_id)


class WarehouseRepository(BaseTenantRepository[Warehouse]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Warehouse, session, organization_id)

    async def get_by_code(self, code: str) -> Optional[Warehouse]:
        stmt = select(Warehouse).where(
            Warehouse.organization_id == self.organization_id,
            Warehouse.code == code.upper(),
            Warehouse.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class FiscalYearRepository(BaseTenantRepository[FiscalYear]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(FiscalYear, session, organization_id)

    async def get_active_fiscal_year(self) -> Optional[FiscalYear]:
        stmt = (
            select(FiscalYear)
            .where(
                FiscalYear.organization_id == self.organization_id,
                FiscalYear.is_closed.is_(False),
                FiscalYear.is_deleted.is_(False),
            )
            .order_by(FiscalYear.start_date.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class TaxConfigurationRepository(BaseTenantRepository[TaxConfiguration]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(TaxConfiguration, session, organization_id)

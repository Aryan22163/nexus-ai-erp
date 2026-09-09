import uuid
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.crm import Activity, Contact, Customer, Lead, Opportunity
from app.repositories.base import BaseTenantRepository


class CustomerRepository(BaseTenantRepository[Customer]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Customer, session, organization_id)

    async def get_with_details(self, customer_id: uuid.UUID) -> Optional[Customer]:
        stmt = (
            select(Customer)
            .options(
                selectinload(Customer.contacts),
                selectinload(Customer.opportunities),
            )
            .where(
                Customer.id == customer_id,
                Customer.organization_id == self.organization_id,
                Customer.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Customer]:
        stmt = select(Customer).where(
            Customer.organization_id == self.organization_id,
            Customer.email == email.lower(),
            Customer.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class ContactRepository(BaseTenantRepository[Contact]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Contact, session, organization_id)

    async def list_by_customer(self, customer_id: uuid.UUID) -> Sequence[Contact]:
        stmt = select(Contact).where(
            Contact.organization_id == self.organization_id,
            Contact.customer_id == customer_id,
            Contact.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class LeadRepository(BaseTenantRepository[Lead]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Lead, session, organization_id)

    async def list_top_scored(self, limit: int = 20) -> Sequence[Lead]:
        """Fetch prioritized leads for the sales team sorted by AI score."""
        stmt = (
            select(Lead)
            .where(
                Lead.organization_id == self.organization_id,
                Lead.status.in_(["NEW", "CONTACTED", "QUALIFIED"]),
                Lead.is_deleted.is_(False),
            )
            .order_by(Lead.score.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class OpportunityRepository(BaseTenantRepository[Opportunity]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Opportunity, session, organization_id)

    async def list_by_customer(self, customer_id: uuid.UUID) -> Sequence[Opportunity]:
        stmt = select(Opportunity).where(
            Opportunity.organization_id == self.organization_id,
            Opportunity.customer_id == customer_id,
            Opportunity.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_stage(self, stage: str) -> Sequence[Opportunity]:
        stmt = select(Opportunity).where(
            Opportunity.organization_id == self.organization_id,
            Opportunity.stage == stage.upper(),
            Opportunity.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class ActivityRepository(BaseTenantRepository[Activity]):
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        super().__init__(Activity, session, organization_id)

    async def list_timeline(self, entity_type: str, entity_id: uuid.UUID) -> Sequence[Activity]:
        stmt = (
            select(Activity)
            .where(
                Activity.organization_id == self.organization_id,
                Activity.entity_type == entity_type.upper(),
                Activity.entity_id == entity_id,
                Activity.is_deleted.is_(False),
            )
            .order_by(Activity.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

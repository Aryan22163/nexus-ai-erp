import uuid
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundException, NexusException
from app.models.crm import Activity, Contact, Customer, Lead, Opportunity
from app.repositories.crm import (
    ActivityRepository,
    ContactRepository,
    CustomerRepository,
    LeadRepository,
    OpportunityRepository,
)
from app.schemas.crm import (
    CustomerAISummaryResponse,
    CustomerCreate,
    CustomerUpdate,
    LeadCreate,
)


class CRMService:
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        self.session = session
        self.organization_id = organization_id
        self.customer_repo = CustomerRepository(session, organization_id)
        self.contact_repo = ContactRepository(session, organization_id)
        self.lead_repo = LeadRepository(session, organization_id)
        self.opp_repo = OpportunityRepository(session, organization_id)
        self.activity_repo = ActivityRepository(session, organization_id)

    async def create_customer(self, payload: CustomerCreate) -> Customer:
        # Check if email is duplicate within tenant
        if payload.email:
            existing = await self.customer_repo.get_by_email(payload.email)
            if existing:
                raise NexusException(f"Customer with email '{payload.email}' already exists in this organization.")

        cust_data = payload.model_dump(exclude={"contacts"})
        cust_data["organization_id"] = self.organization_id
        customer = Customer(**cust_data)
        self.session.add(customer)
        await self.session.flush()

        for contact_data in payload.contacts:
            contact = Contact(
                organization_id=self.organization_id,
                customer_id=customer.id,
                **contact_data.model_dump(),
            )
            self.session.add(contact)

        await self.session.flush()
        return await self.customer_repo.get_with_details(customer.id)

    async def convert_lead_to_customer(self, lead_id: uuid.UUID) -> Tuple[Customer, Lead]:
        lead = await self.lead_repo.get_by_id(lead_id)
        if not lead:
            raise EntityNotFoundException("Lead", lead_id)
        if lead.status == "CONVERTED":
            raise NexusException("Lead is already converted.")

        company_name = lead.company_name or f"{lead.first_name} {lead.last_name}"
        customer = Customer(
            organization_id=self.organization_id,
            name=company_name,
            email=lead.email,
            phone=lead.phone,
            customer_segment="SMB",
            credit_limit=Decimal("50000.00"),
        )
        self.session.add(customer)
        await self.session.flush()

        # Add primary contact
        contact = Contact(
            organization_id=self.organization_id,
            customer_id=customer.id,
            first_name=lead.first_name,
            last_name=lead.last_name,
            email=lead.email,
            phone=lead.phone,
            is_primary=True,
        )
        self.session.add(contact)

        # Update lead status
        lead.status = "CONVERTED"
        lead.converted_customer_id = customer.id
        await self.session.flush()

        # Log conversion activity
        activity = Activity(
            organization_id=self.organization_id,
            entity_type="CUSTOMER",
            entity_id=customer.id,
            activity_type="NOTE",
            title="Lead Converted to Customer",
            details=f"Converted from Lead #{lead.id} ({lead.first_name} {lead.last_name}). Source: {lead.source}",
        )
        self.session.add(activity)
        await self.session.flush()

        return customer, lead

    async def generate_customer_ai_summary(self, customer_id: uuid.UUID) -> CustomerAISummaryResponse:
        """AI-powered Customer 360 summary synthesizing timeline, pipeline, and churn risk."""
        customer = await self.customer_repo.get_with_details(customer_id)
        if not customer:
            raise EntityNotFoundException("Customer", customer_id)

        opportunities = customer.opportunities or []
        activities = await self.activity_repo.list_timeline("CUSTOMER", customer_id)

        open_pipeline_val = sum(
            Decimal(str(opp.amount))
            for opp in opportunities
            if opp.stage not in ["CLOSED_WON", "CLOSED_LOST"]
        )

        # Construct analytical summary
        recs = []
        if customer.churn_risk_score > 0.6:
            recs.append("Schedule urgent retention call; churn probability exceeds 60%.")
        if open_pipeline_val > Decimal("100000.00"):
            recs.append(f"Prioritize closing open pipeline worth ₹{open_pipeline_val:,.2f}.")
        if not activities:
            recs.append("No touchpoints logged in recent timeline. Initiate relationship follow-up.")
        else:
            recs.append("Review last activity notes and set follow-up task.")

        summary_text = (
            f"Customer '{customer.name}' is an {customer.customer_segment} account with "
            f"{len(opportunities)} total deals (₹{open_pipeline_val:,.2f} active pipeline). "
            f"Churn risk score is currently assessed at {customer.churn_risk_score:.2f}."
        )

        return CustomerAISummaryResponse(
            customer_id=customer.id,
            customer_name=customer.name,
            segment=customer.customer_segment,
            churn_risk=customer.churn_risk_score,
            total_opportunities=len(opportunities),
            open_pipeline_value=open_pipeline_val,
            recent_activities_count=len(activities),
            ai_summary=summary_text,
            recommended_actions=recs,
        )

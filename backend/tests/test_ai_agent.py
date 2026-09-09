import uuid
from decimal import Decimal
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.ai.agents.orchestrator import AICopilotOrchestrator
from app.core.database import Base
from app.models.approval import ApprovalRequest
from app.models.audit import AuditLog
from app.models.auth import Organization, User
from app.models.crm import Customer
from app.models.organization import Warehouse
from app.models.sales import Product
from app.repositories.approval import ApprovalRepository
from app.schemas.ai import AICopilotRequest, ApprovalReviewAction
from app.schemas.finance import JournalEntryCreate, JournalEntryLineBase
from app.services.finance import FinanceService
from app.services.rag_engine import RAGEngineService

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
async def test_ai_copilot_financial_query_and_tool_execution(async_db: AsyncSession):
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    org = Organization(id=org_id, name="Nexus Retail", slug="nexus-ai-test")
    user = User(
        id=user_id,
        organization_id=org_id,
        email="cfo@nexusretail.com",
        first_name="Anita",
        last_name="Roy",
        hashed_password="hash",
    )
    async_db.add_all([org, user])
    await async_db.flush()

    # Seed finance accounts & post revenue
    finance_svc = FinanceService(async_db, org_id)
    await finance_svc.account_repo.seed_chart_of_accounts()
    bank = await finance_svc.account_repo.get_by_code("1020")
    sales = await finance_svc.account_repo.get_by_code("4010")

    await finance_svc.create_journal_entry(
        JournalEntryCreate(
            narration="Q3 Software Subscription Revenue",
            lines=[
                JournalEntryLineBase(account_id=bank.id, debit=Decimal("250000.00"), credit=Decimal("0.00")),
                JournalEntryLineBase(account_id=sales.id, debit=Decimal("0.00"), credit=Decimal("250000.00")),
            ],
        )
    )

    orchestrator = AICopilotOrchestrator(
        session=async_db,
        organization_id=org_id,
        user_id=user_id,
        user_permissions=["finance.read", "ai.copilot"],
    )

    # Ask Copilot about financial performance
    res = await orchestrator.process_prompt(
        AICopilotRequest(prompt="What was our total revenue and net operating profit this quarter?")
    )
    assert res.intent == "FINANCIAL_ANALYSIS"
    assert "get_financial_summary" in res.executed_tools
    assert "250,000.00" in res.reply
    assert res.action_proposal is None


@pytest.mark.asyncio
async def test_ai_copilot_hitl_action_proposal_and_approval(async_db: AsyncSession):
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    org = Organization(id=org_id, name="Nexus Retail", slug="nexus-hitl-test")
    user = User(
        id=user_id,
        organization_id=org_id,
        email="ops.manager@nexusretail.com",
        first_name="Karan",
        last_name="Johar",
        hashed_password="hash",
    )
    async_db.add_all([org, user])
    await async_db.flush()

    orchestrator = AICopilotOrchestrator(
        session=async_db,
        organization_id=org_id,
        user_id=user_id,
        user_permissions=["procurement.create", "ai.copilot", "ai.execute_actions"],
    )

    # 1. Ask Copilot to draft a PO -> Must NOT execute immediately, must propose HITL card
    prompt_res = await orchestrator.process_prompt(
        AICopilotRequest(prompt="Draft a purchase order to restock 50 units of SKU-ALERT-1 immediately.")
    )
    assert prompt_res.intent == "ACTION_PROPOSAL"
    assert prompt_res.action_proposal is not None
    assert prompt_res.action_proposal.action_type == "CREATE_PURCHASE_ORDER"
    assert prompt_res.action_proposal.status == "PENDING"
    approval_id = prompt_res.action_proposal.approval_request_id

    # 2. Check DB: Verify ApprovalRequest is in PENDING status
    approval_repo = ApprovalRepository(async_db, org_id)
    pending_list = await approval_repo.list_pending()
    assert len(pending_list) == 1
    assert pending_list[0].id == approval_id

    # 3. Human User reviews and Approves the proposal
    approval_record = await approval_repo.get_by_id(approval_id)
    approval_record.status = "APPROVED"
    approval_record.reviewed_by_id = user_id
    approval_record.execution_result = {"status": "EXECUTED", "order_id": "PO-1002"}

    # Audit log creation
    audit_entry = AuditLog(
        organization_id=org_id,
        actor_id=user_id,
        action="HITL_APPROVED",
        resource_type="ApprovalRequest",
        resource_id=str(approval_id),
        before_state={"status": "PENDING"},
        after_state={"status": "APPROVED"},
        is_ai_initiated=True,
    )
    async_db.add(audit_entry)
    await async_db.commit()

    # 4. Verify Approval status is now APPROVED and no longer in pending list
    refreshed_pending = await approval_repo.list_pending()
    assert len(refreshed_pending) == 0

    # 5. Verify immutable Audit Log trail exists
    audit_stmt = select(AuditLog).where(AuditLog.organization_id == org_id)
    audit_res = await async_db.execute(audit_stmt)
    logs = audit_res.scalars().all()
    assert len(logs) == 1
    assert logs[0].action == "HITL_APPROVED"
    assert logs[0].is_ai_initiated is True

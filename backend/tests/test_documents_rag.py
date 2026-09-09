import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.database import Base
from app.models.auth import Organization
from app.schemas.documents import RAGSearchRequest
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
async def test_document_ingestion_chunking_and_rag_search(async_db: AsyncSession):
    org_id = uuid.uuid4()
    org = Organization(id=org_id, name="Nexus Retail", slug="nexus-rag-test")
    async_db.add(org)
    await async_db.flush()

    service = RAGEngineService(async_db, org_id)

    # 1. Ingest Return Policy Document
    policy_text = (
        "Nexus Retail Return Policy: All damaged or defective items must be reported within 14 days of delivery. "
        "Upon inspection by our quality assurance team, a full credit note or replacement order will be issued within 48 hours. "
        "Custom manufactured goods and cut cables are non-returnable under standard terms."
    )
    doc = await service.ingest_and_chunk_document(
        title="Standard Customer Return Policy 2026",
        file_name="return_policy.txt",
        file_path="uploads/return_policy.txt",
        file_type="TXT",
        raw_text=policy_text,
        chunk_size=120,
        chunk_overlap=20,
    )
    assert doc.id is not None
    assert doc.is_processed is True
    assert doc.total_chunks > 1

    # 2. Semantic Search for "How many days to report defective goods?"
    search_res = await service.semantic_search(
        RAGSearchRequest(query="defective items report days", top_k=2)
    )
    assert len(search_res.results) > 0
    assert any("damaged or defective" in r.content for r in search_res.results)
    assert len(search_res.citations) > 0
    assert "Standard Customer Return Policy 2026" in search_res.citations[0]


@pytest.mark.asyncio
async def test_rag_multi_tenant_isolation(async_db: AsyncSession):
    """Verify that Tenant A cannot retrieve or query Tenant B's uploaded documents."""
    org_a_id = uuid.uuid4()
    org_b_id = uuid.uuid4()

    org_a = Organization(id=org_a_id, name="Alpha Corp", slug="alpha-rag")
    org_b = Organization(id=org_b_id, name="Beta Corp", slug="beta-rag")
    async_db.add_all([org_a, org_b])
    await async_db.flush()

    service_a = RAGEngineService(async_db, org_a_id)
    service_b = RAGEngineService(async_db, org_b_id)

    # Ingest confidential IP document into Tenant Alpha
    await service_a.ingest_and_chunk_document(
        title="Alpha Top Secret Merger Memo",
        file_name="merger_memo.txt",
        file_path="uploads/merger_memo.txt",
        file_type="TXT",
        raw_text="Confidential merger details between Alpha Corp and Global Megacorp valued at 500 million dollars.",
    )

    # 1. Tenant Alpha searches for "merger details" -> Finds it!
    res_a = await service_a.semantic_search(RAGSearchRequest(query="merger details"))
    assert len(res_a.results) > 0
    assert "Global Megacorp" in res_a.results[0].content

    # 2. Tenant Beta searches for the EXACT same term -> Returns ZERO results!
    res_b = await service_b.semantic_search(RAGSearchRequest(query="merger details"))
    assert len(res_b.results) == 0, "CRITICAL: Cross-tenant data leakage in RAG retrieval!"
    assert len(res_b.citations) == 0

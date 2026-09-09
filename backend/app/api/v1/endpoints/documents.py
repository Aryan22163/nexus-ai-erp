from typing import Annotated, List
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import RequirePermissions, get_current_tenant, get_current_user
from app.core.database import get_db_session
from app.models.auth import Organization, User
from app.repositories.documents import DocumentRepository
from app.schemas.documents import (
    DocumentResponse,
    RAGSearchRequest,
    RAGSearchResponse,
)
from app.services.rag_engine import RAGEngineService

router = APIRouter(prefix="/documents", tags=["Document Management & Vector RAG"])


@router.get(
    "",
    response_model=List[DocumentResponse],
    dependencies=[Depends(RequirePermissions("documents.read"))],
)
async def list_documents(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[DocumentResponse]:
    repo = DocumentRepository(db, tenant.id)
    docs = await repo.list_all()
    return [DocumentResponse.model_validate(d) for d in docs]


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("documents.upload"))],
)
async def upload_document(
    file: UploadFile,
    title: Annotated[str, Form(...)],
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> DocumentResponse:
    """Upload, extract, chunk, and embed a business document for semantic RAG search."""
    content_bytes = await file.read()
    raw_text = content_bytes.decode("utf-8", errors="ignore")

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="File content is empty or unreadable.")

    file_ext = file.filename.split(".")[-1].upper() if "." in file.filename else "TXT"

    service = RAGEngineService(db, tenant.id)
    doc = await service.ingest_and_chunk_document(
        title=title,
        file_name=file.filename,
        file_path=f"uploads/{file.filename}",
        file_type=file_ext,
        raw_text=raw_text,
        uploaded_by_id=current_user.id,
    )
    return DocumentResponse.model_validate(doc)


@router.post(
    "/rag-search",
    response_model=RAGSearchResponse,
    dependencies=[Depends(RequirePermissions("documents.read"))],
)
async def rag_semantic_search(
    req: RAGSearchRequest,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> RAGSearchResponse:
    """Perform multi-tenant isolated vector search across indexed knowledge documents."""
    service = RAGEngineService(db, tenant.id)
    return await service.semantic_search(req)

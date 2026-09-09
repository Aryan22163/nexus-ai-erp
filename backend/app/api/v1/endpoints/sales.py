import uuid
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import RequirePermissions, get_current_tenant
from app.core.database import get_db_session
from app.models.auth import Organization
from app.repositories.sales import (
    PaymentRepository,
    ProductRepository,
    QuotationRepository,
    SalesInvoiceRepository,
    SalesOrderRepository,
)
from app.schemas.sales import (
    PaymentCreate,
    PaymentResponse,
    ProductCreate,
    ProductResponse,
    ProductSalesPerformanceItem,
    QuotationCreate,
    QuotationResponse,
    SalesInvoiceCreate,
    SalesInvoiceResponse,
    SalesOrderCreate,
    SalesOrderResponse,
    TopCustomerRevenueItem,
)
from app.services.sales import SalesService

router = APIRouter(prefix="/sales", tags=["Sales & Invoicing"])


# --- Products ---
@router.get(
    "/products",
    response_model=List[ProductResponse],
    dependencies=[Depends(RequirePermissions("sales.read", "inventory.read"))],
)
async def list_products(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    skip: int = 0,
    limit: int = 50,
) -> List[ProductResponse]:
    repo = ProductRepository(db, tenant.id)
    products = await repo.list_all(skip=skip, limit=limit)
    return [ProductResponse.model_validate(p) for p in products]


@router.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("inventory.create", "sales.create"))],
)
async def create_product(
    payload: ProductCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProductResponse:
    repo = ProductRepository(db, tenant.id)
    prod = await repo.create(**payload.model_dump())
    return ProductResponse.model_validate(prod)


# --- Quotations ---
@router.get(
    "/quotations",
    response_model=List[QuotationResponse],
    dependencies=[Depends(RequirePermissions("sales.read"))],
)
async def list_quotations(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[QuotationResponse]:
    repo = QuotationRepository(db, tenant.id)
    quotes = await repo.list_all()
    return [QuotationResponse.model_validate(q) for q in quotes]


@router.post(
    "/quotations",
    response_model=QuotationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("sales.create"))],
)
async def create_quotation(
    payload: QuotationCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> QuotationResponse:
    service = SalesService(db, tenant.id)
    quote = await service.create_quotation(payload)
    return QuotationResponse.model_validate(quote)


# --- Sales Orders ---
@router.get(
    "/orders",
    response_model=List[SalesOrderResponse],
    dependencies=[Depends(RequirePermissions("sales.read"))],
)
async def list_sales_orders(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[SalesOrderResponse]:
    repo = SalesOrderRepository(db, tenant.id)
    orders = await repo.list_all()
    return [SalesOrderResponse.model_validate(o) for o in orders]


@router.post(
    "/orders",
    response_model=SalesOrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("sales.create"))],
)
async def create_sales_order(
    payload: SalesOrderCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> SalesOrderResponse:
    service = SalesService(db, tenant.id)
    order = await service.create_sales_order(payload)
    return SalesOrderResponse.model_validate(order)


# --- Sales Invoices ---
@router.get(
    "/invoices",
    response_model=List[SalesInvoiceResponse],
    dependencies=[Depends(RequirePermissions("sales.read", "finance.read"))],
)
async def list_invoices(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[SalesInvoiceResponse]:
    repo = SalesInvoiceRepository(db, tenant.id)
    invoices = await repo.list_all()
    return [SalesInvoiceResponse.model_validate(i) for i in invoices]


@router.post(
    "/invoices",
    response_model=SalesInvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("sales.create", "finance.create"))],
)
async def create_invoice(
    payload: SalesInvoiceCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> SalesInvoiceResponse:
    service = SalesService(db, tenant.id)
    invoice = await service.create_invoice_from_order(payload)
    return SalesInvoiceResponse.model_validate(invoice)


# --- Payments ---
@router.post(
    "/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermissions("finance.create"))],
)
async def record_payment(
    payload: PaymentCreate,
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> PaymentResponse:
    service = SalesService(db, tenant.id)
    payment = await service.record_payment(payload)
    return PaymentResponse.model_validate(payment)


# --- Analytics & Reporting ---
@router.get(
    "/analytics/top-customers",
    response_model=List[TopCustomerRevenueItem],
    dependencies=[Depends(RequirePermissions("sales.read"))],
)
async def get_top_customers(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    limit: int = 10,
) -> List[TopCustomerRevenueItem]:
    service = SalesService(db, tenant.id)
    return await service.get_top_customers(limit=limit)


@router.get(
    "/analytics/product-performance",
    response_model=List[ProductSalesPerformanceItem],
    dependencies=[Depends(RequirePermissions("sales.read"))],
)
async def get_product_sales_performance(
    tenant: Annotated[Organization, Depends(get_current_tenant)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    limit: int = 15,
) -> List[ProductSalesPerformanceItem]:
    service = SalesService(db, tenant.id)
    return await service.get_product_sales_performance(limit=limit)

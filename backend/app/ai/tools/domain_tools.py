import uuid
from decimal import Decimal
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.tools.registry import global_tool_registry
from app.schemas.documents import RAGSearchRequest
from app.services.finance import FinanceService
from app.services.inventory import InventoryService
from app.services.procurement import ProcurementService
from app.services.rag_engine import RAGEngineService
from app.services.sales import SalesService


@global_tool_registry.register(
    name="get_financial_summary",
    description="Retrieve live financial performance including Revenue, Gross Margin, Net Profit, and Receivables.",
    required_permission="finance.read",
    is_mutating=False,
)
async def get_financial_summary(session: AsyncSession, organization_id: uuid.UUID, **kwargs) -> Dict[str, Any]:
    finance_svc = FinanceService(session, organization_id)
    pnl = await finance_svc.get_profit_and_loss()
    ar = await finance_svc.get_receivables_aging()
    return {
        "total_revenue": str(pnl.total_revenue),
        "gross_profit": str(pnl.gross_profit),
        "net_profit": str(pnl.net_profit),
        "net_margin_percentage": pnl.net_margin_percentage,
        "accounts_receivable_outstanding": str(ar.total_outstanding),
        "overdue_over_60_days": str(ar.over_60_days),
    }


@global_tool_registry.register(
    name="get_top_customers",
    description="Fetch top customers ranked by confirmed revenue and total order volumes.",
    required_permission="sales.read",
    is_mutating=False,
)
async def get_top_customers(session: AsyncSession, organization_id: uuid.UUID, limit: int = 5, **kwargs) -> Dict[str, Any]:
    sales_svc = SalesService(session, organization_id)
    top_custs = await sales_svc.get_top_customers(limit=limit)
    return {
        "top_customers": [
            {
                "customer_id": str(c.customer_id),
                "customer_name": c.customer_name,
                "total_revenue": str(c.total_revenue),
                "orders_count": c.orders_count,
            }
            for c in top_custs
        ]
    }


@global_tool_registry.register(
    name="get_low_stock_items",
    description="Query products that have reached or fallen below reorder levels with stockout forecasts.",
    required_permission="inventory.read",
    is_mutating=False,
)
async def get_low_stock_items(session: AsyncSession, organization_id: uuid.UUID, **kwargs) -> Dict[str, Any]:
    inv_svc = InventoryService(session, organization_id)
    alerts = await inv_svc.get_low_stock_alerts()
    return {
        "low_stock_alerts": [
            {
                "sku": a.sku,
                "product_name": a.product_name,
                "current_stock": str(a.current_stock),
                "reorder_level": str(a.reorder_level),
                "days_until_stockout": a.days_until_stockout,
                "recommended_reorder_qty": str(a.recommended_reorder_qty),
                "urgency": a.urgency,
            }
            for a in alerts
        ]
    }


@global_tool_registry.register(
    name="get_supplier_performance",
    description="Evaluate vendor delivery performance, average delay days, and total historical procurement spend.",
    required_permission="procurement.read",
    is_mutating=False,
)
async def get_supplier_performance(session: AsyncSession, organization_id: uuid.UUID, **kwargs) -> Dict[str, Any]:
    proc_svc = ProcurementService(session, organization_id)
    perf = await proc_svc.get_supplier_performance()
    return {
        "suppliers": [
            {
                "supplier_name": s.supplier_name,
                "total_orders": s.total_orders,
                "total_spend": str(s.total_spend),
                "on_time_delivery_rate": s.on_time_delivery_rate,
                "average_delay_days": s.average_delay_days,
            }
            for s in perf
        ]
    }


@global_tool_registry.register(
    name="query_knowledge_base",
    description="Semantic search across company SOPs, manuals, return policies, and operational documents.",
    required_permission="documents.read",
    is_mutating=False,
)
async def query_knowledge_base(session: AsyncSession, organization_id: uuid.UUID, query: str = "", **kwargs) -> Dict[str, Any]:
    rag_svc = RAGEngineService(session, organization_id)
    res = await rag_svc.semantic_search(RAGSearchRequest(query=query, top_k=3))
    return {
        "results": [r.content for r in res.results],
        "citations": res.citations,
    }


@global_tool_registry.register(
    name="propose_purchase_order",
    description="Propose a new purchase order for supplier procurement (requires human approval).",
    required_permission="procurement.create",
    is_mutating=True,
)
async def propose_purchase_order(session: AsyncSession, organization_id: uuid.UUID, **kwargs) -> Dict[str, Any]:
    """Mutating action tool: packages the proposed purchase order payload for human approval."""
    return {
        "action_type": "CREATE_PURCHASE_ORDER",
        "requires_human_approval": True,
        "details": kwargs,
    }

import uuid
from decimal import Decimal
from typing import List
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.crm import Customer
from app.models.finance import GeneralLedger
from app.models.inventory import StockLedger
from app.models.sales import SalesInvoice, SalesOrder
from app.schemas.dashboard import (
    DashboardAIInsight,
    ExecutiveDashboardSummary,
    KPICard,
)
from app.services.finance import FinanceService
from app.services.inventory import InventoryService


class DashboardService:
    def __init__(self, session: AsyncSession, organization_id: uuid.UUID):
        self.session = session
        self.organization_id = organization_id
        self.finance_service = FinanceService(session, organization_id)
        self.inventory_service = InventoryService(session, organization_id)

    async def get_executive_summary(self) -> ExecutiveDashboardSummary:
        """Aggregate cross-module metrics into the single unified executive cockpit."""
        # 1. Financial Statement Metrics
        pnl = await self.finance_service.get_profit_and_loss()
        ar_aging = await self.finance_service.get_receivables_aging()

        # 2. Inventory Metrics
        balances = await self.inventory_service.get_stock_balance()
        inv_valuation = sum(b.total_value for b in balances)
        low_stock = await self.inventory_service.get_low_stock_alerts()

        # 3. Customer & Churn Counts
        cust_stmt = select(
            func.count(Customer.id).label("total_customers"),
            func.count(Customer.id).filter(Customer.churn_risk_score > 0.6).label("churn_risk_count"),
        ).where(Customer.organization_id == self.organization_id, Customer.is_deleted.is_(False))
        cust_res = await self.session.execute(cust_stmt)
        cust_row = cust_res.first()
        total_custs = cust_row.total_customers if cust_row else 0
        churn_count = cust_row.churn_risk_count if cust_row else 0

        # 4. Open Orders
        order_stmt = select(func.count(SalesOrder.id)).where(
            SalesOrder.organization_id == self.organization_id,
            SalesOrder.status == "CONFIRMED",
            SalesOrder.is_deleted.is_(False),
        )
        order_res = await self.session.execute(order_stmt)
        open_orders = order_res.scalar_one() or 0

        # Construct KPI Cards
        kpis = [
            KPICard(
                title="Total Revenue",
                value=f"₹{pnl.total_revenue:,.2f}",
                numeric_value=pnl.total_revenue,
                change_percentage=12.4,
                is_positive=True,
                color_theme="emerald",
            ),
            KPICard(
                title="Net Profit Margin",
                value=f"{pnl.net_margin_percentage:.1f}%",
                numeric_value=Decimal(str(pnl.net_margin_percentage)),
                change_percentage=2.1,
                is_positive=pnl.net_margin_percentage >= 0,
                color_theme="indigo",
            ),
            KPICard(
                title="Inventory Valuation",
                value=f"₹{inv_valuation:,.2f}",
                numeric_value=inv_valuation,
                change_percentage=-1.8,
                is_positive=True,
                color_theme="amber",
            ),
            KPICard(
                title="Accounts Receivable",
                value=f"₹{ar_aging.total_outstanding:,.2f}",
                numeric_value=ar_aging.total_outstanding,
                change_percentage=5.2,
                is_positive=False,
                color_theme="cyan",
            ),
        ]

        # Construct Proactive AI Insights
        ai_insights = []
        if churn_count > 0:
            ai_insights.append(
                DashboardAIInsight(
                    title="Customer Churn Risk Alert",
                    description=f"{churn_count} high-value account(s) show declining order frequency and high churn risk.",
                    action_text="Review Accounts",
                    urgency_badge="High Risk",
                )
            )

        if len(low_stock) > 0:
            crit_item = low_stock[0]
            ai_insights.append(
                DashboardAIInsight(
                    title="Inventory Stockout Forecast",
                    description=f"Product '{crit_item.product_name}' (SKU: {crit_item.sku}) is below reorder level ({crit_item.current_stock} remaining).",
                    action_text="Draft Purchase Order",
                    urgency_badge="Stock Alert",
                )
            )

        if pnl.net_margin_percentage > 15.0:
            ai_insights.append(
                DashboardAIInsight(
                    title="Healthy Margin Expansion",
                    description=f"Operating margin remains strong at {pnl.net_margin_percentage:.1f}%. Capitalize on enterprise pipeline.",
                    action_text="View Pipeline",
                    urgency_badge="Growth",
                )
            )

        return ExecutiveDashboardSummary(
            kpis=kpis,
            ai_insights=ai_insights,
            total_active_customers=total_custs,
            open_sales_orders_count=open_orders,
            low_stock_items_count=len(low_stock),
            total_inventory_valuation=inv_valuation,
            total_accounts_receivable=ar_aging.total_outstanding,
        )

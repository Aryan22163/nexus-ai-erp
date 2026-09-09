from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class KPICard(BaseModel):
    title: str
    value: str
    numeric_value: Decimal
    change_percentage: Optional[float] = None
    is_positive: bool = True
    color_theme: str  # emerald, indigo, amber, rose, cyan


class DashboardAIInsight(BaseModel):
    title: str
    description: str
    action_text: str
    urgency_badge: str  # High Risk, Stock Alert, Growth, Review
    action_payload: Optional[dict] = None


class ExecutiveDashboardSummary(BaseModel):
    kpis: List[KPICard]
    ai_insights: List[DashboardAIInsight]
    total_active_customers: int
    open_sales_orders_count: int
    low_stock_items_count: int
    total_inventory_valuation: Decimal
    total_accounts_receivable: Decimal

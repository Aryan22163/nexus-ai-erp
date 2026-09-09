from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SalesForecastRequest(BaseModel):
    historical_monthly_sales: List[Decimal] = Field(..., min_length=2, examples=[[Decimal("120000.00"), Decimal("145000.00"), Decimal("160000.00")]])


class SalesForecastResponse(BaseModel):
    historical_periods: int
    projected_next_30_days_revenue: Decimal
    trend_direction: str
    growth_rate_percentage: float
    confidence_interval: Dict[str, Decimal]


class ChurnRiskRequest(BaseModel):
    customer_id: str
    customer_name: str
    recency_days: int = Field(..., ge=0, examples=[52])
    frequency_orders: int = Field(..., ge=0, examples=[2])
    monetary_value: Decimal = Field(..., ge=0, examples=[Decimal("45000.00")])
    unresolved_support_tickets: int = Field(default=0, ge=0)


class ChurnRiskResponse(BaseModel):
    customer_id: str
    customer_name: str
    recency_days: int
    frequency_orders: int
    monetary_value: Decimal
    churn_probability: float
    risk_level: str
    primary_risk_factors: List[str]
    suggested_retention_action: str


class AnomalyDetectionRequest(BaseModel):
    historical_expenses: List[Decimal] = Field(..., min_length=3, examples=[[Decimal("12000.00"), Decimal("11500.00"), Decimal("13000.00"), Decimal("12500.00")]])
    current_amount: Decimal = Field(..., examples=[Decimal("48000.00")])
    category: str = Field(default="Travel & Entertainment")


class AnomalyDetectionResponse(BaseModel):
    record_id: str
    category: str
    amount: Decimal
    deviation_score: float
    is_anomaly: bool
    explanation: str

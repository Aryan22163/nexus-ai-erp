from fastapi import APIRouter, Depends
from app.api.deps import RequirePermissions
from app.ml.engine import PredictiveMLEngine
from app.schemas.ml import (
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    ChurnRiskRequest,
    ChurnRiskResponse,
    SalesForecastRequest,
    SalesForecastResponse,
)

router = APIRouter(prefix="/ml", tags=["Predictive Analytics & Machine Learning"])


@router.post(
    "/forecast/sales",
    response_model=SalesForecastResponse,
    dependencies=[Depends(RequirePermissions("sales.read"))],
)
async def forecast_sales(payload: SalesForecastRequest) -> SalesForecastResponse:
    """Predict next 30 days sales revenue and trend direction based on historical periods."""
    result = PredictiveMLEngine.forecast_sales(payload.historical_monthly_sales)
    return SalesForecastResponse(
        historical_periods=result.historical_periods,
        projected_next_30_days_revenue=result.projected_next_30_days_revenue,
        trend_direction=result.trend_direction,
        growth_rate_percentage=result.growth_rate_percentage,
        confidence_interval=result.confidence_interval,
    )


@router.post(
    "/churn/score",
    response_model=ChurnRiskResponse,
    dependencies=[Depends(RequirePermissions("crm.read"))],
)
async def score_customer_churn(payload: ChurnRiskRequest) -> ChurnRiskResponse:
    """Calculate customer churn risk probability using RFM metrics."""
    result = PredictiveMLEngine.score_customer_churn(
        customer_id=payload.customer_id,
        customer_name=payload.customer_name,
        recency_days=payload.recency_days,
        frequency_orders=payload.frequency_orders,
        monetary_value=payload.monetary_value,
        unresolved_support_tickets=payload.unresolved_support_tickets,
    )
    return ChurnRiskResponse(
        customer_id=result.customer_id,
        customer_name=result.customer_name,
        recency_days=result.recency_days,
        frequency_orders=result.frequency_orders,
        monetary_value=result.monetary_value,
        churn_probability=result.churn_probability,
        risk_level=result.risk_level,
        primary_risk_factors=result.primary_risk_factors,
        suggested_retention_action=result.suggested_retention_action,
    )


@router.post(
    "/anomalies/detect",
    response_model=AnomalyDetectionResponse,
    dependencies=[Depends(RequirePermissions("finance.read"))],
)
async def detect_expense_anomaly(payload: AnomalyDetectionRequest) -> AnomalyDetectionResponse:
    """Statistical Z-score anomaly detection for expense or purchasing outliers."""
    result = PredictiveMLEngine.detect_expense_anomalies(
        historical_expenses=payload.historical_expenses,
        current_amount=payload.current_amount,
        category=payload.category,
    )
    return AnomalyDetectionResponse(
        record_id=result.record_id,
        category=result.category,
        amount=result.amount,
        deviation_score=result.deviation_score,
        is_anomaly=result.is_anomaly,
        explanation=result.explanation,
    )

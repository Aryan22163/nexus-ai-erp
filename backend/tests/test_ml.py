import uuid
from decimal import Decimal
import pytest
from httpx import AsyncClient
from app.api.deps import get_current_user
from app.main import app
from app.ml.engine import PredictiveMLEngine
from app.models.auth import User


def test_predictive_ml_sales_forecast():
    # Test upward trend
    historical_sales = [
        Decimal("100000.00"),
        Decimal("120000.00"),
        Decimal("145000.00"),
        Decimal("170000.00"),
        Decimal("200000.00"),
    ]
    result = PredictiveMLEngine.forecast_sales(historical_sales)
    assert result.historical_periods == 5
    assert result.projected_next_30_days_revenue > Decimal("200000.00")
    assert result.trend_direction == "EXPANSION"
    assert result.growth_rate_percentage > 5.0
    assert result.confidence_interval["lower_bound"] < result.projected_next_30_days_revenue
    assert result.confidence_interval["upper_bound"] > result.projected_next_30_days_revenue

    # Test downward trend
    down_sales = [Decimal("300000.00"), Decimal("240000.00"), Decimal("190000.00")]
    down_result = PredictiveMLEngine.forecast_sales(down_sales)
    assert down_result.trend_direction == "CONTRACTION"
    assert down_result.growth_rate_percentage < 0.0

    # Test edge case (single period)
    single_res = PredictiveMLEngine.forecast_sales([Decimal("50000.00")])
    assert single_res.projected_next_30_days_revenue == Decimal("50000.00")
    assert single_res.trend_direction == "STABLE"


def test_predictive_ml_customer_churn_scoring():
    # Inactive customer with single order
    at_risk = PredictiveMLEngine.score_customer_churn(
        customer_id="cust-123",
        customer_name="Acme Corp",
        recency_days=105,
        frequency_orders=1,
        monetary_value=Decimal("15000.00"),
        unresolved_support_tickets=2,
    )
    assert at_risk.churn_probability >= 0.70
    assert at_risk.risk_level in ["HIGH", "CRITICAL"]
    assert len(at_risk.primary_risk_factors) >= 2
    assert "retention" in at_risk.suggested_retention_action.lower()

    # Active high-frequency customer
    loyal = PredictiveMLEngine.score_customer_churn(
        customer_id="cust-456",
        customer_name="Enterprise Logistics",
        recency_days=8,
        frequency_orders=14,
        monetary_value=Decimal("500000.00"),
        unresolved_support_tickets=0,
    )
    assert loyal.churn_probability < 0.25
    assert loyal.risk_level == "LOW"


def test_predictive_ml_expense_anomaly_detection():
    # Historical normal monthly cloud infrastructure expenses
    historical = [
        Decimal("12000.00"),
        Decimal("12500.00"),
        Decimal("11800.00"),
        Decimal("12200.00"),
        Decimal("12400.00"),
    ]

    # Normal bill
    normal_res = PredictiveMLEngine.detect_expense_anomalies(
        historical_expenses=historical,
        current_amount=Decimal("12350.00"),
        category="Cloud Infrastructure",
    )
    assert not normal_res.is_anomaly
    assert abs(normal_res.deviation_score) < 2.5

    # Massive unexpected spike
    spike_res = PredictiveMLEngine.detect_expense_anomalies(
        historical_expenses=historical,
        current_amount=Decimal("95000.00"),
        category="Cloud Infrastructure",
    )
    assert spike_res.is_anomaly
    assert spike_res.deviation_score > 5.0
    assert "deviates significantly" in spike_res.explanation


@pytest.mark.asyncio
async def test_ml_api_endpoints(async_client: AsyncClient):
    dummy_user = User(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        email="superadmin@nexus.test",
        first_name="Super",
        last_name="Admin",
        is_superuser=True,
        is_active=True,
        roles=[],
    )
    app.dependency_overrides[get_current_user] = lambda: dummy_user

    try:
        # Test Sales Forecast Endpoint
        forecast_resp = await async_client.post(
            "/api/v1/ml/forecast/sales",
            json={"historical_monthly_sales": ["100000.00", "120000.00", "140000.00", "160000.00"]},
        )
        assert forecast_resp.status_code == 200
        fdata = forecast_resp.json()
        assert fdata["trend_direction"] == "EXPANSION"
        assert Decimal(str(fdata["projected_next_30_days_revenue"])) > Decimal("160000.00")

        # Test Customer Churn Endpoint
        churn_resp = await async_client.post(
            "/api/v1/ml/churn/score",
            json={
                "customer_id": "cust-999",
                "customer_name": "Test Client",
                "recency_days": 120,
                "frequency_orders": 1,
                "monetary_value": "5000.00",
                "unresolved_support_tickets": 3,
            },
        )
        assert churn_resp.status_code == 200
        cdata = churn_resp.json()
        assert cdata["risk_level"] in ["HIGH", "CRITICAL"]

        # Test Expense Anomaly Endpoint
        anomaly_resp = await async_client.post(
            "/api/v1/ml/anomalies/detect",
            json={
                "historical_expenses": ["5000.00", "5200.00", "4900.00", "5100.00"],
                "current_amount": "45000.00",
                "category": "Marketing Campaign",
            },
        )
        assert anomaly_resp.status_code == 200
        adata = anomaly_resp.json()
        assert adata["is_anomaly"] is True
    finally:
        app.dependency_overrides.clear()

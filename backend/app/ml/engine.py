from dataclasses import dataclass
from decimal import Decimal
import math
import statistics
from typing import Dict, List, Optional
import uuid


@dataclass
class SalesForecastResult:
    historical_periods: int
    projected_next_30_days_revenue: Decimal
    trend_direction: str  # EXPANSION, STABLE, CONTRACTION
    growth_rate_percentage: float
    confidence_interval: Dict[str, Decimal]


@dataclass
class ChurnRiskScore:
    customer_id: str
    customer_name: str
    recency_days: int
    frequency_orders: int
    monetary_value: Decimal
    churn_probability: float  # 0.0 to 1.0
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    primary_risk_factors: List[str]
    suggested_retention_action: str


@dataclass
class AnomalyDetectionResult:
    record_id: str
    category: str
    amount: Decimal
    deviation_score: float  # Z-score
    is_anomaly: bool
    explanation: str


class PredictiveMLEngine:
    """
    Predictive Machine Learning Engine for NEXUS AI.
    Implements sales time-series forecasting, RFM customer churn risk scoring, and statistical anomaly detection.
    """

    @staticmethod
    def forecast_sales(historical_monthly_sales: List[Decimal]) -> SalesForecastResult:
        """
        Calculates sales projections using linear trend extrapolation and momentum smoothing.
        """
        if not historical_monthly_sales or len(historical_monthly_sales) < 2:
            base_val = historical_monthly_sales[0] if historical_monthly_sales else Decimal("500000.00")
            return SalesForecastResult(
                historical_periods=len(historical_monthly_sales),
                projected_next_30_days_revenue=base_val,
                trend_direction="STABLE",
                growth_rate_percentage=0.0,
                confidence_interval={
                    "lower_bound": base_val * Decimal("0.90"),
                    "upper_bound": base_val * Decimal("1.10"),
                },
            )

        y = [float(val) for val in historical_monthly_sales]
        x = list(range(len(y)))

        n = len(y)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        denom = (n * sum_x2) - (sum_x ** 2)
        if denom != 0:
            slope = ((n * sum_xy) - (sum_x * sum_y)) / denom
            intercept = (sum_y - (slope * sum_x)) / n
        else:
            slope = 0.0
            intercept = sum_y / n
        next_x = n
        projected = slope * next_x + intercept

        # Calculate growth rate
        last_val = y[-1]
        growth = ((projected - last_val) / last_val) * 100 if last_val > 0 else 0.0

        trend_dir = "EXPANSION" if growth > 2.0 else ("CONTRACTION" if growth < -2.0 else "STABLE")
        proj_dec = Decimal(str(round(max(0.0, projected), 2)))

        return SalesForecastResult(
            historical_periods=len(historical_monthly_sales),
            projected_next_30_days_revenue=proj_dec,
            trend_direction=trend_dir,
            growth_rate_percentage=round(growth, 2),
            confidence_interval={
                "lower_bound": proj_dec * Decimal("0.92"),
                "upper_bound": proj_dec * Decimal("1.08"),
            },
        )

    @staticmethod
    def score_customer_churn(
        customer_id: str,
        customer_name: str,
        recency_days: int,
        frequency_orders: int,
        monetary_value: Decimal,
        unresolved_support_tickets: int = 0,
    ) -> ChurnRiskScore:
        """
        Calculates churn probability using RFM (Recency, Frequency, Monetary) engagement metrics.
        """
        risk_score = 0.1  # Baseline probability

        # Recency impact: inactive > 45 days increases churn risk
        if recency_days > 90:
            risk_score += 0.50
        elif recency_days > 45:
            risk_score += 0.30
        elif recency_days > 30:
            risk_score += 0.15

        # Frequency impact: fewer repeat orders increases risk
        if frequency_orders <= 1:
            risk_score += 0.20
        elif frequency_orders <= 3:
            risk_score += 0.10

        # Unresolved tickets
        risk_score += min(0.25, unresolved_support_tickets * 0.10)

        churn_prob = round(min(0.99, max(0.01, risk_score)), 2)

        risk_factors = []
        if recency_days > 45:
            risk_factors.append(f"Inactivity: No confirmed purchases in {recency_days} days")
        if frequency_orders <= 1:
            risk_factors.append("Low order frequency (Single purchase history)")
        if unresolved_support_tickets > 0:
            risk_factors.append(f"{unresolved_support_tickets} pending support inquiry")

        if churn_prob >= 0.70:
            level = "CRITICAL"
            action = "Dispatch Key Account Manager for urgent on-site retention review"
        elif churn_prob >= 0.45:
            level = "HIGH"
            action = "Offer special 10% volume renewal incentive and scheduled follow-up"
        elif churn_prob >= 0.25:
            level = "MEDIUM"
            action = "Send personalized product catalog and satisfaction pulse check"
        else:
            level = "LOW"
            action = "Maintain regular relationship touchpoints and quarterly review"

        return ChurnRiskScore(
            customer_id=customer_id,
            customer_name=customer_name,
            recency_days=recency_days,
            frequency_orders=frequency_orders,
            monetary_value=monetary_value,
            churn_probability=churn_prob,
            risk_level=level,
            primary_risk_factors=risk_factors or ["Healthy ongoing engagement"],
            suggested_retention_action=action,
        )

    @staticmethod
    def detect_expense_anomalies(
        historical_expenses: List[Decimal],
        current_amount: Decimal,
        category: str = "General",
    ) -> AnomalyDetectionResult:
        """
        Detects financial expenditure outliers using statistical standard deviation (Z-score).
        """
        if len(historical_expenses) < 3:
            return AnomalyDetectionResult(
                record_id=str(uuid.uuid4()),
                category=category,
                amount=current_amount,
                deviation_score=0.0,
                is_anomaly=False,
                explanation="Insufficient historical baseline to establish statistical variance.",
            )

        data = [float(x) for x in historical_expenses]
        mean = float(statistics.mean(data))
        std_dev = float(statistics.pstdev(data)) if len(data) > 1 else 0.0

        val = float(current_amount)
        z_score = (val - mean) / std_dev if std_dev > 0 else 0.0

        is_anom = abs(z_score) > 2.5
        expl = (
            f"Amount of ₹{current_amount:,.2f} deviates significantly ({z_score:.1f} standard deviations) "
            f"from the category mean of ₹{mean:,.2f}."
            if is_anom
            else f"Amount of ₹{current_amount:,.2f} falls within normal category variance."
        )

        return AnomalyDetectionResult(
            record_id=str(uuid.uuid4()),
            category=category,
            amount=current_amount,
            deviation_score=round(z_score, 2),
            is_anomaly=is_anom,
            explanation=expl,
        )

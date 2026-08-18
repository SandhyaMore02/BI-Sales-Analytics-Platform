import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.engine import Engine
from src.database.connection import create_db_engine
from src.analytics.query_engine import SQLAnalyticsEngine

class SalesForecastingEngine:
    def __init__(self, engine: Engine = None):
        self.engine = engine or create_db_engine()
        self.query_engine = SQLAnalyticsEngine(engine=self.engine)

    def generate_monthly_forecast(self, forecast_months: int = 3) -> Dict[str, Any]:
        """
        Generates 3-month forward sales revenue forecast based on historical monthly trend analysis.
        Calculates expected forecast value along with upper/lower confidence bounds.
        """
        mom_df = self.query_engine.get_mom_growth()

        if mom_df.empty or len(mom_df) < 3:
            return {"status": "error", "message": "Insufficient historical data for forecasting."}

        # Filter valid historical revenue
        hist_df = mom_df[["year_month", "revenue"]].copy()
        hist_df["revenue"] = hist_df["revenue"].astype(float)

        # Fit simple linear trend + exponential smoothing weighted baseline
        y = hist_df["revenue"].values
        x = np.arange(len(y))

        # Linear fit: y = slope * x + intercept
        slope, intercept = np.polyfit(x, y, 1)

        # Recent momentum factor (weight last 3 months higher)
        recent_avg = np.mean(y[-3:])
        trend_avg = slope * len(y) + intercept
        baseline = 0.6 * trend_avg + 0.4 * recent_avg

        # Generate future months
        last_ym_str = hist_df["year_month"].iloc[-1]
        last_date = datetime.strptime(last_ym_str, "%Y-%m")

        future_records = []
        std_error = np.std(y) * 0.5  # 50% std dev for confidence bounds

        for i in range(1, forecast_months + 1):
            future_date = last_date + relativedelta(months=i)
            future_ym = future_date.strftime("%Y-%m")
            
            # Forecast value with mild slope projection
            forecast_val = max(baseline + (slope * i), 10000.0)
            lower_bound = max(forecast_val - std_error * (1 + 0.1 * i), 5000.0)
            upper_bound = forecast_val + std_error * (1 + 0.1 * i)

            future_records.append({
                "year_month": future_ym,
                "forecast_revenue": round(forecast_val, 2),
                "lower_bound": round(lower_bound, 2),
                "upper_bound": round(upper_bound, 2),
                "type": "Forecast"
            })

        # Format historical records
        historical_records = []
        for _, row in hist_df.iterrows():
            historical_records.append({
                "year_month": row["year_month"],
                "actual_revenue": round(row["revenue"], 2),
                "type": "Historical"
            })

        return {
            "status": "success",
            "historical": historical_records,
            "forecast": future_records,
            "trend_slope": round(float(slope), 2),
            "forecast_months_ahead": forecast_months
        }

if __name__ == "__main__":
    forecaster = SalesForecastingEngine()
    res = forecaster.generate_monthly_forecast()
    print("Forecast Status:", res["status"])
    if res["status"] == "success":
        print("Forecast Records:", res["forecast"])

import pandas as pd
from typing import List, Dict, Any

class BusinessAlertEngine:
    def __init__(self):
        pass

    def evaluate_alerts(self, kpi_summary: Dict[str, Any], regional_df: pd.DataFrame, product_df: pd.DataFrame, mom_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Scans analytics metrics and triggers severity-coded business alerts.
        """
        alerts = []

        # 1. Overall Profit Margin Alert
        margin = kpi_summary.get("profit_margin_pct", 0.0)
        if margin < 15.0:
            alerts.append({
                "severity": "HIGH",
                "category": "Margin Contraction",
                "title": "Low Overall Profit Margin Alert",
                "description": f"Overall profit margin is currently at {margin:.2f}%, which is below the 15% healthy benchmark threshold.",
                "evidence": f"Total Revenue: ${kpi_summary.get('total_revenue', 0):,.2f}, Net Profit: ${kpi_summary.get('total_profit', 0):,.2f}"
            })
        elif margin < 25.0:
            alerts.append({
                "severity": "MEDIUM",
                "category": "Margin Sensitivity",
                "title": "Moderate Profit Margin Warning",
                "description": f"Profit margin stands at {margin:.2f}%. Monitor discount strategies closely.",
                "evidence": f"Total Profit: ${kpi_summary.get('total_profit', 0):,.2f}"
            })

        # 2. Month-over-Month Revenue Growth Alert
        if not mom_df.empty and "mom_growth_pct" in mom_df.columns:
            latest_mom = mom_df.dropna(subset=["mom_growth_pct"]).iloc[-1] if len(mom_df.dropna(subset=["mom_growth_pct"])) > 0 else None
            if latest_mom is not None:
                growth_val = latest_mom["mom_growth_pct"]
                ym = latest_mom.get("year_month", "Latest Month")
                if growth_val < -10.0:
                    alerts.append({
                        "severity": "HIGH",
                        "category": "Revenue Decline",
                        "title": f"Significant MoM Revenue Drop in {ym}",
                        "description": f"Revenue declined by {growth_val:.2f}% compared to previous month.",
                        "evidence": f"Current Month Revenue: ${latest_mom['revenue']:,.2f}, Prev Month: ${latest_mom.get('prev_month_revenue', 0):,.2f}"
                    })
                elif growth_val < 0.0:
                    alerts.append({
                        "severity": "MEDIUM",
                        "category": "Revenue Decline",
                        "title": f"Minor MoM Revenue Dip in {ym}",
                        "description": f"Revenue dipped by {growth_val:.2f}%.",
                        "evidence": f"Current Month Revenue: ${latest_mom['revenue']:,.2f}"
                    })

        # 3. High-Revenue Low-Margin Product Alert
        if not product_df.empty and "total_revenue" in product_df.columns and "profit_margin_pct" in product_df.columns:
            low_margin_products = product_df[(product_df["profit_margin_pct"] < 15.0) & (product_df["total_revenue"] > 100000)].copy()
            for _, row in low_margin_products.iterrows():
                alerts.append({
                    "severity": "HIGH",
                    "category": "Product Profitability",
                    "title": f"High Revenue / Low Margin Product: {row['product_name']}",
                    "description": f"Product '{row['product_name']}' generated ${row['total_revenue']:,.2f} in revenue but has a low margin of {row['profit_margin_pct']:.2f}%.",
                    "evidence": f"Category: {row['category']}, Profit: ${row['total_profit']:,.2f}"
                })

        # 4. Regional Underperformance Alert
        if not regional_df.empty and "profit_margin_pct" in regional_df.columns:
            low_margin_regions = regional_df[regional_df["profit_margin_pct"] < 18.0].copy()
            for _, row in low_margin_regions.iterrows():
                alerts.append({
                    "severity": "MEDIUM",
                    "category": "Regional Performance",
                    "title": f"Underperforming Region: {row['region']} ({row['state']})",
                    "description": f"Region '{row['region']}' ({row['state']}) margin is {row['profit_margin_pct']:.2f}%.",
                    "evidence": f"Total Revenue: ${row['total_revenue']:,.2f}, Profit: ${row['total_profit']:,.2f}"
                })

        return alerts

if __name__ == "__main__":
    alert_engine = BusinessAlertEngine()
    print("Alert Engine Initialized.")

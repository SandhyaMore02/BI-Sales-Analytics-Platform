import pandas as pd
from typing import Dict, Any
from sqlalchemy.engine import Engine
from src.database.connection import create_db_engine

class SQLAnalyticsEngine:
    def __init__(self, engine: Engine = None):
        self.engine = engine or create_db_engine()

    def get_kpi_summary(self) -> Dict[str, Any]:
        """Retrieves top-level business KPI metrics from Star Schema."""
        query = """
        SELECT
            COUNT(DISTINCT f.order_id) AS total_orders,
            COUNT(DISTINCT f.customer_key) AS unique_customers,
            SUM(f.quantity) AS total_units_sold,
            ROUND(SUM(f.revenue), 2) AS total_revenue,
            ROUND(SUM(f.total_cost), 2) AS total_cost,
            ROUND(SUM(f.profit), 2) AS total_profit,
            ROUND((SUM(f.profit) / NULLIF(SUM(f.revenue), 0)) * 100.0, 2) AS profit_margin_pct,
            ROUND(AVG(f.revenue), 2) AS avg_order_line_value
        FROM fact_sales f;
        """
        df = pd.read_sql(query, self.engine)
        return df.iloc[0].to_dict()

    def get_product_performance(self) -> pd.DataFrame:
        """Retrieves product revenue, profit, margins, and ranking."""
        query = """
        SELECT
            p.product_id,
            p.product_name,
            p.category,
            SUM(f.quantity) AS total_units_sold,
            ROUND(SUM(f.revenue), 2) AS total_revenue,
            ROUND(SUM(f.profit), 2) AS total_profit,
            ROUND((SUM(f.profit) / NULLIF(SUM(f.revenue), 0)) * 100.0, 2) AS profit_margin_pct
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY total_revenue DESC;
        """
        return pd.read_sql(query, self.engine)

    def get_regional_analytics(self) -> pd.DataFrame:
        """Retrieves sales breakdown by region and state."""
        query = """
        SELECT
            r.region,
            r.state,
            COUNT(DISTINCT f.order_id) AS total_orders,
            ROUND(SUM(f.revenue), 2) AS total_revenue,
            ROUND(SUM(f.profit), 2) AS total_profit,
            ROUND((SUM(f.profit) / NULLIF(SUM(f.revenue), 0)) * 100.0, 2) AS profit_margin_pct
        FROM fact_sales f
        JOIN dim_region r ON f.region_key = r.region_key
        GROUP BY r.region, r.state
        ORDER BY total_revenue DESC;
        """
        return pd.read_sql(query, self.engine)

    def get_mom_growth(self) -> pd.DataFrame:
        """Calculates Month-over-Month (MoM) revenue & profit growth trends."""
        query = """
        WITH monthly AS (
            SELECT
                d.year,
                d.month,
                d.year_month,
                SUM(f.revenue) AS revenue,
                SUM(f.profit) AS profit
            FROM fact_sales f
            JOIN dim_date d ON f.date_id = d.date_id
            GROUP BY d.year, d.month, d.year_month
        )
        SELECT
            year_month,
            ROUND(revenue, 2) AS revenue,
            ROUND(profit, 2) AS profit,
            ROUND(LAG(revenue) OVER (ORDER BY year, month), 2) AS prev_month_revenue,
            ROUND(
                (revenue - LAG(revenue) OVER (ORDER BY year, month)) 
                / NULLIF(LAG(revenue) OVER (ORDER BY year, month), 0) * 100.0, 2
            ) AS mom_growth_pct
        FROM monthly
        ORDER BY year, month;
        """
        return pd.read_sql(query, self.engine)

if __name__ == "__main__":
    analytics = SQLAnalyticsEngine()
    try:
        kpis = analytics.get_kpi_summary()
        print("Business KPIs:", kpis)
    except Exception as e:
        print("Note: Run database load first.", e)

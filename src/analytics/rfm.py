import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sqlalchemy.engine import Engine
from src.database.connection import create_db_engine

class RFMSegmentationEngine:
    def __init__(self, engine: Engine = None):
        self.engine = engine or create_db_engine()

    def compute_rfm_segmentation(self) -> Dict[str, Any]:
        """
        Computes Recency, Frequency, Monetary (RFM) metrics per customer and assigns segment labels.
        """
        query = """
        SELECT
            c.customer_id,
            c.customer_name,
            MAX(d.full_date) AS last_order_date,
            COUNT(DISTINCT f.order_id) AS frequency,
            SUM(f.revenue) AS monetary
        FROM fact_sales f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        JOIN dim_date d ON f.date_id = d.date_id
        GROUP BY c.customer_id, c.customer_name;
        """
        df = pd.read_sql(query, self.engine)

        if df.empty:
            return {"status": "error", "message": "No customer sales data available."}

        # Calculate Recency in days relative to dataset max date
        max_date = pd.to_datetime(df["last_order_date"]).max()
        df["last_order_datetime"] = pd.to_datetime(df["last_order_date"])
        df["recency"] = (max_date - df["last_order_datetime"]).dt.days

        # Assign R, F, M Scores (1 to 5 scale)
        try:
            df["r_score"] = pd.qcut(df["recency"], q=5, labels=[5, 4, 3, 2, 1], duplicates="drop")
        except Exception:
            df["r_score"] = 3

        try:
            df["f_score"] = pd.qcut(df["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5])
        except Exception:
            df["f_score"] = 3

        try:
            df["m_score"] = pd.qcut(df["monetary"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5])
        except Exception:
            df["m_score"] = 3

        df["r_score"] = df["r_score"].astype(int)
        df["f_score"] = df["f_score"].astype(int)
        df["m_score"] = df["m_score"].astype(int)

        # Segment Classification Logic
        def classify_segment(row):
            r, f, m = row["r_score"], row["f_score"], row["m_score"]
            if r >= 4 and f >= 4 and m >= 4:
                return "Champions"
            elif f >= 3 and m >= 3:
                return "Loyal Customers"
            elif r >= 3 and m >= 3:
                return "Potential Loyalists"
            elif r <= 2 and f >= 3:
                return "At Risk"
            else:
                return "Lost / Low Value"

        df["segment"] = df.apply(classify_segment, axis=1)

        # Summary Metrics per Segment
        segment_summary = df.groupby("segment").agg(
            customer_count=("customer_id", "count"),
            total_revenue=("monetary", "sum"),
            avg_recency=("recency", "mean"),
            avg_orders=("frequency", "mean")
        ).reset_index()

        segment_summary["total_revenue"] = segment_summary["total_revenue"].round(2)
        segment_summary["avg_recency"] = segment_summary["avg_recency"].round(1)
        segment_summary["avg_orders"] = segment_summary["avg_orders"].round(1)

        # Top 10 Champion Customers
        champions = df[df["segment"] == "Champions"].sort_values(by="monetary", ascending=False).head(10)
        champions_list = champions[["customer_id", "customer_name", "recency", "frequency", "monetary"]].to_dict(orient="records")

        return {
            "status": "success",
            "total_customers_analyzed": len(df),
            "segment_summary": segment_summary.to_dict(orient="records"),
            "champions": champions_list,
            "raw_customers": df[["customer_id", "customer_name", "recency", "frequency", "monetary", "segment"]].to_dict(orient="records")
        }

if __name__ == "__main__":
    rfm_engine = RFMSegmentationEngine()
    res = rfm_engine.compute_rfm_segmentation()
    print("RFM Status:", res["status"])
    if res["status"] == "success":
        print("Analyzed Customers:", res["total_customers_analyzed"])
        print("Segments:", res["segment_summary"])

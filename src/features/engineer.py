import pandas as pd
import numpy as np

class FeatureEngineeringPipeline:
    def __init__(self):
        pass

    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates financial business metrics and extracts date dimension features.
        """
        featured_df = df.copy()

        # 1. Financial Business Metrics
        featured_df["revenue"] = (
            featured_df["quantity"] * featured_df["unit_price"] * (1.0 - featured_df["discount"])
        ).round(2)

        featured_df["total_cost"] = (
            featured_df["quantity"] * featured_df["cost"]
        ).round(2)

        featured_df["profit"] = (
            featured_df["revenue"] - featured_df["total_cost"]
        ).round(2)

        featured_df["profit_margin_pct"] = np.where(
            featured_df["revenue"] > 0,
            (featured_df["profit"] / featured_df["revenue"]) * 100.0,
            0.0
        ).round(2)

        # 2. Date Dimension Features
        dates = pd.to_datetime(featured_df["order_date"])
        featured_df["year"] = dates.dt.year
        featured_df["quarter_num"] = dates.dt.quarter
        featured_df["quarter"] = "Q" + dates.dt.quarter.astype(str)
        featured_df["month"] = dates.dt.month
        featured_df["month_name"] = dates.dt.strftime("%B")
        featured_df["year_month"] = dates.dt.strftime("%Y-%m")
        featured_df["day"] = dates.dt.day
        featured_df["day_of_week"] = dates.dt.strftime("%A")
        featured_df["week_of_year"] = dates.dt.isocalendar().week.astype(int)

        print(f"[OK] Feature Engineering Completed:")
        print(f"  - Total Calculated Revenue: ${featured_df['revenue'].sum():,.2f}")
        print(f"  - Total Calculated Profit:  ${featured_df['profit'].sum():,.2f}")
        print(f"  - Overall Profit Margin:    {((featured_df['profit'].sum() / featured_df['revenue'].sum()) * 100):.2f}%")

        return featured_df

if __name__ == "__main__":
    from src.ingestion.ingest import DataIngestionEngine
    from src.cleaning.clean import DataCleaningPipeline
    import os

    path = "data/raw/sales_data.csv"
    if os.path.exists(path):
        df, _ = DataIngestionEngine().ingest(path)
        clean_df, _ = DataCleaningPipeline().clean(df)
        fe_df = FeatureEngineeringPipeline().add_features(clean_df)
        print(fe_df[["order_id", "revenue", "total_cost", "profit", "profit_margin_pct", "year_month"]].head())

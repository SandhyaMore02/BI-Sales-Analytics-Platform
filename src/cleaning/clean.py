import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

class DataCleaningPipeline:
    def __init__(self):
        pass

    def clean(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Executes complete data cleaning pipeline:
        1. Duplicate removal
        2. Missing value imputation / handling
        3. Type conversions
        4. Text standardization
        5. Outlier & invalid value filter
        """
        initial_rows = len(df)
        report = {
            "initial_rows": initial_rows,
            "duplicates_removed": 0,
            "invalid_rows_removed": 0,
            "missing_values_handled": 0,
            "final_rows": 0
        }

        cleaned_df = df.copy()

        # 1. Remove Duplicate Records
        before_dups = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        report["duplicates_removed"] = before_dups - len(cleaned_df)

        # 2. Text Standardization & Casing Normalization
        string_cols = ["customer_name", "product_name", "category", "city", "state", "region"]
        for col in string_cols:
            if col in cleaned_df.columns:
                cleaned_df[col] = cleaned_df[col].astype(str).str.strip().str.title()
                # Restore NaN if string became 'Nan' or 'None'
                cleaned_df[col] = cleaned_df[col].replace(["Nan", "None", ""], np.nan)

        # Fill Missing Cities/Regions with 'Unknown'
        cleaned_df["city"] = cleaned_df["city"].fillna("Unknown")
        cleaned_df["state"] = cleaned_df["state"].fillna("Unknown")
        cleaned_df["region"] = cleaned_df["region"].fillna("Unknown")

        # 3. Numeric Imputation & Type Conversion
        cleaned_df["discount"] = pd.to_numeric(cleaned_df["discount"], errors="coerce").fillna(0.0)
        cleaned_df["quantity"] = pd.to_numeric(cleaned_df["quantity"], errors="coerce")
        cleaned_df["unit_price"] = pd.to_numeric(cleaned_df["unit_price"], errors="coerce")
        cleaned_df["cost"] = pd.to_numeric(cleaned_df["cost"], errors="coerce")
        cleaned_df["order_date"] = pd.to_datetime(cleaned_df["order_date"], errors="coerce")

        # 4. Filter Invalid Records (e.g. quantity <= 0, discount < 0 or discount > 1.0, negative prices)
        valid_mask = (
            (cleaned_df["quantity"] > 0) &
            (cleaned_df["unit_price"] >= 0) &
            (cleaned_df["cost"] >= 0) &
            (cleaned_df["discount"] >= 0.0) &
            (cleaned_df["discount"] <= 1.0) &
            (cleaned_df["order_date"].notna())
        )

        invalid_count = len(cleaned_df) - int(valid_mask.sum())
        cleaned_df = cleaned_df[valid_mask].copy()
        report["invalid_rows_removed"] = invalid_count

        # Ensure correct final data types
        cleaned_df["quantity"] = cleaned_df["quantity"].astype(int)
        cleaned_df["discount"] = cleaned_df["discount"].astype(float)
        cleaned_df["unit_price"] = cleaned_df["unit_price"].astype(float)
        cleaned_df["cost"] = cleaned_df["cost"].astype(float)

        report["final_rows"] = len(cleaned_df)

        print(f"[OK] Data Cleaning Completed:")
        print(f"  - Initial Rows: {report['initial_rows']:,}")
        print(f"  - Duplicates Removed: {report['duplicates_removed']:,}")
        print(f"  - Invalid Rows Filtered: {report['invalid_rows_removed']:,}")
        print(f"  - Cleaned Final Rows: {report['final_rows']:,}")

        return cleaned_df, report

if __name__ == "__main__":
    from src.ingestion.ingest import DataIngestionEngine
    import os

    path = "data/raw/sales_data.csv"
    if os.path.exists(path):
        ingestor = DataIngestionEngine()
        df, _ = ingestor.ingest(path)
        cleaner = DataCleaningPipeline()
        cleaned_df, report = cleaner.clean(df)

import os
import pandas as pd
from typing import Tuple, Dict, Any

REQUIRED_COLUMNS = [
    "order_id", "order_date", "customer_id", "customer_name",
    "product_id", "product_name", "category", "quantity",
    "unit_price", "discount", "cost", "city", "state", "region"
]

class DataIngestionEngine:
    def __init__(self, required_columns: list = None):
        self.required_columns = required_columns or REQUIRED_COLUMNS

    def load_file(self, file_path: str) -> pd.DataFrame:
        """Reads CSV or Excel file into a pandas DataFrame."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at path: {file_path}")

        ext = os.path.splitext(file_path)[-1].lower()
        if ext == ".csv":
            df = pd.read_csv(file_path)
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Only .csv and .xlsx supported.")
        
        return df

    def validate_schema(self, df: pd.DataFrame) -> Tuple[bool, list]:
        """Checks if all required columns are present in DataFrame."""
        missing = [col for col in self.required_columns if col not in df.columns]
        return len(missing) == 0, missing

    def generate_ingestion_report(self, file_path: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Generates structured data quality report during ingestion phase."""
        is_valid_schema, missing_cols = self.validate_schema(df)
        
        duplicate_count = int(df.duplicated().sum())
        missing_values_sum = int(df.isna().sum().sum())
        missing_by_col = df.isna().sum().to_dict()

        report = {
            "file_path": file_path,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "valid_schema": is_valid_schema,
            "missing_columns": missing_cols,
            "duplicate_records": duplicate_count,
            "total_missing_cells": missing_values_sum,
            "missing_cells_by_column": {k: int(v) for k, v in missing_by_col.items() if v > 0}
        }
        return report

    def ingest(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Main ingestion entry point: loads file, validates, and reports metrics."""
        print(f"Ingesting file: {file_path}")
        df = self.load_file(file_path)
        report = self.generate_ingestion_report(file_path, df)

        if not report["valid_schema"]:
            raise ValueError(f"Schema Validation Failed! Missing required columns: {report['missing_columns']}")

        print(f"[OK] Ingestion complete: {report['total_rows']:,} rows, {report['total_columns']} columns ingested.")
        if report["duplicate_records"] > 0:
            print(f"[WARN] Warning: {report['duplicate_records']:,} duplicate rows detected.")
        if report["total_missing_cells"] > 0:
            print(f"[WARN] Warning: {report['total_missing_cells']:,} missing cells detected.")

        return df, report

if __name__ == "__main__":
    ingestor = DataIngestionEngine()
    test_path = "data/raw/sales_data.csv"
    if os.path.exists(test_path):
        df, rep = ingestor.ingest(test_path)
        print("Report:", rep)

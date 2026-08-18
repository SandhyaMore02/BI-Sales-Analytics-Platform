import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List

class StatisticalAnalyticsEngine:
    def __init__(self):
        pass

    def compute_summary_statistics(self, df: pd.DataFrame, columns: List[str] = None) -> Dict[str, Dict[str, float]]:
        """Computes mean, median, std, min, max, skewness for numerical variables."""
        if columns is None:
            columns = ["revenue", "profit", "profit_margin_pct", "quantity", "discount"]

        results = {}
        for col in columns:
            if col in df.columns:
                series = df[col].dropna()
                results[col] = {
                    "mean": float(series.mean()),
                    "median": float(series.median()),
                    "std_dev": float(series.std()),
                    "min": float(series.min()),
                    "max": float(series.max()),
                    "skewness": float(series.skew())
                }
        return results

    def compute_correlation_matrix(self, df: pd.DataFrame, columns: List[str] = None) -> Dict[str, Dict[str, float]]:
        """Computes Pearson correlation matrix between key financial/operating fields."""
        if columns is None:
            columns = ["quantity", "unit_price", "discount", "cost", "revenue", "profit", "profit_margin_pct"]
        
        valid_cols = [c for c in columns if c in df.columns]
        corr_df = df[valid_cols].corr(method="pearson").round(4)
        return corr_df.to_dict()

    def detect_outliers_iqr(self, df: pd.DataFrame, column: str = "revenue", multiplier: float = 1.5) -> pd.DataFrame:
        """Detects outliers using the Interquartile Range (IQR) method."""
        if column not in df.columns:
            raise KeyError(f"Column '{column}' not present in DataFrame.")
        
        series = df[column].dropna()
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - (multiplier * iqr)
        upper_bound = q3 + (multiplier * iqr)

        outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)].copy()
        outliers["outlier_reason"] = np.where(outliers[column] < lower_bound, f"Below IQR Low ({lower_bound:.2f})", f"Above IQR High ({upper_bound:.2f})")
        return outliers

    def detect_outliers_zscore(self, df: pd.DataFrame, column: str = "revenue", threshold: float = 3.0) -> pd.DataFrame:
        """Detects outliers using Z-score method (|Z| > threshold)."""
        if column not in df.columns:
            raise KeyError(f"Column '{column}' not present in DataFrame.")
        
        series = df[column].dropna()
        z_scores = np.abs(stats.zscore(series))
        outliers = df.iloc[np.where(z_scores > threshold)[0]].copy()
        return outliers

if __name__ == "__main__":
    from src.ingestion.ingest import DataIngestionEngine
    from src.cleaning.clean import DataCleaningPipeline
    from src.features.engineer import FeatureEngineeringPipeline
    import os

    path = "data/raw/sales_data.csv"
    if os.path.exists(path):
        df, _ = DataIngestionEngine().ingest(path)
        clean_df, _ = DataCleaningPipeline().clean(df)
        fe_df = FeatureEngineeringPipeline().add_features(clean_df)
        stats_engine = StatisticalAnalyticsEngine()
        print("Summary Stats:", stats_engine.compute_summary_statistics(fe_df))
        outliers = stats_engine.detect_outliers_iqr(fe_df, "revenue")
        print(f"Detected {len(outliers):,} revenue outliers.")

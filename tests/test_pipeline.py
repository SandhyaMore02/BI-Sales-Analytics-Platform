import pytest
import pandas as pd
import numpy as np
from src.data.generate_dataset import generate_sales_dataset
from src.ingestion.ingest import DataIngestionEngine
from src.cleaning.clean import DataCleaningPipeline
from src.features.engineer import FeatureEngineeringPipeline
from src.statistics.stats_engine import StatisticalAnalyticsEngine
from src.database.connection import create_db_engine
from src.database.loader import StarSchemaETLLoader
from src.analytics.query_engine import SQLAnalyticsEngine

@pytest.fixture
def sample_sales_file(tmp_path):
    file_path = str(tmp_path / "test_sales.csv")
    generate_sales_dataset(output_path=file_path, num_rows=1000, seed=123)
    return file_path

def test_data_ingestion(sample_sales_file):
    ingestor = DataIngestionEngine()
    df, report = ingestor.ingest(sample_sales_file)
    assert len(df) >= 1000
    assert report["valid_schema"] is True
    assert report["total_rows"] == len(df)

def test_data_cleaning(sample_sales_file):
    ingestor = DataIngestionEngine()
    df, _ = ingestor.ingest(sample_sales_file)
    cleaner = DataCleaningPipeline()
    cleaned_df, report = cleaner.clean(df)
    
    assert report["final_rows"] > 0
    assert cleaned_df["quantity"].min() > 0
    assert cleaned_df["discount"].min() >= 0.0
    assert cleaned_df["discount"].max() <= 1.0
    assert cleaned_df["city"].isna().sum() == 0

def test_feature_engineering(sample_sales_file):
    ingestor = DataIngestionEngine()
    df, _ = ingestor.ingest(sample_sales_file)
    cleaner = DataCleaningPipeline()
    cleaned_df, _ = cleaner.clean(df)
    
    fe = FeatureEngineeringPipeline()
    fe_df = fe.add_features(cleaned_df)
    
    assert "revenue" in fe_df.columns
    assert "profit" in fe_df.columns
    assert "profit_margin_pct" in fe_df.columns
    assert "year_month" in fe_df.columns

    # Verify math for first row
    row0 = fe_df.iloc[0]
    expected_rev = round(row0["quantity"] * row0["unit_price"] * (1.0 - row0["discount"]), 2)
    assert row0["revenue"] == expected_rev

def test_statistics_engine(sample_sales_file):
    ingestor = DataIngestionEngine()
    df, _ = ingestor.ingest(sample_sales_file)
    cleaner = DataCleaningPipeline()
    cleaned_df, _ = cleaner.clean(df)
    fe_df = FeatureEngineeringPipeline().add_features(cleaned_df)
    
    stats_engine = StatisticalAnalyticsEngine()
    stats_res = stats_engine.compute_summary_statistics(fe_df)
    assert "revenue" in stats_res
    assert stats_res["revenue"]["mean"] > 0

    outliers = stats_engine.detect_outliers_iqr(fe_df, "revenue")
    assert isinstance(outliers, pd.DataFrame)

def test_database_etl_and_sql_analytics(sample_sales_file):
    ingestor = DataIngestionEngine()
    df, _ = ingestor.ingest(sample_sales_file)
    cleaner = DataCleaningPipeline()
    cleaned_df, _ = cleaner.clean(df)
    fe_df = FeatureEngineeringPipeline().add_features(cleaned_df)
    
    engine = create_db_engine()
    loader = StarSchemaETLLoader(engine=engine)
    loader.load_star_schema(fe_df)
    
    analytics = SQLAnalyticsEngine(engine=engine)
    kpis = analytics.get_kpi_summary()
    
    assert kpis["total_orders"] > 0
    assert kpis["total_revenue"] > 0

import os
import sys
from src.data.generate_dataset import generate_sales_dataset
from src.ingestion.ingest import DataIngestionEngine
from src.cleaning.clean import DataCleaningPipeline
from src.features.engineer import FeatureEngineeringPipeline
from src.database.connection import create_db_engine
from src.database.loader import StarSchemaETLLoader
from src.analytics.query_engine import SQLAnalyticsEngine
from src.statistics.stats_engine import StatisticalAnalyticsEngine

def run_full_pipeline():
    print("=" * 70)
    print(" AI-POWERED BI & SALES ANALYTICS PLATFORM - END-TO-END PIPELINE ")
    print("=" * 70)

    # 1. Dataset Generation
    raw_path = "data/raw/sales_data.csv"
    generate_sales_dataset(output_path=raw_path, num_rows=55000)

    # 2. Data Ingestion & Schema Validation
    ingestor = DataIngestionEngine()
    df_raw, ingestion_report = ingestor.ingest(raw_path)

    # 3. Data Cleaning Pipeline
    cleaner = DataCleaningPipeline()
    df_clean, cleaning_report = cleaner.clean(df_raw)

    # Save cleaned data to processed folder
    os.makedirs("data/processed", exist_ok=True)
    df_clean.to_csv("data/processed/cleaned_sales.csv", index=False)

    # 4. Feature Engineering
    fe_engine = FeatureEngineeringPipeline()
    df_featured = fe_engine.add_features(df_clean)
    df_featured.to_csv("data/processed/featured_sales.csv", index=False)

    # 5. Database ETL (Star Schema DDL & Data Loading)
    print("\n--- Initializing Star Schema Database ETL ---")
    engine = create_db_engine()
    loader = StarSchemaETLLoader(engine=engine)
    loader.load_star_schema(df_featured)

    # 6. SQL Analytics Execution
    print("\n--- Executing SQL Analytics Engine ---")
    analytics = SQLAnalyticsEngine(engine=engine)
    kpis = analytics.get_kpi_summary()

    print("\n" + "=" * 50)
    print(" EXECUTIVE BUSINESS KPI SUMMARY ")
    print("=" * 50)
    print(f" Total Orders:             {kpis['total_orders']:,}")
    print(f" Unique Customers:         {kpis['unique_customers']:,}")
    print(f" Total Units Sold:         {kpis['total_units_sold']:,}")
    print(f" Total Revenue:            ${kpis['total_revenue']:,.2f}")
    print(f" Total Cost:               ${kpis['total_cost']:,.2f}")
    print(f" Total Net Profit:         ${kpis['total_profit']:,.2f}")
    print(f" Profit Margin:            {kpis['profit_margin_pct']}%")
    print(f" Avg Order Line Value:     ${kpis['avg_order_line_value']:,.2f}")
    print("=" * 50 + "\n")

    # 7. Statistical & Outlier Analysis
    print("--- Executing Statistical Engine & Outlier Analysis ---")
    stats_engine = StatisticalAnalyticsEngine()
    summary_stats = stats_engine.compute_summary_statistics(df_featured)
    outliers = stats_engine.detect_outliers_iqr(df_featured, "revenue")

    print(f" Summary Stats (Revenue Mean): ${summary_stats['revenue']['mean']:,.2f}")
    print(f" Summary Stats (Revenue Std):  ${summary_stats['revenue']['std_dev']:,.2f}")
    print(f" Identified Outliers (IQR):   {len(outliers):,} records")

    print("\n[OK] Milestone 1 Execution Completed Successfully!")

if __name__ == "__main__":
    run_full_pipeline()

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine
from src.database.connection import create_db_engine

class StarSchemaETLLoader:
    def __init__(self, engine: Engine = None):
        self.engine = engine or create_db_engine()

    def init_schema(self):
        """Applies table creation schema DDL if tables do not exist."""
        is_sqlite = "sqlite" in str(self.engine.url)
        
        if is_sqlite:
            ddl = """
            CREATE TABLE IF NOT EXISTS dim_date (
                date_id INTEGER PRIMARY KEY,
                full_date TEXT NOT NULL UNIQUE,
                year INTEGER NOT NULL,
                quarter TEXT NOT NULL,
                quarter_num INTEGER NOT NULL,
                month INTEGER NOT NULL,
                month_name TEXT NOT NULL,
                year_month TEXT NOT NULL,
                day INTEGER NOT NULL,
                day_of_week TEXT NOT NULL,
                week_of_year INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS dim_customer (
                customer_key INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT UNIQUE NOT NULL,
                customer_name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS dim_product (
                product_key INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT UNIQUE NOT NULL,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                unit_price REAL NOT NULL,
                unit_cost REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS dim_region (
                region_key INTEGER PRIMARY KEY AUTOINCREMENT,
                region TEXT NOT NULL,
                state TEXT NOT NULL,
                city TEXT NOT NULL,
                UNIQUE(region, state, city)
            );

            CREATE TABLE IF NOT EXISTS fact_sales (
                sales_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                date_id INTEGER NOT NULL REFERENCES dim_date(date_id),
                customer_key INTEGER NOT NULL REFERENCES dim_customer(customer_key),
                product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
                region_key INTEGER NOT NULL REFERENCES dim_region(region_key),
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                discount REAL NOT NULL,
                cost REAL NOT NULL,
                revenue REAL NOT NULL,
                total_cost REAL NOT NULL,
                profit REAL NOT NULL,
                profit_margin_pct REAL NOT NULL
            );
            """
        else:
            with open("sql/schema/01_star_schema.sql", "r") as f:
                ddl = f.read()

        with self.engine.begin() as conn:
            for statement in ddl.split(";"):
                stmt = statement.strip()
                if stmt:
                    conn.execute(text(stmt))
        print("[OK] Star Schema database DDL initialized.")

    def reset_tables(self):
        """Clears existing data from fact and dimension tables before reloading."""
        with self.engine.begin() as conn:
            conn.execute(text("DELETE FROM fact_sales;"))
            conn.execute(text("DELETE FROM dim_region;"))
            conn.execute(text("DELETE FROM dim_product;"))
            conn.execute(text("DELETE FROM dim_customer;"))
            conn.execute(text("DELETE FROM dim_date;"))

    def load_star_schema(self, df: pd.DataFrame, clear_existing: bool = True):
        """Populates dimension tables and fact table from processed DataFrame."""
        self.init_schema()
        if clear_existing:
            self.reset_tables()

        print("Populating Star Schema tables...")

        # 1. Dim Date
        dates_df = df[[
            "order_date", "year", "quarter", "quarter_num",
            "month", "month_name", "year_month", "day",
            "day_of_week", "week_of_year"
        ]].drop_duplicates().copy()

        dates_df["full_date"] = pd.to_datetime(dates_df["order_date"]).dt.strftime("%Y-%m-%d")
        dates_df["date_id"] = pd.to_datetime(dates_df["order_date"]).dt.strftime("%Y%m%d").astype(int)
        dates_df = dates_df.drop(columns=["order_date"]).drop_duplicates(subset=["date_id"])

        dates_df.to_sql("dim_date", self.engine, if_exists="append", index=False, chunksize=100)
        print(f"  - Loaded {len(dates_df):,} rows into dim_date")

        # 2. Dim Customer
        cust_df = df[["customer_id", "customer_name"]].drop_duplicates(subset=["customer_id"]).copy()
        cust_df.to_sql("dim_customer", self.engine, if_exists="append", index=False, chunksize=100)
        print(f"  - Loaded {len(cust_df):,} rows into dim_customer")

        # 3. Dim Product
        prod_df = df[["product_id", "product_name", "category", "unit_price", "cost"]].drop_duplicates(subset=["product_id"]).copy()
        prod_df = prod_df.rename(columns={"cost": "unit_cost"})
        prod_df.to_sql("dim_product", self.engine, if_exists="append", index=False, chunksize=100)
        print(f"  - Loaded {len(prod_df):,} rows into dim_product")

        # 4. Dim Region
        region_df = df[["region", "state", "city"]].drop_duplicates().copy()
        region_df.to_sql("dim_region", self.engine, if_exists="append", index=False, chunksize=100)
        print(f"  - Loaded {len(region_df):,} rows into dim_region")

        # Read back surrogate keys for Fact table mapping
        dim_cust_db = pd.read_sql("SELECT customer_key, customer_id FROM dim_customer", self.engine)
        dim_prod_db = pd.read_sql("SELECT product_key, product_id FROM dim_product", self.engine)
        dim_reg_db = pd.read_sql("SELECT region_key, region, state, city FROM dim_region", self.engine)

        # 5. Fact Sales Mapping
        fact_df = df.copy()
        fact_df["date_id"] = pd.to_datetime(fact_df["order_date"]).dt.strftime("%Y%m%d").astype(int)

        fact_df = fact_df.merge(dim_cust_db, on="customer_id", how="left")
        fact_df = fact_df.merge(dim_prod_db, on="product_id", how="left")
        fact_df = fact_df.merge(dim_reg_db, on=["region", "state", "city"], how="left")

        fact_columns = [
            "order_id", "date_id", "customer_key", "product_key", "region_key",
            "quantity", "unit_price", "discount", "cost", "revenue", "total_cost",
            "profit", "profit_margin_pct"
        ]

        fact_to_load = fact_df[fact_columns].copy()
        fact_to_load.to_sql("fact_sales", self.engine, if_exists="append", index=False, chunksize=500)

        print(f"  - Loaded {len(fact_to_load):,} rows into fact_sales table!")
        print("[OK] Star Schema ETL Load Complete.")

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
        loader = StarSchemaETLLoader()
        loader.load_star_schema(fe_df)

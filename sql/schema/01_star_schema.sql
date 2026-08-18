-- Star Schema DDL for AI-Powered BI & Sales Analytics Platform

-- 1. Date Dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_id INT PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INT NOT NULL,
    quarter VARCHAR(5) NOT NULL,
    quarter_num INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    year_month VARCHAR(7) NOT NULL,
    day INT NOT NULL,
    day_of_week VARCHAR(20) NOT NULL,
    week_of_year INT NOT NULL
);

-- 2. Customer Dimension
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(255) NOT NULL
);

-- 3. Product Dimension
CREATE TABLE IF NOT EXISTS dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    unit_cost NUMERIC(10, 2) NOT NULL
);

-- 4. Geography / Region Dimension
CREATE TABLE IF NOT EXISTS dim_region (
    region_key SERIAL PRIMARY KEY,
    region VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    CONSTRAINT unique_region_state_city UNIQUE(region, state, city)
);

-- 5. Sales Fact Table
CREATE TABLE IF NOT EXISTS fact_sales (
    sales_id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    date_id INT NOT NULL REFERENCES dim_date(date_id),
    customer_key INT NOT NULL REFERENCES dim_customer(customer_key),
    product_key INT NOT NULL REFERENCES dim_product(product_key),
    region_key INT NOT NULL REFERENCES dim_region(region_key),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    discount NUMERIC(5, 4) NOT NULL CHECK (discount >= 0 AND discount <= 1),
    cost NUMERIC(10, 2) NOT NULL CHECK (cost >= 0),
    revenue NUMERIC(12, 2) NOT NULL,
    total_cost NUMERIC(12, 2) NOT NULL,
    profit NUMERIC(12, 2) NOT NULL,
    profit_margin_pct NUMERIC(6, 2) NOT NULL
);

-- Performance Indexes for BI & SQL Analytics
CREATE INDEX IF NOT EXISTS idx_fact_sales_date ON fact_sales(date_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_customer ON fact_sales(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product ON fact_sales(product_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_region ON fact_sales(region_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_order ON fact_sales(order_id);

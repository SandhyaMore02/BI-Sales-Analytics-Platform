# AI-Powered Business Intelligence & Sales Analytics Platform

An end-to-end analytics platform that converts raw sales and business data into clean analytical datasets, structured SQL star-schema models, business metrics, Power BI dashboards, and AI-generated business insights.

---

## 🚀 Architecture Overview

```text
CSV / Excel Data
       │
       ▼
Data Ingestion Engine (Schema Validation)
       │
       ▼
Data Cleaning Pipeline (Deduplication, Imputation, Normalization)
       │
       ▼
Feature Engineering (Revenue, Profit, Margin %, Date Dimensions)
       │
       ▼
PostgreSQL / SQLite Database (Star Schema: Dimensions & Fact Tables)
       │
       ├───► SQL Analytics Engine (CTEs, Window Functions, MoM Growth)
       ├───► Statistical Engine (Mean/Median, Outliers, Correlation)
       ├───► Power BI Interactive Dashboards (DAX & Star Schema Model)
       └───► AI Business Insight Engine (LLM Context & Recommendations)
```

---

## 🛠 Tech Stack

- **Data Processing & Analytics**: Python 3.12, Pandas, NumPy, SciPy, Scikit-learn
- **Database & Modeling**: PostgreSQL 16 (Docker Compose), SQLAlchemy, SQL (Star Schema DDL)
- **Visualization & BI**: Microsoft Power BI Desktop, DAX Measures
- **Backend & Application**: FastAPI, Streamlit, Pydantic, Uvicorn
- **AI Layer**: LLM API (Google Gemini / OpenAI API)
- **Infrastructure & Containerization**: Docker, Docker Compose, Git

---

## 📁 Repository Structure

```text
bi-sales-analytics/
│
├── data/
│   ├── raw/                 # Ingested raw datasets
│   ├── processed/           # Cleaned & featured analytical datasets
│   └── sample/              # Sample CSV datasets
│
├── sql/
│   ├── schema/              # Star Schema DDL (01_star_schema.sql)
│   └── analytics/           # Business query repository (01_business_queries.sql)
│
├── src/
│   ├── data/                # Synthetic data generator
│   ├── ingestion/           # Data ingestion & schema validator
│   ├── cleaning/            # Data cleaning pipeline
│   ├── features/            # Business metric feature engineering
│   ├── database/            # Database connection engine & ETL loader
│   ├── analytics/           # SQL analytics query engine
│   ├── statistics/          # Statistical analysis & outlier detection
│   └── ai/                  # AI insight generation engine
│
├── tests/                   # Automated Pytest test suite
├── docker-compose.yml       # Docker Compose service for PostgreSQL
├── requirements.txt         # Project dependencies
├── .env.example             # Environment template
└── run_pipeline.py          # End-to-end pipeline execution runner
```

---

## 📊 Star Schema Database Design

The analytical database follows a **Star Schema** dimensional modeling design:

- **`dim_date`**: `date_id`, `full_date`, `year`, `quarter`, `month`, `month_name`, `year_month`, `day`, `day_of_week`
- **`dim_customer`**: `customer_key`, `customer_id`, `customer_name`
- **`dim_product`**: `product_key`, `product_id`, `product_name`, `category`, `unit_price`, `unit_cost`
- **`dim_region`**: `region_key`, `region`, `state`, `city`
- **`fact_sales`**: `sales_id`, `order_id`, `date_id`, `customer_key`, `product_key`, `region_key`, `quantity`, `unit_price`, `discount`, `cost`, `revenue`, `total_cost`, `profit`, `profit_margin_pct`

---

## ⚡ Quick Start

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/your-username/bi-sales-analytics.git
cd bi-sales-analytics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start PostgreSQL via Docker Compose

```bash
docker compose up -d
```

### 3. Run End-to-End Analytics Pipeline

```bash
python run_pipeline.py
```

This runs the complete workflow:
1. Generates 55,000+ synthetic sales transactions.
2. Ingests and validates dataset schema.
3. Cleans, normalizes text casing, and handles missing/invalid values.
4. Engineers revenue, profit, margin, and date dimensional features.
5. Initializes database schema and loads Star Schema tables.
6. Computes SQL KPIs, product rankings, regional trends, and Month-over-Month growth.
7. Executes statistical distribution analysis and IQR outlier detection.

---

## 🔍 Business Metrics Computed

- **Total Revenue**: $\sum (\text{Quantity} \times \text{Unit Price} \times (1 - \text{Discount}))$
- **Total Cost**: $\sum (\text{Quantity} \times \text{Unit Cost})$
- **Total Net Profit**: $\text{Revenue} - \text{Total Cost}$
- **Profit Margin %**: $(\text{Profit} / \text{Revenue}) \times 100$
- **Month-over-Month (MoM) Growth %**: $\frac{\text{Revenue}_t - \text{Revenue}_{t-1}}{\text{Revenue}_{t-1}} \times 100$

# Power BI Data Model & Dashboard Guide

This directory provides the complete blueprint for building the **Power BI Desktop Business Intelligence Dashboard** for the AI-Powered BI & Sales Analytics Platform.

---

## 1. Connecting Power BI to the Star Schema Database

### Option A: Direct PostgreSQL Database Connection
1. Ensure your Docker PostgreSQL container is active (`docker compose up -d`).
2. Open **Microsoft Power BI Desktop**.
3. Select **Get Data** → **PostgreSQL database**.
4. Enter server details:
   - **Server**: `localhost:5432`
   - **Database**: `bi_analytics`
   - **Data Connectivity Mode**: Import
5. Enter credentials:
   - **Username**: `postgres`
   - **Password**: `postgres`
6. Select the 5 Star Schema tables: `fact_sales`, `dim_date`, `dim_customer`, `dim_product`, `dim_region`.

### Option B: Local Processed CSV Import
If running in CSV mode:
- Select **Get Data** → **Text/CSV** → Import `data/processed/featured_sales.csv`.

---

## 2. Star Schema Data Model Relationships

In Power BI **Model View**, establish **1-to-Many ($1 : *$)** relationships with **Single Filter Direction** (Dimension filters Fact):

```text
                       ┌──────────────┐
                       │   dim_date   │
                       └──────┬───────┘
                              │ 1 (date_id)
                              ▼ * (date_id)
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ dim_customer │ 1 ──► │  fact_sales  │ ◄── 1 │ dim_product  │
└──────────────┘     * └──────────────┘ *     └──────────────┘
  (customer_key)              ▲ *              (product_key)
                              │ 1 (region_key)
                       ┌──────┴───────┐
                       │  dim_region  │
                       └──────────────┘
```

- `dim_date[date_id]` (1) $\rightarrow$ `fact_sales[date_id]` (*)
- `dim_customer[customer_key]` (1) $\rightarrow$ `fact_sales[customer_key]` (*)
- `dim_product[product_key]` (1) $\rightarrow$ `fact_sales[product_key]` (*)
- `dim_region[region_key]` (1) $\rightarrow$ `fact_sales[region_key]` (*)

---

## 3. DAX Measures Repository

Create a dedicated Measure Table `_Measures` in Power BI and paste the following DAX calculations:

### Financial Metrics

```DAX
Total Revenue = 
SUM(fact_sales[revenue])
```

```DAX
Total Cost = 
SUM(fact_sales[total_cost])
```

```DAX
Total Net Profit = 
SUM(fact_sales[profit])
```

```DAX
Profit Margin % = 
DIVIDE([Total Net Profit], [Total Revenue], 0)
```

```DAX
Average Order Line Value = 
AVERAGE(fact_sales[revenue])
```

---

### Volume Metrics

```DAX
Total Orders = 
DISTINCTCOUNT(fact_sales[order_id])
```

```DAX
Total Units Sold = 
SUM(fact_sales[quantity])
```

```DAX
Unique Customers = 
DISTINCTCOUNT(fact_sales[customer_key])
```

---

### Time-Intelligence & MoM Growth Measures

```DAX
Previous Month Revenue = 
CALCULATE(
    [Total Revenue],
    DATEADD(dim_date[full_date], -1, MONTH)
)
```

```DAX
MoM Growth % = 
VAR PrevRev = [Previous Month Revenue]
RETURN
IF(
    ISBLANK(PrevRev) || PrevRev = 0,
    BLANK(),
    DIVIDE([Total Revenue] - PrevRev, PrevRev, 0)
)
```

```DAX
YTD Revenue = 
TOTALYTD([Total Revenue], dim_date[full_date])
```

---

## 4. Power BI 4-Page Visual Layout Blueprint

### Page 1 — Executive Overview
- **Header Card Visuals**: `Total Revenue`, `Total Net Profit`, `Profit Margin %`, `Total Orders`, `MoM Growth %`.
- **Main Chart**: Monthly Line Chart (`dim_date[year_month]` vs `[Total Revenue]` and `[Total Net Profit]`).
- **Secondary Chart**: Regional Column Chart (`dim_region[region]` vs `[Total Revenue]`).
- **Category Donut Chart**: `dim_product[category]` vs `[Total Revenue]`.

### Page 2 — Product Analytics
- **Top 10 Products Table**: `dim_product[product_name]`, `[Total Units Sold]`, `[Total Revenue]`, `[Profit Margin %]`.
- **Scatter Plot**: X-Axis = `[Total Revenue]`, Y-Axis = `[Profit Margin %]`, Size = `[Total Units Sold]`, Details = `dim_product[product_name]`.

### Page 3 — Regional Analytics
- **Geographic Matrix**: Drill-down hierarchy (`dim_region[region]` $\rightarrow$ `state` $\rightarrow$ `city`).
- **Regional Margin Comparison**: Clustered Bar Chart of `[Profit Margin %]` across regions.

### Page 4 — Customer Analytics
- **Top Customers**: Ranked by `[Total Revenue]`.
- **Customer Purchase Frequency & Average Spend Matrix**.

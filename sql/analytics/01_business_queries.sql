-- Business Analytics SQL Queries for AI-Powered BI & Sales Analytics Platform

-- Query 1: Executive KPI Overview Summary
SELECT
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(DISTINCT f.customer_key) AS unique_customers,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(SUM(f.total_cost), 2) AS total_cost,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS overall_profit_margin_pct,
    ROUND(AVG(f.revenue), 2) AS avg_order_line_value
FROM fact_sales f;

-- Query 2: Product Performance & Ranking (Window Functions)
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS profit_margin_pct,
    RANK() OVER (ORDER BY SUM(f.revenue) DESC) AS revenue_rank,
    RANK() OVER (ORDER BY SUM(f.profit) DESC) AS profit_rank
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC;

-- Query 3: Regional Sales & Margin Breakdown
SELECT
    r.region,
    r.state,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS profit_margin_pct
FROM fact_sales f
JOIN dim_region r ON f.region_key = r.region_key
GROUP BY r.region, r.state
ORDER BY total_revenue DESC;

-- Query 4: Month-over-Month (MoM) Growth Analysis (CTE + LAG Window Function)
WITH monthly_revenue AS (
    SELECT
        d.year,
        d.month,
        d.year_month,
        SUM(f.revenue) AS current_month_revenue,
        SUM(f.profit) AS current_month_profit
    FROM fact_sales f
    JOIN dim_date d ON f.date_id = d.date_id
    GROUP BY d.year, d.month, d.year_month
)
SELECT
    year_month,
    ROUND(current_month_revenue, 2) AS revenue,
    ROUND(LAG(current_month_revenue) OVER (ORDER BY year, month), 2) AS previous_month_revenue,
    ROUND(
        (current_month_revenue - LAG(current_month_revenue) OVER (ORDER BY year, month)) 
        / NULLIF(LAG(current_month_revenue) OVER (ORDER BY year, month), 0) * 100.0, 2
    ) AS mom_growth_pct,
    ROUND(current_month_profit, 2) AS profit
FROM monthly_revenue
ORDER BY year, month;

-- Query 5: Customer Contribution Ranking (Top 10 Customers)
SELECT
    c.customer_id,
    c.customer_name,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.revenue), 2) AS total_spend,
    ROUND(SUM(f.profit), 2) AS total_profit_contributed,
    ROUND(AVG(f.revenue), 2) AS avg_transaction_value
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spend DESC
LIMIT 10;

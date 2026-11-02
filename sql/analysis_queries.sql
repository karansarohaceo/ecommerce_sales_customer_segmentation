USE ecommerce_analytics;

-- 1. KPI overview
SELECT
    COUNT(DISTINCT InvoiceNo) AS total_orders,
    COUNT(DISTINCT CustomerID) AS unique_customers,
    COUNT(*) AS line_items,
    ROUND(SUM(Revenue), 2) AS total_revenue,
    ROUND(SUM(Revenue) / NULLIF(COUNT(DISTINCT InvoiceNo), 0), 2) AS average_order_value
FROM order_items;

-- 2. Monthly revenue and order count
SELECT OrderMonth,
       ROUND(SUM(Revenue), 2) AS revenue,
       COUNT(DISTINCT InvoiceNo) AS orders
FROM order_items
GROUP BY OrderMonth
ORDER BY OrderMonth;

-- 3. Top 10 products by revenue
SELECT Description,
       SUM(Quantity) AS units_sold,
       ROUND(SUM(Revenue), 2) AS revenue
FROM order_items
GROUP BY Description
ORDER BY revenue DESC
LIMIT 10;

-- 4. Revenue by country
SELECT Country,
       COUNT(DISTINCT InvoiceNo) AS orders,
       COUNT(DISTINCT CustomerID) AS customers,
       ROUND(SUM(Revenue), 2) AS revenue
FROM order_items
GROUP BY Country
ORDER BY revenue DESC;

-- 5. Customer-level RFM features
-- Snapshot date is derived from the latest date in the loaded data.
WITH snapshot AS (
    SELECT DATE_ADD(MAX(InvoiceDate), INTERVAL 1 DAY) AS snapshot_date
    FROM order_items
)
SELECT oi.CustomerID,
       DATEDIFF(s.snapshot_date, MAX(oi.InvoiceDate)) AS Recency,
       COUNT(DISTINCT oi.InvoiceNo) AS Frequency,
       ROUND(SUM(oi.Revenue), 2) AS Monetary
FROM order_items oi
CROSS JOIN snapshot s
GROUP BY oi.CustomerID, s.snapshot_date
ORDER BY Monetary DESC;

-- 6. Weekday sales pattern
SELECT DAYNAME(InvoiceDate) AS weekday,
       ROUND(SUM(Revenue), 2) AS revenue
FROM order_items
GROUP BY DAYOFWEEK(InvoiceDate), DAYNAME(InvoiceDate)
ORDER BY DAYOFWEEK(InvoiceDate);

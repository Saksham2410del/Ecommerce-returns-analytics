-- Return analysis queries
-- Run with: sqlite3 ecommerce_data_warehouse.db < sql_analytics.sql


-- 1. Return rate by category
-- Count purchases and returns in each category, then returns / purchases
SELECT
    product_category,
    SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchases,
    SUM(CASE WHEN event_type = 'return' THEN 1 ELSE 0 END) AS returns,
    ROUND(SUM(CASE WHEN event_type = 'return' THEN 1 ELSE 0 END) * 100.0
          / SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END), 2) AS return_rate_pct
FROM transactions
GROUP BY product_category
ORDER BY return_rate_pct DESC;


-- 2. Refunds by category and each category's share of all refunds
SELECT
    product_category,
    COUNT(*) AS returns,
    ROUND(SUM(refund_amount), 2) AS total_refund,
    ROUND(SUM(refund_amount) * 100.0
          / (SELECT SUM(refund_amount) FROM transactions WHERE event_type = 'return'), 2) AS share_of_refunds_pct
FROM transactions
WHERE event_type = 'return'
GROUP BY product_category
ORDER BY total_refund DESC;


-- 3. Why are items being returned? Reasons in each category
SELECT
    product_category,
    reason,
    COUNT(*) AS returns
FROM transactions
WHERE event_type = 'return'
GROUP BY product_category, reason
ORDER BY product_category, returns DESC;


-- 4. Customers who returned the most items (top 10)
SELECT
    customer_id,
    COUNT(*) AS items_returned,
    ROUND(SUM(refund_amount), 2) AS total_refund
FROM transactions
WHERE event_type = 'return'
GROUP BY customer_id
HAVING COUNT(*) >= 2
ORDER BY items_returned DESC, total_refund DESC
LIMIT 10;

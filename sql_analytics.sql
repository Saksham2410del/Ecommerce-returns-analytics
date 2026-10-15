WITH category_purchases AS (
    SELECT 
        product_category, 
        COUNT(*) AS total_purchases
    FROM transactions
    WHERE event_type = 'purchase'
    GROUP BY product_category
),
category_returns AS (
    SELECT 
        product_category, 
        COUNT(*) AS total_returns
    FROM transactions
    WHERE event_type = 'return'
    GROUP BY product_category
)
SELECT 
    p.product_category,
    p.total_purchases,
    COALESCE(r.total_returns, 0) AS total_returns,
    ROUND(CAST(COALESCE(r.total_returns, 0) AS FLOAT) / p.total_purchases * 100, 2) AS return_rate_pct
FROM category_purchases p
LEFT JOIN category_returns r ON p.product_category = r.product_category
ORDER BY return_rate_pct DESC;

SELECT 
    product_category,
    COUNT(*) AS total_returns,
    ROUND(SUM(refund_amount), 2) AS total_refund_inr,
    ROUND(AVG(refund_amount), 2) AS avg_refund_inr,
    ROUND(SUM(refund_amount) * 100.0 / (SELECT SUM(refund_amount) FROM transactions WHERE event_type = 'return'), 2) AS pct_of_all_refunds
FROM transactions
WHERE event_type = 'return'
GROUP BY product_category
ORDER BY total_refund_inr DESC;

WITH customer_returns AS (
    SELECT 
        customer_id,
        COUNT(*) AS total_returned_items,
        ROUND(SUM(refund_amount), 2) AS total_refund_received
    FROM transactions
    WHERE event_type = 'return'
    GROUP BY customer_id
)
SELECT 
    customer_id,
    total_returned_items,
    total_refund_received,
    RANK() OVER (ORDER BY total_returned_items DESC, total_refund_received DESC) AS returner_rank
FROM customer_returns
WHERE total_returned_items >= 2
ORDER BY returner_rank
LIMIT 10;

SELECT 
    product_category,
    reason,
    COUNT(*) AS total_cases,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY product_category), 2) AS reason_share_pct
FROM transactions
WHERE event_type = 'return'
GROUP BY product_category, reason
ORDER BY product_category, total_cases DESC;

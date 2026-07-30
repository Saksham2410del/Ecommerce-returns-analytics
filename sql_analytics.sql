-- Identify worst performing categories
SELECT 
    product_category,
    COUNT(*) AS total_returns,
    ROUND(AVG(refund_amount), 2) AS average_refund_value
FROM events
WHERE event_type = 'return'
GROUP BY product_category
ORDER BY total_returns DESC;

-- Rank serial returners
WITH CustomerReturnStats AS (
    SELECT 
        user_id,
        COUNT(event_id) AS total_items_returned,
        SUM(refund_amount) AS total_money_refunded
    FROM events
    WHERE event_type = 'return'
    GROUP BY user_id
)
SELECT 
    user_id,
    total_items_returned,
    total_money_refunded,
    RANK() OVER(ORDER BY total_items_returned DESC) as returner_rank
FROM CustomerReturnStats
WHERE total_items_returned > 3
ORDER BY returner_rank
LIMIT 10;

-- Return rate by category
WITH CategoryPurchases AS (
    SELECT product_category, COUNT(*) as total_purchases
    FROM events
    WHERE event_type = 'purchase'
    GROUP BY product_category
),
CategoryReturns AS (
    SELECT product_category, COUNT(*) as total_returns
    FROM events
    WHERE event_type = 'return'
    GROUP BY product_category
)
SELECT 
    p.product_category,
    p.total_purchases,
    COALESCE(r.total_returns, 0) AS total_returns,
    ROUND(CAST(COALESCE(r.total_returns, 0) AS FLOAT) / p.total_purchases * 100, 2) AS return_rate_percentage
FROM CategoryPurchases p
LEFT JOIN CategoryReturns r ON p.product_category = r.product_category
ORDER BY return_rate_percentage DESC;

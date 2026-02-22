-- Aggregate transactions per minute
SELECT
    DATE_TRUNC('minute', timestamp) AS minute,
    COUNT(*) AS total_tx,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed,
    SUM(CASE WHEN status = 'denied' THEN 1 ELSE 0 END) AS denied,
    SUM(CASE WHEN status = 'reversed' THEN 1 ELSE 0 END) AS reversed
FROM transactions
GROUP BY 1
ORDER BY 1;
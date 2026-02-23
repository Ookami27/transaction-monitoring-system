-- Hybrid baseline anomaly detection for hourly POS sales
-- Assumes a table `checkout_data` with one row per hour and the following columns:
-- time               -> hour of day (or timestamp truncated to hour)
-- today_sales        -> sales volume for today
-- yesterday_sales    -> sales volume for yesterday
-- week_avg_sales     -> average sales for this hour over the last week
-- week_std_sales     -> standard deviation of sales for this hour over the last week
-- month_avg_sales    -> average sales for this hour over the last month
-- month_std_sales    -> standard deviation of sales for this hour over the last month

WITH base AS (
    SELECT
        time,
        today_sales,
        yesterday_sales,
        week_avg_sales,
        week_std_sales,
        month_avg_sales,
        month_std_sales
    FROM checkout_data
),

deviation_calc AS (
    SELECT
        time,
        today_sales,
        yesterday_sales,
        week_avg_sales,
        week_std_sales,
        month_avg_sales,
        month_std_sales,

        -- 1) Operational baseline: today vs yesterday (percent deviation)
        (today_sales - yesterday_sales) * 1.0 / NULLIF(yesterday_sales, 0) AS pct_vs_yesterday,

        -- 2) Structural baseline: Z-score vs monthly mean
        CASE
            WHEN month_std_sales IS NOT NULL AND month_std_sales > 0 THEN
                (today_sales - month_avg_sales) / month_std_sales
            ELSE NULL
        END AS zscore_vs_month,

        -- 3) Tactical baseline: Z-score vs weekly mean
        CASE
            WHEN week_std_sales IS NOT NULL AND week_std_sales > 0 THEN
                (today_sales - week_avg_sales) / week_std_sales
            ELSE NULL
        END AS zscore_vs_week

    FROM base
)

SELECT
    time,
    today_sales,
    yesterday_sales,
    week_avg_sales,
    month_avg_sales,
    pct_vs_yesterday,
    zscore_vs_week,
    zscore_vs_month,

    CASE
        -- Operational anomaly: strong deviation vs yesterday
        WHEN ABS(pct_vs_yesterday) > 0.20 THEN 'OPERATIONAL_ANOMALY'

        -- Structural anomaly: above monthly mean + 3σ
        WHEN zscore_vs_month IS NOT NULL AND zscore_vs_month > 3 THEN 'STRUCTURAL_ANOMALY'

        -- Tactical anomaly: above weekly mean + 3σ
        WHEN zscore_vs_week IS NOT NULL AND zscore_vs_week > 3 THEN 'SEASONAL_ANOMALY'

        ELSE 'NORMAL'
    END AS anomaly_flag

FROM deviation_calc
ORDER BY time;
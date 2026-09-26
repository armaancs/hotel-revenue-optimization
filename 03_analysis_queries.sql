-- 03_analysis_queries.sql
-- RevP/Optimize — the five revenue questions. Run each and WRITE DOWN the answer;
-- these numbers fill the [brackets] in your resume bullets and your memo.
-- Run:  sqlite3 hotel.db < 03_analysis_queries.sql   (or paste one at a time)

-- === Q1. Headline KPIs =====================================================
-- Total realized revenue, overall cancellation rate, blended ADR.
SELECT
    ROUND(SUM(realized_revenue), 0)                         AS total_realized_revenue,
    ROUND(100.0 * SUM(is_canceled) / COUNT(*), 1)           AS cancellation_rate_pct,
    ROUND(AVG(adr), 2)                                      AS avg_adr,
    COUNT(*)                                                AS total_bookings
FROM fact_bookings;

-- === Q2. Rate benchmarking — how much is underpriced? ======================
-- % of bookings priced >10% below their room-type/month benchmark.
SELECT
    SUM(is_underpriced)                                     AS underpriced_bookings,
    COUNT(*)                                                AS total_bookings,
    ROUND(100.0 * SUM(is_underpriced) / COUNT(*), 1)        AS underpriced_pct,
    ROUND(SUM(CASE WHEN is_underpriced=1 THEN benchmark_adr - adr ELSE 0 END)
          * 1.0, 0)                                         AS adr_gap_total
FROM benchmarked_bookings;

-- === Q3. Cancellation revenue leakage by segment ===========================
-- Potential revenue lost to cancellations, ranked by market segment.
SELECT
    market_segment,
    COUNT(*)                                                AS bookings,
    ROUND(100.0 * SUM(is_canceled) / COUNT(*), 1)           AS cancel_rate_pct,
    ROUND(SUM(CASE WHEN is_canceled=1 THEN potential_revenue ELSE 0 END), 0)
                                                            AS revenue_lost
FROM fact_bookings
GROUP BY market_segment
ORDER BY revenue_lost DESC;

-- === Q4. Leakage by lead-time bucket =======================================
-- Do longer lead times cancel more? (pricing/deposit-policy insight)
SELECT
    lead_time_bucket,
    COUNT(*)                                                AS bookings,
    ROUND(100.0 * SUM(is_canceled) / COUNT(*), 1)           AS cancel_rate_pct,
    ROUND(SUM(CASE WHEN is_canceled=1 THEN potential_revenue ELSE 0 END), 0)
                                                            AS revenue_lost
FROM fact_bookings
GROUP BY lead_time_bucket
ORDER BY cancel_rate_pct DESC;

-- === Q5. Channel margin — profit, not just volume ==========================
-- Which distribution channel delivers the best modeled margin?
SELECT
    distribution_channel,
    COUNT(*)                                                AS bookings,
    ROUND(SUM(realized_revenue), 0)                         AS realized_revenue,
    ROUND(SUM(modeled_margin), 0)                           AS modeled_margin,
    ROUND(100.0 * SUM(modeled_margin) / NULLIF(SUM(realized_revenue),0), 1)
                                                            AS margin_pct
FROM fact_bookings
GROUP BY distribution_channel
ORDER BY modeled_margin DESC;
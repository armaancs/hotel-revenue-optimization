-- 02_build_views.sql
-- RevP/Optimize — analytical views over the cleaned bookings table.
-- Run against hotel.db, e.g.:  sqlite3 hotel.db < 02_build_views.sql
-- These views are your "reusable data assets" (a posting requirement).

-- ---------------------------------------------------------------------------
-- Fact view: one clean row per booking with the fields the dashboard needs.
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS fact_bookings;
CREATE VIEW fact_bookings AS
SELECT
    ROWID                         AS booking_id,
    hotel,
    is_canceled,
    arrival_date,
    arrival_date_year             AS year,
    arrival_date_month            AS month_name,
    arrival_month_num             AS month_num,
    lead_time,
    market_segment,
    distribution_channel,
    reserved_room_type,
    assigned_room_type,
    total_nights,
    adr,
    potential_revenue,
    realized_revenue,
    cost_rate,
    modeled_margin,
    CASE
        WHEN lead_time <= 7   THEN '0-7 days'
        WHEN lead_time <= 30  THEN '8-30 days'
        WHEN lead_time <= 90  THEN '31-90 days'
        WHEN lead_time <= 180 THEN '91-180 days'
        ELSE '180+ days'
    END                           AS lead_time_bucket
FROM bookings;

-- ---------------------------------------------------------------------------
-- Rate benchmark: the average ADR for each hotel + room type + month.
-- A booking priced below its benchmark is a candidate for "underpriced".
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS rate_benchmark;
CREATE VIEW rate_benchmark AS
SELECT
    hotel,
    reserved_room_type,
    month_num,
    ROUND(AVG(adr), 2)            AS benchmark_adr,
    COUNT(*)                      AS n_bookings
FROM fact_bookings
GROUP BY hotel, reserved_room_type, month_num;

-- ---------------------------------------------------------------------------
-- Benchmarked bookings: each booking joined to its benchmark, with a flag.
-- "underpriced" = ADR more than 10% below the benchmark for its group.
-- ---------------------------------------------------------------------------
DROP VIEW IF EXISTS benchmarked_bookings;
CREATE VIEW benchmarked_bookings AS
SELECT
    f.*,
    b.benchmark_adr,
    ROUND(f.adr - b.benchmark_adr, 2)                       AS adr_gap,
    CASE WHEN f.adr < 0.90 * b.benchmark_adr THEN 1 ELSE 0 END AS is_underpriced
FROM fact_bookings f
JOIN rate_benchmark b
  ON f.hotel = b.hotel
 AND f.reserved_room_type = b.reserved_room_type
 AND f.month_num = b.month_num;
# Hotel Revenue Optimization & Rate Benchmarking Dashboard

An end-to-end revenue-analytics pipeline over **117,000+ real hotel bookings**: Python cleaning → SQLite analytical views → SQL analysis → Power BI dashboard. It measures revenue, flags underpriced bookings against a rate benchmark, quantifies cancellation leakage, and compares channel margins.

**Stack:** Python (pandas), SQLite / SQL, Power BI

## Key findings

| Metric | Result |
|---|---|
| Bookings analyzed (after cleaning) | 117,398 |
| Total realized revenue | €25.99M |
| Cancellation rate | 37.5% |
| Average daily rate (ADR) | €103.50 |
| Bookings >10% below their rate benchmark | **38.0%** (44,618 bookings) |
| Potential revenue lost to cancellations | **€16.7M** |

- **Cancellations concentrate in Online TA and Groups.** Online TA accounts for €10.2M of lost revenue; Groups cancel at 61.7%, the highest of any major segment.
- **Lead time predicts cancellation.** Bookings made 180+ days out cancel at 57.2%, versus 9.7% for bookings made within a week. That supports tiered deposit policies for long-lead bookings.
- **Direct bookings earn the best margin.** Under the modeled cost assumptions, Direct returns a 45% margin versus 28% for travel agents / tour operators, even though TA/TO drives most of the volume.

## Dashboard

`Hotel Revenue Optimization Dashboard.pbix` (Power BI Desktop) has two pages:

1. **Revenue Overview:** KPI cards, revenue over time, and revenue by market segment.
2. **Rate Benchmarking & Leakage:** ADR against benchmark by room type, count of underpriced bookings, cancellation loss by segment, and channel margin.

## Pipeline

| Step | File | What it does |
|---|---|---|
| 1 | `01 clean and load.py` | Cleans the raw CSV, adds derived revenue and margin fields, writes `hotel.db` and `exports/bookings.csv` |
| 2 | `02_build_views.sql` (run via `run_sql.py`) | Creates the `fact_bookings`, `rate_benchmark` and `benchmarked_bookings` views |
| 3 | `03_analysis_queries.sql` | Runs five revenue questions: KPIs, underpricing, leakage by segment, leakage by lead time, channel margin |
| 4 | `Hotel Revenue Optimization Dashboard.pbix` | Power BI dashboard built on the exported views |

`peek.py` is a quick check that prints sample rows and the row count from `hotel.db`.

### Data cleaning

- Filled nulls: `children` → 0, `country` → `UNK`, `agent` / `company` → 0
- Dropped rows with ADR ≤ 0 or ≥ 1,000 (removes a negative rate and a ~5,400 outlier)
- Dropped bookings with zero guests or zero nights
- Derived `total_nights`, `potential_revenue` (ADR × nights), `realized_revenue` (0 if canceled), `arrival_date` and lead-time buckets

### Rate benchmark

The benchmark is the average ADR for each **hotel × reserved room type × arrival month**. A booking counts as **underpriced** when its ADR is more than 10% below its group's benchmark.

## Modeled costs (important caveat)

The public dataset contains no cost data. To demonstrate margin analysis, the pipeline applies an **assumed cost-of-sale rate by distribution channel**:

| Channel | Assumed cost rate |
|---|---|
| Direct | 55% |
| Corporate | 60% |
| GDS | 70% |
| TA/TO | 72% |
| Undefined / other | 68% |

Margin figures are therefore illustrative. They show how the analysis works, not actual hotel profitability. Replace `channel_cost_rate` in `01 clean and load.py` with real costs when they are available.

## Reproducing

Data files are not committed (see `.gitignore`), so the pipeline has to be rerun locally.

1. Download `hotel_bookings.csv` from Kaggle ([Hotel Booking Demand](https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand)) into the project folder.
2. Install pandas and run the pipeline:
   ```bash
   pip install pandas
   python "01 clean and load.py"
   python run_sql.py
   ```
   Then run the queries in `03_analysis_queries.sql` in any SQLite client, e.g. `sqlite3 hotel.db < 03_analysis_queries.sql`.
3. To refresh the dashboard, export the `fact_bookings` and `benchmarked_bookings` views to CSV and open the `.pbix` in Power BI Desktop.

## Data source

Antonio, Almeida & Nunes (2019), *Hotel booking demand datasets*, Data in Brief. The data covers two hotels in Portugal (a resort hotel and a city hotel) with arrivals from 2015 to 2017. Monetary values are in euros.

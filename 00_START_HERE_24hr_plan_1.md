# RevP/Optimize — the 24-hour build plan

Yes, this is doable in a day. Below is a scoped-down version with the SQL and cleaning code pre-written, so your time goes into *running and understanding* it, not writing from scratch. Realistic hands-on time: **8–12 hours.** The rest of the 24 is buffer, breaks, and Power BI's learning curve if it's your first time.

**One hard prerequisite:** install **Power BI Desktop** (free, Windows) *before* the clock starts. On Mac, use Power BI in a Windows VM, or substitute **Tableau Public** (also free) — the SQL half is identical and the resume bullet just says Tableau instead. Don't lose 3 hours to setup mid-build.

**The scope cut that makes 24h realistic:** 2 dashboard pages, not 3. Drop the separate margin page; fold one margin visual into page 2. You can add page 3 later if you want. Everything else stays.

---

## Hour-by-hour

### Block 1 — Setup & data (Hours 0–2)
- Download `hotel_bookings.csv` from Kaggle ("Hotel Booking Demand", by jessemostipak).
- Install SQLite (or just use the Python script below — it needs nothing but pandas).
- Run `01_clean_and_load.py` (provided). It cleans the known quirks and writes `hotel.db`.
- **Checkpoint:** you can open `hotel.db` and `SELECT COUNT(*) FROM bookings;` returns ~119k.

### Block 2 — SQL views & analysis (Hours 2–6)
- Run `02_build_views.sql` (provided). It creates the fact view, the benchmark, the leakage query, and the margin layer.
- Run each query in `03_analysis_queries.sql` (provided) and **write the answer down** — you need these numbers for your resume bullets and interviews.
- **Checkpoint:** you have real numbers for: total revenue, cancellation rate, % of bookings below benchmark, revenue lost to cancellations, best-margin channel.

### Block 3 — Power BI (Hours 6–11)
- Connect Power BI Desktop to `hotel.db` (via ODBC) **or** the simpler path: export the views to CSV (the SQL file does this) and load those CSVs into Power BI. CSV import is faster and 100% fine for this.
- Page 1 — Revenue Overview: 4 KPI cards, revenue-over-time line, revenue-by-segment bar.
- Page 2 — Rate Benchmarking & Leakage: ADR-vs-benchmark by room type, below-benchmark count, cancellation-loss by segment, one channel-margin visual.
- **Checkpoint:** two clean pages, filters working, no broken visuals.

### Block 4 — Polish & ship (Hours 11–14)
- Write the one-page recommendation memo (template provided).
- Export one Excel summary tab.
- Push to GitHub with the README (provided), plus a screenshot of the dashboard.
- **Checkpoint:** repo link works, README renders, screenshot visible.

**Hours 14–24 are buffer.** If you're on track, use them to add the 3rd page or tighten visuals. If you're behind, they're why you'll still finish.

---

## What's in the starter kit (separate files)
1. `01_clean_and_load.py` — cleans the CSV, handles the outliers/nulls, writes `hotel.db` and CSV exports.
2. `02_build_views.sql` — fact view, benchmark, margin layer.
3. `03_analysis_queries.sql` — the 5 revenue questions, ready to run.
4. `README_template.md` — drop-in README with the honesty note about modeled costs.
5. `recommendation_memo_template.md` — the business-case one-pager.

---

## If you fall behind, cut in this order
1. Drop the Excel export (least important; SQL + dashboard carry the resume bullets).
2. Drop the channel-margin visual (keep the margin *query* so the bullet still holds).
3. Drop page 2's leakage visual, keep benchmarking.

**Never cut:** the SQL views, the benchmark query, and at least one working dashboard page. Those three are what make the resume bullets true.

---

## The bullets you'll be able to write by hour 14
Same as the full spec — fill the brackets with the numbers you wrote down in Block 2:
> - Built an end-to-end revenue-analytics pipeline over 119,000+ real hotel bookings in SQL, with reusable views for rate, revenue, and margin analysis
> - Designed a Power BI dashboard surfacing ADR, cancellation leakage, and rate-benchmark gaps, turning 119K rows into actionable pricing insights
> - Built a SQL rate-benchmarking model flagging **[N]%** of bookings as underpriced, and quantified **\$[X]** in cancellation revenue leakage with a costed policy recommendation

Honest, buildable in a day, and every word defensible.

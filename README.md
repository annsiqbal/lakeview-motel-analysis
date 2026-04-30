# 🏨 Lakeview Motel — Hospitality Business Intelligence Analysis

> **Real-world data analytics project** built during an engagement with an active independent motel business in Ontario. All pricing, revenue, and occupancy figures are authentic operational data. The business name and location have been anonymized to protect client privacy.

---

## 📌 Project Overview

This project analyzes 19 months of real operational data (September 2024 – April 2026) from an 11-room independent motel in small-town Ontario — a seasonal tourist destination with a hard summer peak driven by a major annual local festival. The data was sourced directly from the business's handwritten reservation logs and POS reporting system.

**The goal:** Transform raw paper-based booking records and POS revenue exports into a structured analytical pipeline answering real business questions — and delivering recommendations the owner can act on immediately.

> ⚠️ **Privacy Note:** This project was conducted with a real operating business. The motel name, town, owner names, and corporate client names have been anonymized. All financial figures (rates, revenue, transaction counts) are authentic and unmodified.

---

## 📊 Key Findings

| Metric | Value |
|---|---|
| Total bookings analyzed | 393 |
| Total revenue tracked | $187,857 CAD |
| Date range | Sept 2024 – Apr 2026 |
| Annual Festival week revenue (1 week) | **$18,760** |
| Average nightly rate | $160 |
| Top booking channel | Booking.com (33%) |
| Corporate revenue share | 27% |
| Google rating | ⭐ 4.7 / 5.0 |
| Positive review rate | 87% |
| POS-verified months | Jan 2026: $11,889 / Feb: $7,403 / Mar: $10,110 |

---

## 🗂️ Repository Structure

```
lakeview-motel-analysis/
│
├── data/
│   ├── bookings.csv          # 393 anonymized booking records (Sept 2024–Apr 2026)
│   ├── monthly_revenue.csv   # 19 months revenue incl. POS-verified figures
│   └── reviews.csv           # 30 guest reviews across Google, TripAdvisor, Booking.com
│
├── outputs/
│   ├── figure1_dashboard.png  # Revenue, occupancy, RevPAR, booking channel charts
│   ├── figure2_seasonal.png   # Seasonal patterns, festival impact, DoW demand
│   ├── figure3_sentiment.png  # Review sentiment & theme frequency analysis
│   └── figure4_forecast.png   # 6-month revenue forecast with confidence intervals
│
├── lakeview_motel_analysis.py  # Full analysis script (Python + SQLite)
└── README.md
```

---

## 🔍 Analysis Breakdown

### 1. Data Cleaning & Feature Engineering
- Digitized 19 months of handwritten reservation calendars into structured CSV
- Created derived features: `season`, `is_weekend`, `is_annual_festival`, `is_corporate`, `revenue_per_night`, `year_month`
- Handled multi-night stays, monthly corporate bookings, and seasonal rate tiers correctly
- All guest names anonymized to `Guest_001` format for privacy

### 2. SQL Business Queries (SQLite)
Six production-style SQL queries answering core business questions:

```sql
-- Annual Festival vs Regular Summer performance
SELECT
    CASE WHEN is_annual_festival = 1 THEN 'Festival Week'
         ELSE 'Regular Summer' END AS period,
    COUNT(*)                        AS bookings,
    SUM(total_revenue)              AS total_revenue,
    ROUND(AVG(rate_per_night), 2)   AS avg_rate,
    ROUND(AVG(num_nights), 1)       AS avg_nights
FROM bookings
WHERE season = 'Summer'
GROUP BY is_annual_festival
```

| Period | Bookings | Revenue | Avg Rate | Avg Nights |
|---|---|---|---|---|
| Festival Week | 11 | $18,760 | $243.64 | 7.0 |
| Regular Summer | 102 | $45,880 | $225.49 | 2.0 |

### 3. Hospitality KPI Calculations
Industry-standard metrics computed per month:
- **Occupancy Rate** = Nights Sold / (11 rooms × days in month)
- **ADR** (Average Daily Rate) = Revenue / Nights Sold
- **RevPAR** (Revenue Per Available Room) = Revenue / Total Available Room-Nights

### 4. Seasonal Trend Analysis
- Hard peak: June–August (occupancy >85% in peak weeks)
- Annual festival week: 100% occupancy, highest ADR of the year at $243/night
- Winter floor: Corporate clients provide ~27% of annual revenue through extended stays
- Shoulder seasons (May, October): Identified as the primary growth opportunity

### 5. Guest Sentiment Analysis
Manual keyword-frequency NLP on 30 cross-platform reviews:
- **#1 theme:** Cleanliness (77% of reviews)
- **#2 theme:** Staff warmth (60%)
- **#3 theme:** Location (40%)
- Negative reviews (7%): pricing transparency gap, one room-type mix-up

### 6. Revenue Forecasting
Seasonal decomposition-based forecast for the next 6 months:

| Month | Seasonal Index | Forecast |
|---|---|---|
| April | 0.55 | $5,268 |
| May | 0.72 | $6,808 |
| June | 1.13 | $10,783 |
| **July (Festival)** | **2.28** | **$21,690** |
| August | 2.03 | $19,275 |
| September | 0.90 | $8,549 |
| **Total (6 months)** | | **$72,373** |

---

## 📈 Visualizations

### Figure 1 — Business Intelligence Dashboard
Monthly gross revenue colour-coded by season, occupancy rate trend line with 80% target benchmark, RevPAR vs ADR dual-axis chart, and booking channel revenue share pie. POS-verified months marked with ✓.

### Figure 2 — Seasonal & Demand Patterns
Average occupancy by month (heat-coloured), festival week vs regular summer nightly rate comparison, and day-of-week check-in demand pattern.

### Figure 3 — Guest Sentiment Analysis
Cross-platform rating distribution, top review themes by frequency, positive/neutral/negative sentiment breakdown.

### Figure 4 — Revenue Forecast
19-month actuals with 6-month forward projection, ±12% confidence intervals, and festival peak annotation.

---

## 💡 Strategic Recommendations

| Priority | Area | Recommendation |
|---|---|---|
| 🔴 HIGH | Dynamic Pricing | 3-night minimum on peak summer weekends to reduce turnover |
| 🔴 HIGH | Festival Strategy | Early-bird booking page + January email campaign to past guests |
| 🔴 HIGH | Direct Bookings | "Book Direct" incentive to reduce OTA commission spend (~$25–40/booking) |
| 🟡 MEDIUM | Corporate Winter | Formalize preferred rate agreements with corporate clients |
| 🟡 MEDIUM | Guest Satisfaction | Pre-arrival room checklist; OTA rate parity review |
| 🟢 LOW | Shoulder Season | Victoria Day & Thanksgiving weekend packages with 2-night minimum |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `Python 3.12` | Core analysis |
| `pandas` | Data wrangling and transformation |
| `numpy` | KPI calculations |
| `matplotlib` | All charts and visualizations |
| `seaborn` | Statistical plots |
| `SQLite (via sqlite3)` | In-memory SQL queries |

---

## 🚀 How to Run

```bash
git clone https://github.com/YOUR_USERNAME/lakeview-motel-analysis.git
cd lakeview-motel-analysis

pip install pandas numpy matplotlib seaborn

python lakeview_motel_analysis.py
```

All 4 charts will be saved to the `outputs/` folder.

---

## 📝 Data Notes

- Booking records were digitized from handwritten monthly reservation calendars
- Revenue figures for the last 3 months are **POS-verified** from the business's Square reporting system
- Earlier months use revenue calculated from confirmed seasonal pricing × observed occupancy
- Guest names replaced with anonymous IDs (`Guest_001`, `Guest_002`, etc.)
- Corporate client names replaced with generic identifiers (`Corporate_Client_A`)
- Reviews reflect real guest feedback, rewritten to remove identifying location details
- Business name, location, and owner names withheld at client's request

---

## 👤 About This Project

This project was built using real data from an active independent motel business in Ontario as part of a data analytics portfolio. It demonstrates end-to-end analytical skills — data cleaning, SQL querying, KPI calculation, visualization, NLP, forecasting, and business communication.

**Analyst:** Anns Iqbal

---

*Real data. Real business. Real impact.*

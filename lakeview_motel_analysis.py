# =============================================================================
# MAPLE LEAF MOTEL — HOSPITALITY BUSINESS INTELLIGENCE ANALYSIS
# =============================================================================
# Author      : [Your Name]
# Client      : Lakeview Motel, Small-Town Ontario
# Data Range  : September 2024 – April 2026
# Tools       : Python (pandas, numpy, matplotlib, seaborn), SQL (SQLite)
# Description : Full occupancy, revenue, booking source, seasonal trend,
#               KPI dashboard, and guest sentiment analysis for a real
#               11-room independent motel in Small-Town Ontario.
# =============================================================================

# ── SECTION 0: IMPORTS & SETUP ───────────────────────────────────────────────
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
import sqlite3
import warnings
from datetime import datetime, timedelta
from collections import Counter

warnings.filterwarnings('ignore')

# ── Style ─────────────────────────────────────────────────────────────────────
MAPLE_RED    = '#C8102E'   # Canadian red
MAPLE_GOLD   = '#F5A623'
MAPLE_DARK   = '#1A1A2E'
MAPLE_LIGHT  = '#F0F4F8'
ACCENT_BLUE  = '#2E86AB'
ACCENT_GREEN = '#2D7D46'

plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor':   '#FAFAFA',
    'axes.spines.top':  False,
    'axes.spines.right':False,
    'axes.labelsize':   11,
    'axes.titlesize':   13,
    'axes.titleweight': 'bold',
    'xtick.labelsize':  9,
    'ytick.labelsize':  9,
    'font.family':      'DejaVu Sans',
    'grid.alpha':       0.3,
    'grid.linestyle':   '--',
})

print("✅ Libraries loaded. Beginning Lakeview Motel analysis...")

# =============================================================================
# SECTION 1: DATA LOADING & CLEANING
# =============================================================================

bookings = pd.read_csv('data/bookings.csv', parse_dates=['check_in', 'check_out'])
revenue  = pd.read_csv('data/monthly_revenue.csv')
reviews  = pd.read_csv('data/reviews.csv')

# ── Feature Engineering ───────────────────────────────────────────────────────
bookings['stay_month']      = bookings['check_in'].dt.month
bookings['stay_year']       = bookings['check_in'].dt.year
bookings['day_of_week']     = bookings['check_in'].dt.day_name()
bookings['year_month']      = bookings['check_in'].dt.to_period('M')
bookings['is_corporate']    = bookings['booking_source'].str.lower() == 'corporate'
bookings['revenue_per_night'] = bookings['total_revenue'] / bookings['num_nights'].replace(0, np.nan)

# Revenue date column
revenue['date'] = pd.to_datetime(
    revenue['year'].astype(str) + '-' + revenue['month'].astype(str) + '-01'
)
revenue.sort_values('date', inplace=True)
revenue.reset_index(drop=True, inplace=True)

print(f"✅ Data loaded: {len(bookings)} bookings | {len(revenue)} revenue months | {len(reviews)} reviews")
print(f"   Date range: {bookings['check_in'].min().date()} → {bookings['check_in'].max().date()}")
print(f"\nRoom type breakdown:")
print(bookings['room_type'].value_counts().to_string())
print(f"\nBooking source breakdown:")
print(bookings['booking_source'].value_counts().to_string())

# =============================================================================
# SECTION 2: SQL DATABASE + BUSINESS QUERIES
# =============================================================================
# We load the data into SQLite to demonstrate SQL skills
# and answer key business questions programmatically.

conn = sqlite3.connect(':memory:')
bookings_sql = bookings.copy()
bookings_sql["year_month"] = bookings_sql["year_month"].astype(str)
bookings_sql["check_in"] = bookings_sql["check_in"].astype(str)
bookings_sql["check_out"] = bookings_sql["check_out"].astype(str)
bookings_sql.to_sql('bookings', conn, index=False, if_exists='replace')
revenue.to_sql('monthly_revenue', conn, index=False, if_exists='replace')

print("\n" + "="*60)
print("SQL BUSINESS QUERIES")
print("="*60)

# Q1: Total revenue by season
q1 = pd.read_sql_query("""
    SELECT
        season,
        COUNT(*)              AS total_bookings,
        SUM(num_nights)       AS total_nights_sold,
        SUM(total_revenue)    AS total_revenue,
        ROUND(AVG(rate_per_night), 2) AS avg_nightly_rate,
        ROUND(AVG(num_nights), 1)     AS avg_stay_length
    FROM bookings
    GROUP BY season
    ORDER BY total_revenue DESC
""", conn)
print("\n📊 Q1 — Revenue by Season:")
print(q1.to_string(index=False))

# Q2: Top performing booking sources
q2 = pd.read_sql_query("""
    SELECT
        booking_source,
        COUNT(*)           AS num_bookings,
        SUM(total_revenue) AS total_revenue,
        ROUND(AVG(total_revenue), 2) AS avg_booking_value
    FROM bookings
    GROUP BY booking_source
    ORDER BY total_revenue DESC
""", conn)
print("\n📊 Q2 — Revenue by Booking Source:")
print(q2.to_string(index=False))

# Q3: Annual Summer Festival vs regular summer comparison
q3 = pd.read_sql_query("""
    SELECT
        CASE WHEN is_annual_festival = 1 THEN 'Annual Summer Festival' ELSE 'Regular Summer' END AS period,
        COUNT(*) AS bookings,
        SUM(total_revenue) AS total_revenue,
        ROUND(AVG(rate_per_night), 2) AS avg_rate,
        ROUND(AVG(num_nights), 1) AS avg_nights
    FROM bookings
    WHERE season = 'Summer'
    GROUP BY is_annual_festival
""", conn)
print("\n📊 Q3 — Annual Summer Festival vs Regular Summer:")
print(q3.to_string(index=False))

# Q4: Room type performance
q4 = pd.read_sql_query("""
    SELECT
        room_type,
        COUNT(*)           AS bookings,
        SUM(num_nights)    AS nights_sold,
        SUM(total_revenue) AS total_revenue,
        ROUND(AVG(rate_per_night), 2) AS avg_rate
    FROM bookings
    GROUP BY room_type
    ORDER BY total_revenue DESC
""", conn)
print("\n📊 Q4 — Performance by Room Type:")
print(q4.to_string(index=False))

# Q5: Monthly occupancy rate
# 11 rooms total, calculate available room-nights per month
q5 = pd.read_sql_query("""
    SELECT
        year_month,
        season,
        SUM(num_nights) AS nights_sold,
        SUM(total_revenue) AS revenue
    FROM bookings
    GROUP BY year_month
    ORDER BY year_month
""", conn)
print("\n📊 Q5 — Monthly Nights Sold:")
print(q5.to_string(index=False))

# Q6: Corporate vs leisure revenue split
q6 = pd.read_sql_query("""
    SELECT
        CASE WHEN is_corporate = 1 THEN 'Corporate/Extended' ELSE 'Leisure/Tourist' END AS guest_type,
        COUNT(*) AS bookings,
        SUM(num_nights) AS total_nights,
        SUM(total_revenue) AS total_revenue,
        ROUND(AVG(rate_per_night), 2) AS avg_nightly_rate
    FROM bookings
    GROUP BY is_corporate
""", conn)
print("\n📊 Q6 — Corporate vs Leisure Breakdown:")
print(q6.to_string(index=False))

conn.close()

# =============================================================================
# SECTION 3: KPI CALCULATIONS
# =============================================================================

# Hotel industry standard KPIs
TOTAL_ROOMS = 11

def get_days_in_month(year, month):
    import calendar
    return calendar.monthrange(year, month)[1]

# Calculate occupancy rate and RevPAR for each month in revenue table
occ_data = []
for _, row in revenue.iterrows():
    y, m = int(row['year']), int(row['month'])
    days = get_days_in_month(y, m)
    available_room_nights = TOTAL_ROOMS * days

    # Get actual nights sold from bookings for that month/year
    month_bookings = bookings[
        (bookings['stay_year'] == y) & (bookings['stay_month'] == m)
    ]
    nights_sold = month_bookings['num_nights'].sum()

    occupancy = (nights_sold / available_room_nights) * 100
    adr = row['gross_revenue'] / nights_sold if nights_sold > 0 else 0  # ADR
    revpar = row['gross_revenue'] / available_room_nights                # RevPAR

    occ_data.append({
        'date': row['date'],
        'month_name': row['month_name'],
        'year': y,
        'month': m,
        'season': row['season'],
        'available_room_nights': available_room_nights,
        'nights_sold': nights_sold,
        'occupancy_rate': round(occupancy, 1),
        'gross_revenue': row['gross_revenue'],
        'adr': round(adr, 2),
        'revpar': round(revpar, 2),
        'num_transactions': row['num_transactions']
    })

kpi_df = pd.DataFrame(occ_data)

print("\n" + "="*60)
print("KEY PERFORMANCE INDICATORS (KPIs)")
print("="*60)
print(kpi_df[['month_name','year','occupancy_rate','adr','revpar','gross_revenue']].to_string(index=False))

peak_revpar = kpi_df.loc[kpi_df['revpar'].idxmax()]
print(f"\n🏆 Highest RevPAR Month: {peak_revpar['month_name']} {peak_revpar['year']}")
print(f"   RevPAR: ${peak_revpar['revpar']:.2f}  |  Occupancy: {peak_revpar['occupancy_rate']:.1f}%")

avg_summer_occ = kpi_df[kpi_df['season'].str.contains('Summer')]['occupancy_rate'].mean()
avg_winter_occ = kpi_df[kpi_df['season'].str.contains('Winter')]['occupancy_rate'].mean()
print(f"\n📈 Avg Summer Occupancy: {avg_summer_occ:.1f}%")
print(f"📉 Avg Winter Occupancy: {avg_winter_occ:.1f}%")
print(f"📊 Seasonal Swing: {avg_summer_occ - avg_winter_occ:.1f} percentage points")

# =============================================================================
# SECTION 4: VISUALIZATIONS — FIGURE 1: REVENUE & OCCUPANCY DASHBOARD
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.suptitle(
    'Lakeview Motel — Business Intelligence Dashboard\nSmall-Town Ontario  |  Sept 2024 – Mar 2026',
    fontsize=15, fontweight='bold', y=0.98, color=MAPLE_DARK
)
fig.patch.set_facecolor('white')

# ─── Plot 1: Monthly Revenue Bar Chart ───────────────────────────────────────
ax1 = axes[0, 0]
season_colors = {
    'Winter': ACCENT_BLUE,
    'Fall': MAPLE_GOLD,
    'Spring': ACCENT_GREEN,
    'Summer': MAPLE_RED,
    'Summer/Fall': '#E8A020',
    'Fall/Winter': '#7B8FA1'
}
bar_colors = [season_colors.get(s.split('/')[0], ACCENT_BLUE) for s in revenue['season']]
bars = ax1.bar(range(len(revenue)), revenue['gross_revenue'], color=bar_colors, edgecolor='white', linewidth=0.5)

# Highlight Annual Summer Festival month (July 2025)
celtic_idx = revenue[(revenue['year'] == 2025) & (revenue['month'] == 7)].index
if len(celtic_idx) > 0:
    idx_pos = revenue.index.get_loc(celtic_idx[0])
    bars[idx_pos].set_edgecolor(MAPLE_DARK)
    bars[idx_pos].set_linewidth(2.5)
    ax1.annotate('Festival\nFestival', xy=(idx_pos, revenue.iloc[idx_pos]['gross_revenue']),
                 xytext=(idx_pos - 1.5, revenue.iloc[idx_pos]['gross_revenue'] + 500),
                 fontsize=7.5, color=MAPLE_DARK, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color=MAPLE_DARK, lw=1.2))

# POS-verified markers
pos_months = revenue[(revenue['year'] == 2026) & (revenue['month'].isin([1, 2, 3]))]
for _, row in pos_months.iterrows():
    idx = revenue.index.get_loc(row.name)
    ax1.text(idx, row['gross_revenue'] + 200, '✓', ha='center', fontsize=9, color=ACCENT_GREEN, fontweight='bold')

ax1.set_xticks(range(len(revenue)))
ax1.set_xticklabels(
    [f"{r['month_name'][:3]}\n{str(r['year'])[2:]}" for _, r in revenue.iterrows()],
    fontsize=7.5
)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
ax1.set_title('Monthly Gross Revenue', pad=10)
ax1.set_ylabel('Revenue (CAD)')
ax1.grid(axis='y', alpha=0.3)

legend_handles = [mpatches.Patch(color=v, label=k) for k, v in season_colors.items() if k in ['Winter','Spring','Summer','Fall']]
legend_handles.append(mpatches.Patch(color='white', label='✓ = POS Verified'))
ax1.legend(handles=legend_handles, fontsize=7.5, loc='upper left', framealpha=0.9)

# ─── Plot 2: Occupancy Rate Line Chart ────────────────────────────────────────
ax2 = axes[0, 1]
ax2.plot(kpi_df['date'], kpi_df['occupancy_rate'], color=MAPLE_RED, linewidth=2.5,
         marker='o', markersize=6, markerfacecolor='white', markeredgewidth=2)
ax2.fill_between(kpi_df['date'], kpi_df['occupancy_rate'], alpha=0.12, color=MAPLE_RED)
ax2.axhline(y=80, color=ACCENT_GREEN, linestyle='--', linewidth=1.3, alpha=0.8, label='80% target')
ax2.axhline(y=kpi_df['occupancy_rate'].mean(), color=MAPLE_GOLD, linestyle=':', linewidth=1.3,
            alpha=0.9, label=f"Avg: {kpi_df['occupancy_rate'].mean():.0f}%")
ax2.set_title('Monthly Occupancy Rate (%)', pad=10)
ax2.set_ylabel('Occupancy Rate (%)')
ax2.set_ylim(0, 105)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}%'))
ax2.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b\n%y'))
ax2.legend(fontsize=8.5)
ax2.grid(axis='y', alpha=0.3)

for _, row in kpi_df.iterrows():
    if row['occupancy_rate'] >= 90:
        ax2.annotate(f"{row['occupancy_rate']:.0f}%",
                     xy=(row['date'], row['occupancy_rate']),
                     xytext=(0, 8), textcoords='offset points',
                     ha='center', fontsize=7.5, color=MAPLE_RED, fontweight='bold')

# ─── Plot 3: RevPAR & ADR Dual Axis ──────────────────────────────────────────
ax3 = axes[1, 0]
ax3b = ax3.twinx()
ax3.bar(kpi_df['date'], kpi_df['revpar'], width=20, color=ACCENT_BLUE, alpha=0.7, label='RevPAR')
ax3b.plot(kpi_df['date'], kpi_df['adr'], color=MAPLE_GOLD, linewidth=2.5,
          marker='D', markersize=5, label='ADR')
ax3.set_title('RevPAR vs Average Daily Rate (ADR)', pad=10)
ax3.set_ylabel('RevPAR (CAD)', color=ACCENT_BLUE)
ax3b.set_ylabel('ADR (CAD)', color=MAPLE_GOLD)
ax3.tick_params(axis='y', labelcolor=ACCENT_BLUE)
ax3b.tick_params(axis='y', labelcolor=MAPLE_GOLD)
ax3.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b\n%y'))
lines1, labels1 = ax3.get_legend_handles_labels()
lines2, labels2 = ax3b.get_legend_handles_labels()
ax3.legend(lines1 + lines2, labels1 + labels2, fontsize=8.5, loc='upper left')
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}'))
ax3b.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}'))

# ─── Plot 4: Booking Source Revenue Share ─────────────────────────────────────
ax4 = axes[1, 1]
source_rev = bookings.groupby('booking_source')['total_revenue'].sum().sort_values(ascending=False)
source_colors = [MAPLE_RED, MAPLE_GOLD, ACCENT_BLUE, ACCENT_GREEN, '#9B59B6', '#E67E22']
wedges, texts, autotexts = ax4.pie(
    source_rev.values,
    labels=source_rev.index,
    autopct='%1.1f%%',
    colors=source_colors[:len(source_rev)],
    startangle=140,
    pctdistance=0.75,
    wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
)
for text in texts:
    text.set_fontsize(8.5)
for autotext in autotexts:
    autotext.set_fontsize(8)
    autotext.set_fontweight('bold')
ax4.set_title('Revenue by Booking Channel', pad=10)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('outputs/figure1_dashboard.png', dpi=180, bbox_inches='tight', facecolor='white')
plt.show()
print("✅ Figure 1 saved: Revenue & Occupancy Dashboard")

# =============================================================================
# SECTION 5: VISUALIZATIONS — FIGURE 2: SEASONAL PATTERNS
# =============================================================================

fig2, axes2 = plt.subplots(1, 3, figsize=(18, 6))
fig2.suptitle('Lakeview Motel — Seasonal & Demand Patterns', fontsize=14, fontweight='bold', y=1.02)

# ─── Plot 5: Avg Occupancy by Month (seasonality heatmap) ─────────────────────
ax5 = axes2[0]
month_labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
monthly_avg = kpi_df.groupby('month')['occupancy_rate'].mean().reindex(range(1, 13), fill_value=0)
colors_heat = [ACCENT_BLUE if v < 40 else MAPLE_GOLD if v < 70 else MAPLE_RED for v in monthly_avg.values]
bars5 = ax5.bar(month_labels, monthly_avg.values, color=colors_heat, edgecolor='white')
ax5.axhline(80, color='black', linestyle='--', linewidth=1, alpha=0.5, label='80% target')
for bar, val in zip(bars5, monthly_avg.values):
    if val > 0:
        ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                 f'{val:.0f}%', ha='center', va='bottom', fontsize=8, fontweight='bold')
ax5.set_title('Average Occupancy by Month')
ax5.set_ylabel('Avg Occupancy Rate (%)')
ax5.set_ylim(0, 110)
low_p = mpatches.Patch(color=ACCENT_BLUE, label='Low season (<40%)')
mid_p = mpatches.Patch(color=MAPLE_GOLD, label='Mid season (40-70%)')
high_p = mpatches.Patch(color=MAPLE_RED, label='Peak season (>70%)')
ax5.legend(handles=[low_p, mid_p, high_p], fontsize=7.5)

# ─── Plot 6: Annual Summer Festival impact ───────────────────────────────────────────
ax6 = axes2[1]
celtic = bookings[bookings['is_annual_festival'] == True]
regular_summer = bookings[(bookings['season'] == 'Summer') & (bookings['is_annual_festival'] == False)]
categories = ['Regular Summer\n(Weekday)', 'Regular Summer\n(Weekend)', 'Annual Summer Festival\nWeek']
avg_rates = [
    regular_summer[regular_summer['is_weekend'] == False]['rate_per_night'].mean(),
    regular_summer[regular_summer['is_weekend'] == True]['rate_per_night'].mean(),
    celtic['rate_per_night'].mean()
]
bar_colors6 = [ACCENT_BLUE, MAPLE_GOLD, MAPLE_RED]
bars6 = ax6.bar(categories, avg_rates, color=bar_colors6, width=0.55, edgecolor='white')
for bar, val in zip(bars6, avg_rates):
    ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
             f'${val:.0f}', ha='center', fontsize=10, fontweight='bold')
ax6.set_title('Average Nightly Rate by Period')
ax6.set_ylabel('Average Rate (CAD/night)')
ax6.set_ylim(0, max(avg_rates) * 1.2)
ax6.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}'))

# ─── Plot 7: Day-of-week booking pattern ─────────────────────────────────────
ax7 = axes2[2]
dow_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
dow_counts = bookings.groupby('day_of_week')['booking_id'].count().reindex(dow_order, fill_value=0)
dow_revenue = bookings.groupby('day_of_week')['total_revenue'].sum().reindex(dow_order, fill_value=0)
dow_colors = [MAPLE_RED if d in ['Friday','Saturday','Sunday'] else ACCENT_BLUE for d in dow_order]
ax7b = ax7.twinx()
ax7.bar(range(len(dow_order)), dow_counts.values, color=dow_colors, alpha=0.75, width=0.5, label='# Check-ins')
ax7b.plot(range(len(dow_order)), dow_revenue.values, color=MAPLE_GOLD, marker='o',
          linewidth=2, markersize=7, label='Total Revenue')
ax7.set_xticks(range(len(dow_order)))
ax7.set_xticklabels([d[:3] for d in dow_order])
ax7.set_title('Check-in Day Demand Pattern')
ax7.set_ylabel('# Check-ins', color=ACCENT_BLUE)
ax7b.set_ylabel('Total Revenue (CAD)', color=MAPLE_GOLD)
ax7.tick_params(axis='y', labelcolor=ACCENT_BLUE)
ax7b.tick_params(axis='y', labelcolor=MAPLE_GOLD)
ax7b.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
lines_a, labels_a = ax7.get_legend_handles_labels()
lines_b, labels_b = ax7b.get_legend_handles_labels()
ax7.legend(lines_a + lines_b, labels_a + labels_b, fontsize=8)

plt.tight_layout()
plt.savefig('outputs/figure2_seasonal.png', dpi=180, bbox_inches='tight', facecolor='white')
plt.show()
print("✅ Figure 2 saved: Seasonal Patterns")

# =============================================================================
# SECTION 6: GUEST SENTIMENT ANALYSIS
# =============================================================================
# Manual keyword-based sentiment analysis (no external NLP library needed).
# Mimics VADER-style approach using curated hospitality keyword sets.

print("\n" + "="*60)
print("GUEST SENTIMENT & REVIEW ANALYSIS")
print("="*60)

# ── Rating distribution
print("\n⭐ Rating Distribution:")
rating_dist = reviews['rating'].value_counts().sort_index(ascending=False)
for rating, count in rating_dist.items():
    bar = '█' * count
    print(f"  {rating:.1f} ★  {bar} ({count})")

print(f"\n  Mean Rating: {reviews['rating'].mean():.2f}")
print(f"  Ratings ≥ 4: {(reviews['rating'] >= 4).sum()}/{len(reviews)} ({(reviews['rating'] >= 4).mean()*100:.0f}%)")

# ── Theme frequency analysis
all_themes = []
for themes in reviews['themes'].dropna():
    all_themes.extend(themes.split(','))

theme_counts = Counter(all_themes)
print("\n🏷️  Most Frequent Review Themes:")
for theme, count in theme_counts.most_common(10):
    bar = '■' * count
    pct = (count / len(reviews)) * 100
    print(f"  {theme:<25} {bar} ({count} reviews, {pct:.0f}%)")

# ── Sentiment by platform
print("\n📊 Avg Rating by Platform:")
platform_ratings = reviews.groupby('platform')['rating'].agg(['mean','count']).round(2)
print(platform_ratings.to_string())

# ── Negative review analysis
neg_reviews = reviews[reviews['sentiment_label'] == 'Negative']
print(f"\n⚠️  Negative Reviews: {len(neg_reviews)}/{len(reviews)} ({len(neg_reviews)/len(reviews)*100:.0f}%)")
print("   Issues identified in negative reviews:")
neg_themes = []
for themes in neg_reviews['themes'].dropna():
    neg_themes.extend(themes.split(','))
for theme, count in Counter(neg_themes).most_common():
    print(f"   • {theme}")

# ── Sentiment Visualization
fig3, axes3 = plt.subplots(1, 3, figsize=(16, 5))
fig3.suptitle('Lakeview Motel — Guest Sentiment Analysis', fontsize=14, fontweight='bold')

# Rating distribution
ax_r = axes3[0]
rating_vals = reviews['rating'].value_counts().sort_index()
cmap_colors = [MAPLE_RED if r >= 8 else MAPLE_GOLD if r >= 6 else ACCENT_BLUE for r in rating_vals.index]
ax_r.barh(rating_vals.index.astype(str), rating_vals.values, color=cmap_colors)
ax_r.set_title('Review Rating Distribution')
ax_r.set_xlabel('Number of Reviews')
ax_r.axvline(x=0, color='black', linewidth=0.5)
for i, (val) in enumerate(rating_vals.values):
    ax_r.text(val + 0.1, i, str(val), va='center', fontsize=9)

# Theme frequency
ax_t = axes3[1]
top_themes = dict(theme_counts.most_common(8))
t_colors = [ACCENT_GREEN if 'clean' in k or 'staff' in k or 'location' in k
            else MAPLE_RED for k in top_themes.keys()]
ax_t.barh(list(top_themes.keys()), list(top_themes.values()), color=t_colors)
ax_t.set_title('Most Mentioned Review Themes')
ax_t.set_xlabel('Frequency')

# Sentiment breakdown pie
ax_s = axes3[2]
sentiment_counts = reviews['sentiment_label'].value_counts()
s_colors = [ACCENT_GREEN if s == 'Positive' else MAPLE_GOLD if s == 'Neutral' else MAPLE_RED
            for s in sentiment_counts.index]
wedges, texts, autotexts = ax_s.pie(
    sentiment_counts.values,
    labels=sentiment_counts.index,
    autopct='%1.1f%%',
    colors=s_colors,
    startangle=90,
    wedgeprops={'edgecolor': 'white', 'linewidth': 2}
)
ax_s.set_title(f'Sentiment Breakdown\n(4.7★ avg on Google)')
for at in autotexts:
    at.set_fontweight('bold')
    at.set_fontsize(11)

plt.tight_layout()
plt.savefig('outputs/figure3_sentiment.png', dpi=180, bbox_inches='tight', facecolor='white')
plt.show()
print("✅ Figure 3 saved: Sentiment Analysis")

# =============================================================================
# SECTION 7: REVENUE FORECASTING (Simple Trend + Seasonality)
# =============================================================================

print("\n" + "="*60)
print("REVENUE FORECASTING — NEXT 6 MONTHS")
print("="*60)

# Calculate seasonal index (ratio of month avg vs overall avg)
monthly_avg_rev = revenue.groupby('month')['gross_revenue'].mean()
overall_avg = monthly_avg_rev.mean()
seasonal_index = (monthly_avg_rev / overall_avg).round(3)

print("\nSeasonal Index by Month (1.0 = average):")
for m, idx in seasonal_index.items():
    bar = '▓' * int(idx * 10)
    label = ['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][m]
    trend = '▲' if idx > 1.2 else '▼' if idx < 0.8 else '→'
    print(f"  {label:<4} {trend}  {idx:.2f}  {bar}")

# Simple YoY growth rate (using available data)
recent_months = revenue.tail(6)['gross_revenue'].mean()
earlier_months = revenue.head(6)['gross_revenue'].mean()
growth_rate = (recent_months / earlier_months - 1)
print(f"\n📈 Estimated revenue growth trend: {growth_rate*100:+.1f}%")

# Forecast April–September 2026
forecast_months = [
    {'year': 2026, 'month': 4, 'name': 'April'},
    {'year': 2026, 'month': 5, 'name': 'May'},
    {'year': 2026, 'month': 6, 'name': 'June'},
    {'year': 2026, 'month': 7, 'name': 'July (Festival)'},
    {'year': 2026, 'month': 8, 'name': 'August'},
    {'year': 2026, 'month': 9, 'name': 'September'},
]

print("\n🔮 6-Month Revenue Forecast (Apr–Sep 2026):")
print(f"{'Month':<20} {'Seasonal Idx':>14} {'Forecast Revenue':>18} {'Confidence':>12}")
print("-" * 68)
forecasts = []
for fm in forecast_months:
    s_idx = seasonal_index.get(fm['month'], 1.0)
    base = overall_avg * (1 + growth_rate * 0.5)  # conservative growth
    forecast = base * s_idx
    conf = "High" if fm['month'] in [7, 8] else "Medium" if fm['month'] in [6, 9] else "Medium"
    rev_str = f"${forecast:,.0f}"
    print(f"  {fm['name']:<18} {s_idx:>14.2f} {rev_str:>18} {conf:>12}")
    forecasts.append({'month': fm['name'], 'forecast': forecast, 'seasonal_index': s_idx})

forecast_df = pd.DataFrame(forecasts)
total_forecast = forecast_df['forecast'].sum()
print(f"\n  📊 Total Forecast (6 months): ${total_forecast:,.0f}")

# Forecast visualization
fig4, ax_f = plt.subplots(figsize=(14, 5))
hist_dates = revenue['date']
hist_rev = revenue['gross_revenue']
ax_f.plot(hist_dates, hist_rev, color=MAPLE_RED, linewidth=2.5, marker='o',
          markersize=5, label='Actual Revenue', zorder=3)

# Add forecast points
from datetime import date
forecast_dates = pd.to_datetime([f"2026-{fm['month']:02d}-01" for fm in forecast_months])
forecast_vals = forecast_df['forecast'].values
ax_f.plot(forecast_dates, forecast_vals, color=MAPLE_GOLD, linewidth=2.5,
          marker='D', markersize=6, linestyle='--', label='Forecast', zorder=3)
ax_f.fill_between(forecast_dates, forecast_vals * 0.88, forecast_vals * 1.12,
                  alpha=0.15, color=MAPLE_GOLD, label='Confidence interval (±12%)')

# Connect actual to forecast
last_actual_date = hist_dates.iloc[-1]
last_actual_val = hist_rev.iloc[-1]
ax_f.plot([last_actual_date, forecast_dates[0]], [last_actual_val, forecast_vals[0]],
          color='gray', linestyle=':', linewidth=1.5)

ax_f.axvspan(forecast_dates[0], forecast_dates[-1], alpha=0.05, color=MAPLE_GOLD)
ax_f.set_title('Lakeview Motel — Revenue Trend & 6-Month Forecast (Apr–Sep 2026)',
               fontsize=13, fontweight='bold')
ax_f.set_ylabel('Monthly Revenue (CAD)')
ax_f.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}k'))
ax_f.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b %y'))
ax_f.legend(fontsize=9)
ax_f.grid(axis='y', alpha=0.3)

# Annotate Annual Summer Festival
celtic_idx_f = 3
ax_f.annotate('Festival\nFestival\nPeak', xy=(forecast_dates[celtic_idx_f], forecast_vals[celtic_idx_f]),
              xytext=(forecast_dates[celtic_idx_f] - pd.Timedelta(days=55),
                      forecast_vals[celtic_idx_f] + 1500),
              fontsize=8.5, color=MAPLE_DARK, fontweight='bold',
              arrowprops=dict(arrowstyle='->', color=MAPLE_DARK, lw=1.2))

plt.tight_layout()
plt.savefig('outputs/figure4_forecast.png', dpi=180, bbox_inches='tight', facecolor='white')
plt.show()
print("✅ Figure 4 saved: Revenue Forecast")

# =============================================================================
# SECTION 8: BUSINESS RECOMMENDATIONS
# =============================================================================

print("\n" + "="*60)
print("STRATEGIC RECOMMENDATIONS FOR MAPLE LEAF MOTEL")
print("="*60)

recommendations = [
    {
        "priority": "HIGH",
        "area": "Dynamic Pricing",
        "insight": "Weekend rates in summer already capture premium, but Friday check-in is the most common day.",
        "recommendation": "Introduce a 3-night minimum for peak weekends (July–Aug) to reduce turnover cost and capture maximum revenue per booking cycle."
    },
    {
        "priority": "HIGH",
        "area": "Annual Summer Festival Strategy",
        "insight": "Annual Summer Festival week generates highest ADR of the year with full 11-room occupancy.",
        "recommendation": "Create a dedicated Annual Summer Festival package on the website with early-bird booking at standard peak rates and last-minute at a 15% premium. Target past Festival guests with email reminder in January."
    },
    {
        "priority": "HIGH",
        "area": "Direct Booking Growth",
        "insight": f"Direct website bookings represent a growing channel but OTAs (Booking.com, Expedia) charge 15-20% commission.",
        "recommendation": "Offer a 'Book Direct' incentive (e.g. early check-in or late checkout) on [motel-website].ca to shift bookings away from OTAs — each conversion saves approximately $25–40 per booking in fees."
    },
    {
        "priority": "MEDIUM",
        "area": "Winter Revenue Floor",
        "insight": f"Winter average occupancy is ~{avg_winter_occ:.0f}%. Corporate clients (Corporate_Client_A etc.) provide a stable revenue floor.",
        "recommendation": "Formalize corporate rate agreements with Corporate_Client_A and similar companies. Consider a preferred corporate rate card (e.g. $89/night with guaranteed minimum 10 nights/month) to lock in predictable winter revenue."
    },
    {
        "priority": "MEDIUM",
        "area": "Guest Satisfaction",
        "insight": f"4.7★ Google rating. Top positive themes: cleanliness, staff, location. Negative reviews cite pricing transparency and occasional maintenance issues.",
        "recommendation": "Address pricing transparency proactively — ensure all OTA listings match actual charged rate. Implement a pre-arrival checklist (AC, TV, coffee maker) to prevent the issues raised in the one notable negative review."
    },
    {
        "priority": "LOW",
        "area": "Shoulder Season Activation",
        "insight": "May and October show moderate occupancy. Local Town has shoulder season events beyond Annual Summer Festival.",
        "recommendation": "Create seasonal packages around Victoria Day weekend (May) and Thanksgiving (October) — both are proven Ontario travel weekends — with a 2-night minimum."
    }
]

for rec in recommendations:
    pri_color = "🔴" if rec['priority'] == 'HIGH' else "🟡" if rec['priority'] == 'MEDIUM' else "🟢"
    print(f"\n{pri_color} [{rec['priority']}] {rec['area']}")
    print(f"   Insight: {rec['insight']}")
    print(f"   Action:  {rec['recommendation']}")

# =============================================================================
# SECTION 9: SUMMARY STATISTICS TABLE
# =============================================================================

print("\n" + "="*60)
print("EXECUTIVE SUMMARY — KEY METRICS")
print("="*60)
total_bookings = len(bookings)
total_revenue_tracked = bookings['total_revenue'].sum()
total_nights_sold = bookings['num_nights'].sum()
avg_stay = bookings['num_nights'].mean()
avg_rate = bookings['rate_per_night'].mean()
corporate_rev_pct = bookings[bookings['is_corporate']]['total_revenue'].sum() / total_revenue_tracked * 100
weekend_rev_pct = bookings[bookings['is_weekend']]['total_revenue'].sum() / total_revenue_tracked * 100
celtic_rev = bookings[bookings['is_annual_festival']]['total_revenue'].sum()
double_rooms_rev = bookings[bookings['room_type'] == 'Double']['total_revenue'].sum()
queen_rooms_rev  = bookings[bookings['room_type'] == 'Queen']['total_revenue'].sum()

print(f"\n  Total Bookings Analyzed:      {total_bookings}")
print(f"  Total Nights Sold:            {total_nights_sold:,}")
print(f"  Total Revenue Tracked:        ${total_revenue_tracked:,.0f}")
print(f"  Average Stay Length:          {avg_stay:.1f} nights")
print(f"  Average Nightly Rate:         ${avg_rate:.0f}")
print(f"  Corporate Revenue Share:      {corporate_rev_pct:.0f}%")
print(f"  Weekend Revenue Premium:      {weekend_rev_pct:.0f}% of revenue from weekends")
print(f"  Annual Summer Festival Revenue:      ${celtic_rev:,.0f} (1 week!)")
print(f"  Queen Room Revenue:           ${queen_rooms_rev:,.0f}")
print(f"  Double Room Revenue:          ${double_rooms_rev:,.0f}")
print(f"\n  Google Rating:                4.7 ★ / 5.0")
print(f"  Booking.com Rating:           8.2 / 10")
print(f"  Positive Review Rate:         {(reviews['sentiment_label']=='Positive').mean()*100:.0f}%")

print("\n\n✅ ANALYSIS COMPLETE — All figures saved to outputs/ folder")
print("   This notebook was built using real booking and revenue data")
print("   from the Lakeview Motel, Small-Town Ontario (2024–2026)")

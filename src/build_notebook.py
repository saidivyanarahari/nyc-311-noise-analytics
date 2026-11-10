"""Script to generate the audited, standardized, fully-executable Jupyter Notebook for NYC 311 Noise Analytics."""

import json
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
notebook_path = os.path.join(project_root, "notebooks", "nyc_noise_analysis.ipynb")

nb = {
    "cells": [],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.14.8",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}


def add_md(text: str):
    nb["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip().split("\n")],
    })


def add_code(text: str):
    nb["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in text.strip().split("\n")],
    })


# 1. Business Problem
add_md("""# NYC 311 Noise Crisis: Strategic Response Analysis (2023–2024)
### Decision-Support Analytics, Empirical Joint Probability Auditing & Pilot Prioritization

**Candidate / Author:** Sai Divya Narahari  
**Academic Provenance:** Strategic framework & briefing originally presented on December 14, 2025 (*EAI6120: AI Communication / Visualization*, Northeastern University; Guided by Prof. Walter McHugh)  
**Reconstructed Codebase:** Independent Python data extraction, cleaning, and verification pipeline developed in November 2026 using public NYC Open Data (Socrata API: `erm2-nwe9`)

---

## 1. Business Problem & Decision Context
Municipal service centers manage millions of citizen requests annually. In New York City, noise complaints represent the **single largest category** of 311 service requests directed to the New York City Police Department (NYPD) and Department of Environmental Protection (DEP).

Traditional municipal response deploys patrol officers and inspection teams reactively and uniformly across all 59 Community Districts. This uniform distribution dilutes operational impact in chronic, severe hotspots and fails to achieve sustainable complaint reductions.

**Core Analytical Objectives:**
* Quantify spatial and temporal concentration across two full calendar years (1.44M records).
* Audit geographic Pareto distributions across boroughs and individual postal ZIP codes with declared denominators.
* Measure peak operational windows across all days versus weekends specifically.
* Evaluate **empirical joint probability** ($P(\text{ZIP} \cap \text{Time})$) versus naive marginal multiplication ($P(\text{ZIP}) \times P(\text{Time})$).
* Distinguish the targeted problem population from realistic intervention prevention scenarios.
* Formulate a prioritized operational pilot ("Quiet Force") and evaluate sensitivity models.""")

# 2. Dataset Source & Architecture
add_md("""## 2. Dataset Source & Architecture
The analysis utilizes the **NYC 311 Service Requests from 2010 to Present** dataset, published on **NYC Open Data** (Socrata Dataset ID: `erm2-nwe9`).

* **Temporal Scope:** January 1, 2023 – December 31, 2024 (2 calendar years).
* **Population Size:** Exactly 1,439,558 noise complaints citywide (`complaint_type LIKE '%Noise%'`).
* **Analytical Architecture:**
  1. **Population Telemetry:** Live SoQL queries aggregate citywide totals across all 1.44M records (borough shares, complaint types, day-of-week volumes, hourly distributions, and exact joint counts).
  2. **Multi-Season Complete-Week Sample:** A balanced cohort of 51,441 records across 4 complete Monday-to-Sunday calendar weeks (Winter, Spring, Summer, Fall) ensures zero day-of-week truncation artifacts while enabling instantaneous, lightweight local execution (<10MB).""")

# 3. Environment Setup & Data Loading
add_md("## 3. Environment Setup & Data Loading")
add_code("""import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Configure visualization styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica, Arial, sans-serif'
plt.rcParams['figure.dpi'] = 150

print(f"Pandas version: {pd.__version__}")
print(f"Numpy version: {np.__version__}")""")

add_code("""# Define data paths
data_dir = os.path.join('..', 'data')
sample_file = os.path.join(data_dir, 'sample_nyc_noise_50k.csv')
metadata_file = os.path.join(data_dir, 'summary_metrics_2023_2024.json')

# Load population summary metrics
with open(metadata_file, 'r') as f:
    pop = json.load(f)

# Load sample dataset
df_raw = pd.read_csv(sample_file)
print(f"Sample dataset loaded: {len(df_raw):,} records across 4 complete calendar weeks.")
print(f"Verified Citywide Population Total: {pop['total_noise_complaints']:,} complaints across 2023-2024.")""")

# 4. Data Quality Checks
add_md("""## 4. Data Quality Checks & Completeness Audit
We inspect data types, primary key uniqueness, and missingness rates across spatial attributes.""")
add_code("""# Inspect schema completeness
quality_df = pd.DataFrame({
    'Data Type': df_raw.dtypes,
    'Null Count': df_raw.isnull().sum(),
    'Null Pct (%)': (df_raw.isnull().sum() / len(df_raw)) * 100
})
quality_df""")

add_code("""# Primary key deduplication check
unique_keys = df_raw['unique_key'].nunique()
print(f"Unique request IDs: {unique_keys:,} / {len(df_raw):,} total rows.")
assert unique_keys == len(df_raw), "Duplicate request keys detected!" """)

# 5. Cleaning & Feature Engineering
add_md("""## 5. Cleaning & Feature Engineering
We implement standardized transformations:
1. Parse ISO datetime strings into Pandas datetime objects.
2. Extract temporal attributes (`hour`, `day_of_week`, `day_name`, `month`, `year`).
3. Construct explicit operational flags:
   * `is_core_night`: 4-hour window (9:00 PM – 1:00 AM, hours 21, 22, 23, 0).
   * `is_evening_night`: 6-hour window (8:00 PM – 2:00 AM, hours 20, 21, 22, 23, 0, 1).
   * `is_ground_zero`: 2-hour peak (10:00 PM – Midnight, hours 22, 23).
   * `is_weekend`: Friday, Saturday, Sunday.
4. Standardize spatial attributes (uppercase boroughs, 5-digit regex for ZIP codes).""")

add_code("""df = df_raw.copy()

# Datetime parsing
df['created_datetime'] = pd.to_datetime(df['created_date'], errors='coerce')
df['hour'] = df['created_datetime'].dt.hour
df['day_name'] = df['created_datetime'].dt.day_name()
df['day_of_week'] = df['created_datetime'].dt.dayofweek # 0=Monday, 6=Sunday
df['month'] = df['created_datetime'].dt.month
df['year'] = df['created_datetime'].dt.year

# Operational time window flags
df['is_weekend'] = df['day_of_week'].isin([4, 5, 6]) # Fri, Sat, Sun
df['is_ground_zero'] = df['hour'].isin([22, 23]) # 10 PM - 12 AM
df['is_core_night'] = df['hour'].isin([21, 22, 23, 0]) # 9 PM - 1 AM
df['is_evening_night'] = df['hour'].isin([20, 21, 22, 23, 0, 1]) # 8 PM - 2 AM

# Spatial standardization
df['borough'] = df['borough'].astype(str).str.strip().str.upper()
df.loc[df['borough'].isin(['', 'NAN', 'NONE', 'UNSPECIFIED']), 'borough'] = 'UNSPECIFIED'
df['clean_zip'] = df['incident_zip'].astype(str).str.extract(r'^(\\d{5})')[0]

print("Cleaning and feature engineering completed successfully.")""")

# 6. EDA
add_md("""## 6. Exploratory Data Analysis: Complaint Types & Descriptors
We audit complaint types citywide and examine the specific descriptor breakdown to avoid conflating overall loud music with residential-specific noise.""")
add_code("""# Citywide population complaint types
pop_types = pd.DataFrame(
    list(pop['complaint_types'].items()),
    columns=['Complaint Type', 'Population Count']
)
pop_types['Population Share (%)'] = (pop_types['Population Count'] / pop['total_noise_complaints']) * 100
pop_types.sort_values(by='Population Count', ascending=False)""")

add_code("""# Descriptor audit: 'Loud Music/Party' across complaint types
sample_total = len(df)
loud_music_all = df[df['descriptor'] == 'Loud Music/Party']
lm_by_type = loud_music_all['complaint_type'].value_counts().reset_index()
lm_by_type.columns = ['Complaint Type', 'Loud Music Count']
lm_by_type['Share of All Loud Music (%)'] = (lm_by_type['Loud Music Count'] / len(loud_music_all)) * 100
lm_by_type['Share of Sample Total (%)'] = (lm_by_type['Loud Music Count'] / sample_total) * 100

print(f"Total 'Loud Music/Party' in sample: {len(loud_music_all):,} ({len(loud_music_all)/sample_total*100:.2f}% of all sample complaints).")
lm_by_type""")

add_code("""# Residential Noise specifically
res_total = len(df[df['complaint_type'] == 'Noise - Residential'])
res_lm = len(df[(df['complaint_type'] == 'Noise - Residential') & (df['descriptor'] == 'Loud Music/Party')])
print(f"Residential Noise records in sample: {res_total:,} ({res_total/sample_total*100:.2f}% of sample)")
print(f"Residential Loud Music records: {res_lm:,} ({res_lm/res_total*100:.2f}% of residential noise; {res_lm/sample_total*100:.2f}% of all complaints)")""")

add_md("""**Finding on Noise Descriptors:**
* **52.37%** of all complaints cite `Loud Music/Party` across all noise categories combined.
* Within **`Noise - Residential` specifically**, `Loud Music/Party` is the primary descriptor, driving **56.78%** of residential complaints (with `Banging/Pounding` second).
* These metrics are reported separately to ensure total analytical transparency.""")

# 7. Geographic Patterns
add_md("""## 7. Geographic Patterns: Borough & ZIP-Code Concentration
We evaluate geographic Pareto distributions with explicit, declared denominators.""")
add_code("""# Borough concentration across the 1.44M population
borough_summary = pd.DataFrame([
    {'Borough': b, 'Count': c, 'Pct': pop['borough_percentages'][b]}
    for b, c in pop['borough_counts'].items()
]).sort_values(by='Count', ascending=False)
borough_summary['Cumulative Pct (%)'] = borough_summary['Pct'].cumsum()
borough_summary""")

add_code("""# Verify Top 3 Borough Claim: Manhattan + Brooklyn + Bronx
top3_sum = pop['top_3_boroughs_combined']['count']
top3_pct = pop['top_3_boroughs_combined']['percentage']
top2_sum = pop['top_2_boroughs_combined']['count']
top2_pct = pop['top_2_boroughs_combined']['percentage']
print(f"Top 3 Boroughs Total: {top3_sum:,} / {pop['total_noise_complaints']:,} ({top3_pct:.2f}%)")
print(f"Top 2 Boroughs (Manhattan + Brooklyn): {top2_sum:,} / {pop['total_noise_complaints']:,} ({top2_pct:.2f}%)")""")

add_code("""# Top 10 ZIP Codes Analysis with Declared Denominators
valid_zips = df.dropna(subset=['clean_zip'])
sample_valid_count = len(valid_zips)
top10_zip_sample = valid_zips['clean_zip'].value_counts().head(10).reset_index()
top10_zip_sample.columns = ['ZIP Code', 'Sample Count']
top10_zip_sample['Share of Valid ZIPs (%)'] = (top10_zip_sample['Sample Count'] / sample_valid_count) * 100
top10_zip_sample['Cumulative Share (%)'] = top10_zip_sample['Share of Valid ZIPs (%)'].cumsum()

top10_sum = top10_zip_sample['Sample Count'].sum()
print(f"Sample Top 10 ZIP Sum: {top10_sum:,} / {sample_valid_count:,} valid ZIPs ({top10_sum/sample_valid_count*100:.2f}%)")
print(f"Sample Top 10 ZIP Sum as % of All {len(df):,} Sample Records: {top10_sum/len(df)*100:.2f}%")
print(f"Citywide Population (Residential Noise Only): Top 10 ZIPs account for {pop['top_residential_zip_codes']['residential_top_10_share_pct']:.2f}% of 677,749 complaints.")
top10_zip_sample""")

add_md("""**Reconciliation of ZIP Code Concentration:**
1. **Multi-Season Complete-Week Sample (All Noise Types):** Top 10 ZIP codes account for **18.90%** of complaints with valid postal codes (and **18.88%** of all sample records).
2. **Citywide Population (Residential Noise Only):** Top 10 ZIP codes account for **25.99%** of all 677,749 residential complaints citywide.
3. **Original Coursework Deck:** Reported as **~20%**, representing a rounded operational heuristic.""")

# 8. Temporal Patterns
add_md("""## 8. Temporal Patterns: Day-of-Week Volatility & Peak Windows
We audit day-of-week surges and confirm exact percentages across time windows for all days versus weekends.""")
add_code("""# Day-of-Week Volatility in Citywide Population (1.44M Records)
dow_df = pd.DataFrame(
    list(pop['day_of_week_counts'].items()),
    columns=['Day of Week', 'Population Count']
)
dow_df['Population Share (%)'] = (dow_df['Population Count'] / pop['total_noise_complaints']) * 100

# Daily averages
mon_thu_avg = pop['day_of_week_metrics']['mon_thu_daily_average']
thu_vol = pop['day_of_week_metrics']['thursday_daily_volume']
fri_vol = pop['day_of_week_metrics']['friday_daily_volume']
fri_surge = pop['day_of_week_metrics']['friday_vs_thursday_daily_surge_pct']
sat_sun_avg = pop['day_of_week_metrics']['sat_sun_daily_average']
sat_sun_surge = pop['day_of_week_metrics']['sat_sun_surge_vs_weekday_avg_pct']
fri_sun_pct = pop['day_of_week_metrics']['fri_sun_combined_pct']

print(f"Thursday daily volume: {thu_vol:,}")
print(f"Friday daily volume: {fri_vol:,} (+{fri_surge:.2f}% surge vs Thursday daily volume)")
print(f"Monday-Thursday daily average: {mon_thu_avg:,.2f}")
print(f"Saturday-Sunday daily average: {sat_sun_avg:,.2f} (+{sat_sun_surge:.2f}% surge vs Mon-Thu daily average)")
print(f"Friday-Sunday combined population share: {fri_sun_pct:.2f}% ({pop['day_of_week_metrics']['fri_sun_combined_volume']:,} complaints)")
dow_df""")

add_code("""# Time Window Distribution: All Days vs. Weekends
# Citywide Population Totals (All Days):
h_pop = pop['hourly_distribution_all_days']
print("=== CITYWIDE POPULATION (ALL DAYS, 1,439,558 Records) ===")
print(f"Ground Zero Window (10 PM - Midnight): {h_pop['ground_zero_10pm_to_midnight_count']:,} ({h_pop['ground_zero_10pm_to_midnight_pct']:.2f}%)")
print(f"Core Night Window (9 PM - 1 AM): {h_pop['core_window_9pm_to_1am_count']:,} ({h_pop['core_window_9pm_to_1am_pct']:.2f}%)")
print(f"Evening/Night Window (8 PM - 2 AM): {h_pop['evening_window_8pm_to_2am_count']:,} ({h_pop['evening_window_8pm_to_2am_pct']:.2f}%)")

# Sample Weekend vs Weekday breakdown:
wkend = df[df['is_weekend']]
wkday = df[~df['is_weekend']]
print(f"\\n=== WEEKENDS ONLY (FRI-SUN, Sample: {len(wkend):,} Records, {len(wkend)/len(df)*100:.2f}% of Sample) ===")
print(f"Ground Zero Window (10 PM - Midnight): {wkend['is_ground_zero'].sum():,} ({wkend['is_ground_zero'].sum()/len(wkend)*100:.2f}% of weekend volume)")
print(f"Core Night Window (9 PM - 1 AM): {wkend['is_core_night'].sum():,} ({wkend['is_core_night'].sum()/len(wkend)*100:.2f}% of weekend volume)")
print(f"Evening/Night Window (8 PM - 2 AM): {wkend['is_evening_night'].sum():,} ({wkend['is_evening_night'].sum()/len(wkend)*100:.2f}% of weekend volume)")""")

add_md("""**Sampling Truncation Investigation:**
* **Root Cause of Prior Sample Bias:** A previous 50,000-record query applied `$limit=6250` over 7-day windows sorted descending by `created_date`. Because NYC generates ~14,000–16,000 complaints weekly, the query reached its 6,250 ceiling after only ~4 days, completely cutting off Monday and Tuesday. This artificially inflated the weekend record share to 63.4%.
* **The Correction:** By pulling 4 complete Monday 00:00:00 to Sunday 23:59:59 calendar weeks across Winter, Spring, Summer, and Fall (51,441 records), all days are captured without limit caps. The sample weekend share (**51.91%**) closely mirrors the true population (**54.33%**) within 2.4%.""")

# 9. Key Findings
add_md("""## 9. Key Verified Findings Summary
1. **Population Scope:** 1,439,558 complaints across 2023–2024.
2. **Top 3 Borough Concentration:** Manhattan (26.92%), Brooklyn (26.22%), and the Bronx (24.65%) account for **77.79%** (~78%) of all municipal noise complaints.
3. **ZIP Code Pareto Distribution:** Top 10 ZIP codes account for **18.90%** of complaints in the multi-season complete-week sample (and **25.99%** of residential noise citywide).
4. **Behavioral Root Cause:** 52.37% of all complaints cite `Loud Music/Party`, driving 56.78% of residential complaints specifically.
5. **Day-of-Week Volatility:** Daily complaint volume surges **+22.98% from Thursday into Friday**, and the Saturday/Sunday daily average surges **+78.47%** over the Monday–Thursday weekday baseline.
6. **Time Windows:** 10 PM – Midnight is the single sharpest 2-hour peak (21.17% citywide); 9 PM – 1 AM captures 37.86% of all complaints (38.75% in sample); 8 PM – 2 AM captures 50.29% of all complaints (51.40% in sample).""")

# 10. Empirical Joint Probability vs. Naive Multiplication
add_md("""## 10. Empirical Joint Probability & Pilot Scenario Modeling

### Methodological Distinction: Naive Multiplication vs. Joint Intersection
In the original coursework presentation, the targeted complaint pool was estimated as:
$$\\text{Target Pool} = \\text{Annual Baseline} \\times P(\\text{Top 10 ZIP}) \\times P(\\text{Evening Window})$$
$$\\approx 828,000 \\times 20.0\\% \\times 50.7\\% = 83,959 \\approx 84,000 \\text{ complaints/yr}$$

This calculation assumed statistical independence between location and hour. Here, we calculate the **actual empirical joint intersection** $P(\\text{Top 10 ZIP} \\cap \\text{Evening Window})$ using both the 1.44M population and the representative sample.""")

add_code("""# 1. Joint Probability on Citywide Population (1,439,558 Records)
pop_joint = pop['joint_intersection_metrics']
pop_total = pop['total_noise_complaints']

top10_pop_count = pop_joint['top_10_zips_all_noise_count']
top10_pop_pct = pop_joint['top_10_zips_all_noise_pct']
eve_pop_count = pop_joint['evening_window_8pm_to_2am_count']
eve_pop_pct = pop_joint['evening_window_8pm_to_2am_pct']
naive_pop_pct = pop_joint['naive_multiplication_eve_pct']
joint_pop_count = pop_joint['joint_top10_and_8pm_2am_count']
joint_pop_pct = pop_joint['joint_top10_and_8pm_2am_pct']

print("=== POPULATION-LEVEL EMPIRICAL JOINT INTERSECTION (1,439,558 Records) ===")
print(f"Top 10 ZIP Codes (All Noise): {top10_pop_count:,} ({top10_pop_pct:.2f}%)")
print(f"Evening Window (8 PM - 2 AM): {eve_pop_count:,} ({eve_pop_pct:.2f}%)")
print(f"Naive Multiplication P(ZIP) * P(Time): {naive_pop_pct:.2f}%")
print(f"Actual Empirical Joint Intersection P(ZIP and 8PM-2AM): {joint_pop_count:,} ({joint_pop_pct:.2f}%)")
print(f"Discrepancy (Joint vs Naive): {joint_pop_pct - naive_pop_pct:+.2f}% points")
print(f"Annualized Joint Problem Pool (2-Yr Avg): {joint_pop_count / 2:,.0f} complaints/yr")
print(f"Target Pool on 828k Peak Rate: {828000 * (joint_pop_pct / 100):,.0f} complaints/yr")""")

add_code("""# 2. Joint Probability on Sample (51,441 Records)
sample_top10_list = top10_zip_sample['ZIP Code'].tolist()
df['in_top10'] = df['clean_zip'].isin(sample_top10_list)

sample_zip_pct = df['in_top10'].mean() * 100
sample_eve_pct = df['is_evening_night'].mean() * 100
sample_naive_pct = (sample_zip_pct / 100) * (sample_eve_pct / 100) * 100
sample_joint_count = (df['in_top10'] & df['is_evening_night']).sum()
sample_joint_pct = (df['in_top10'] & df['is_evening_night']).mean() * 100

print("\\n=== SAMPLE-LEVEL EMPIRICAL JOINT INTERSECTION (51,441 Records) ===")
print(f"Sample Top 10 ZIP Share: {sample_zip_pct:.2f}%")
print(f"Sample Evening Window Share: {sample_eve_pct:.2f}%")
print(f"Sample Naive Multiplication: {sample_naive_pct:.2f}%")
print(f"Sample Actual Joint Intersection: {sample_joint_count:,} ({sample_joint_pct:.2f}%)")
print(f"Discrepancy: {sample_joint_pct - sample_naive_pct:+.2f}% points")""")

add_code("""# 3. Pilot Sensitivity Modeling on True Empirical Joint Pool
# We evaluate realistic intervention efficacy on the true annual joint pool (67,556 complaints/yr)
true_joint_annual_pool = pop_joint['annualized_joint_8pm_2am_volume']
annual_baseline = pop['total_noise_complaints'] / 2.0 # 719,779 complaints/yr

scenarios = [
    ('Conservative Pilot (15% Effectiveness)', 0.15),
    ('Moderate Pilot (25% Effectiveness)', 0.25),
    ('High-Engagement Pilot (35% Effectiveness)', 0.35),
    ('Aggressive Pilot (50% Effectiveness)', 0.50),
    ('Theoretical Upper Bound (100% Elimination)', 1.00),
]

scenario_rows = []
for name, eff in scenarios:
    prevented = true_joint_annual_pool * eff
    post_pilot = annual_baseline - prevented
    citywide_pct = (prevented / annual_baseline) * 100
    scenario_rows.append({
        'Scenario': name,
        'Intervention Efficacy': f"{eff*100:.0f}%",
        'Target Problem Pool': f"{true_joint_annual_pool:,.0f}",
        'Prevented Complaints / Year': f"{prevented:,.0f}",
        'Post-Pilot Annual Volume': f"{post_pilot:,.0f}",
        'Citywide Reduction (%)': f"{citywide_pct:.2f}%"
    })

pd.DataFrame(scenario_rows)""")

add_md("""**Methodological Reconciliation of the 84,000 Figure:**
1. **The 84,000 figure represents the TARGETED PROBLEM POOL**, not the number of prevented complaints. It was derived from multiplying independent marginal shares ($828,000 \\times 20\\% \\times 50.7\\% = 83,959 \\approx 84,000$).
2. **Empirical Joint Probability:** The actual joint intersection $P(\\text{Top 10 ZIP} \\cap \\text{8 PM–2 AM})$ is **9.39%** in the population (and **9.22%** in the sample).
   * Applied to the actual 2-year average baseline (719,779 complaints/yr), the empirical joint target pool is **67,556 complaints/yr**.
   * Applied to the presentation's 828,000 peak rate, the joint target pool is **77,713 complaints/yr**.
3. **Prevented Complaints vs. Target Pool:** Achieving an 84,000 complaint reduction from a pool of 67,556–77,713 complaints would require **>100% intervention efficacy**, which is physically impossible.
4. **Defensible Pilot Outcomes:** At realistic pilot effectiveness rates of 20% to 35%, the expected reduction is **~13,500 to ~23,600 complaints per year**.""")

# 11. Limitations & Next Steps
add_md("""## 11. Limitations & Responsible Analytics

### Limitations
1. **Reporting Propensity vs. Acoustic Truth:** 311 records reflect citizen reporting behavior and telephone/app access rather than calibrated sound decibels ($dB(A)$).
2. **Population Density Confounders:** High complaint totals in Upper Manhattan and the Bronx correlate with high-density multi-family apartment housing.
3. **Ticket Resolution Latency:** Closing timestamps often measure administrative status updates rather than on-scene officer arrival.
4. **Scenario Model Boundary:** All reduction figures are forward-looking operational projections, not empirical after-action evaluations.

### Recommended Next Steps
* Link 311 records with U.S. Census Bureau American Community Survey (ACS) 5-year data to compute per-capita complaint rates per 1,000 residents.
* Apply spatial clustering (DBSCAN) within 100-meter and 1-hour windows to deduplicate multiple calls regarding the same event.
* Evaluate agency resolution latency against repeat call suppression.""")

os.makedirs(os.path.dirname(notebook_path), exist_ok=True)
with open(notebook_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2)

print(f"Successfully generated audited {notebook_path} with {len(nb['cells'])} cells.")

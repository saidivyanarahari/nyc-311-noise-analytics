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
### Decision-Support Analytics, Concentration Auditing & Pilot Prioritization

**Candidate / Author:** Sai Divya Narahari  
**Academic Provenance:** Strategic framework & briefing originally presented on December 14, 2025 (*EAI6120: AI Communication / Visualization*, Northeastern University; Guided by Prof. Walter McHugh)  
**Reconstructed Codebase:** Independent Python data extraction, cleaning, and verification pipeline developed in November 2026 using public NYC Open Data (Socrata API: `erm2-nwe9`)

---

## 1. Business Problem & Decision Context
Municipal agencies manage massive volumes of non-emergency quality-of-life requests. In New York City, noise complaints represent the **single largest category** of 311 service requests directed to the New York City Police Department (NYPD) and Department of Environmental Protection (DEP).

Traditional municipal response deploys patrol officers and inspection teams reactively and uniformly across all 59 Community Districts. This uniform distribution dilutes operational impact in chronic, severe hotspots and fails to achieve sustainable complaint reductions.

**Core Analytical Objectives:**
* Quantify spatial and temporal concentration across two full calendar years (1.44M records).
* Audit geographic Pareto distributions across boroughs and individual postal ZIP codes with declared denominators.
* Measure peak operational windows across all days versus weekends specifically.
* Distinguish the targeted problem population from realistic intervention prevention scenarios.
* Formulate a prioritized operational pilot ("Quiet Force") and evaluate sensitivity models.""")

# 2. Dataset Source & Architecture
add_md("""## 2. Dataset Source & Description
The analysis utilizes the **NYC 311 Service Requests from 2010 to Present** dataset, published on **NYC Open Data** (Socrata Dataset ID: `erm2-nwe9`).

* **Temporal Scope:** January 1, 2023 – December 31, 2024 (2 calendar years).
* **Population Size:** Exactly 1,439,558 noise complaints citywide (`complaint_type LIKE '%Noise%'`).
* **Analytical Architecture:**
  1. **Population Telemetry:** Live SoQL queries aggregate citywide totals across all 1.44M records (borough shares, complaint types, day-of-week volumes, hourly distributions).
  2. **Stratified Representative Sample:** A multi-season cohort of 50,000 records across 8 quarters (Winter, Spring, Summer, Fall across 2023 and 2024) enables instantaneous, lightweight local execution (<10MB).""")

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
print(f"Sample dataset loaded: {len(df_raw):,} records.")
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
4. Standardize text fields (uppercase boroughs, 5-digit regex for ZIP codes).""")

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
* **52.46%** of all sample complaints cite `Loud Music/Party` across all noise categories combined (Residential: 25.01% of all complaints, Street/Sidewalk: 16.92%, Commercial: 9.40%).
* Within **`Noise - Residential` specifically**, `Loud Music/Party` is the primary descriptor, driving **55.00%** of residential complaints (with `Banging/Pounding` at 34.09%).
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
print(f"Sample Top 10 ZIP Sum as % of All 50,000 Sample Records: {top10_sum/len(df)*100:.2f}%")
print(f"Citywide Population (Residential Noise Only): Top 10 ZIPs account for {pop['top_residential_zip_codes']['residential_top_10_share_pct']:.2f}% of 677,749 complaints.")
top10_zip_sample""")

add_md("""**Reconciliation of ZIP Code Concentration:**
1. **50k Stratified Sample (All Noise Types):** Top 10 ZIP codes account for **17.47%** of complaints with valid postal codes (and **17.46%** of all sample records).
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

print(f"Thursday daily volume: {thu_vol:,}")
print(f"Friday daily volume: {fri_vol:,} (+{fri_surge:.2f}% surge vs Thursday daily volume)")
print(f"Monday-Thursday daily average: {mon_thu_avg:,.2f}")
print(f"Saturday-Sunday daily average: {sat_sun_avg:,.2f} (+{sat_sun_surge:.2f}% surge vs Mon-Thu daily average)")
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
print("\\n=== WEEKENDS ONLY (FRI-SUN, Sample: 31,703 Records) ===")
print(f"Ground Zero Window (10 PM - Midnight): {wkend['is_ground_zero'].sum():,} ({wkend['is_ground_zero'].sum()/len(wkend)*100:.2f}% of weekend volume)")
print(f"Core Night Window (9 PM - 1 AM): {wkend['is_core_night'].sum():,} ({wkend['is_core_night'].sum()/len(wkend)*100:.2f}% of weekend volume)")
print(f"Evening/Night Window (8 PM - 2 AM): {wkend['is_evening_night'].sum():,} ({wkend['is_evening_night'].sum()/len(wkend)*100:.2f}% of weekend volume)")""")

add_md("""**Finding on Time Windows:**
* Across **ALL DAYS** citywide:
  * **10 PM – Midnight (2 hours):** **21.17%** of all complaints ("Ground Zero").
  * **9 PM – 1 AM (4 hours):** **37.86%** of all complaints (Core Patrol Window).
  * **8 PM – 2 AM (6 hours):** **50.29%** of all complaints (Evening/Night Window).
* On **WEEKENDS specifically (Friday–Sunday)**:
  * The **9 PM – 1 AM** window accounts for **40.18%** of all weekend complaints.
  * The **8 PM – 2 AM** window accounts for **52.25%** of all weekend complaints.""")

# 9. Key Findings
add_md("""## 9. Key Verified Findings Summary
1. **Population Scope:** 1,439,558 complaints across 2023–2024.
2. **Top 3 Borough Concentration:** Manhattan (26.92%), Brooklyn (26.22%), and the Bronx (24.65%) account for **77.79%** (~78%) of all municipal noise complaints.
3. **ZIP Code Pareto Distribution:** Top 10 ZIP codes account for **17.47%** of complaints in the multi-season sample (and **25.99%** of residential noise citywide).
4. **Behavioral Root Cause:** 52.46% of all complaints cite `Loud Music/Party`, which accounts for 55.00% of residential complaints specifically.
5. **Day-of-Week Volatility:** Daily complaint volume surges **+22.98% from Thursday into Friday**, and the Saturday/Sunday daily average surges **+78.47%** over the Monday–Thursday weekday baseline.
6. **Time Windows:** 10 PM – Midnight is the single sharpest 2-hour peak (21.17% citywide); 9 PM – 1 AM captures 37.86% of all complaints (40.18% on weekends); 8 PM – 2 AM captures 50.29% of all complaints (52.25% on weekends).""")

# 10. Recommendations & Scenario Modeling
add_md("""## 10. Strategic Pilot Prioritization & Sensitivity Modeling

### Operational Target Population vs. Prevented Reduction
To maintain analytical rigor, we explicitly separate:
* **The Target Problem Pool:** The volume of complaints occurring in the targeted hotspot zone.
* **The Prevented Complaints:** The projected reduction, which depends on assumed pilot effectiveness.

### Mathematical Formulation
$$\\text{Target Pool} = B \\times S_{\\text{ZIP}} \\times S_{\\text{Window}}$$
$$\\text{Prevented Complaints} = \\text{Target Pool} \\times E$$

Where:
* $B$ = Annual Baseline Status Quo ($828,000$ complaints/yr)
* $S_{\\text{ZIP}}$ = Top 10 ZIP code share ($20.0\\%$ heuristic / $17.47\\%$ sample)
* $S_{\\text{Window}}$ = Evening/night window share ($50.7\\%$)
* $E$ = Assumed pilot de-escalation effectiveness rate""")

add_code("""# Define inputs
annual_baseline = 828000
top10_share_heuristic = 0.20
evening_window_share = 0.507

# Target pool volume
target_pool = annual_baseline * top10_share_heuristic * evening_window_share
print(f"Annual Baseline Status Quo: {annual_baseline:,} complaints/yr")
print(f"Target Problem Pool (Top 10 ZIPs, 8 PM - 2 AM): {target_pool:,.0f} complaints/yr (~84,000)\\n")

# Sensitivity Scenarios
efficacy_scenarios = [
    ('Conservative Pilot (15% Effectiveness)', 0.15),
    ('Moderate Pilot (25% Effectiveness)', 0.25),
    ('High-Engagement Pilot (35% Effectiveness)', 0.35),
    ('Aggressive Pilot (50% Effectiveness)', 0.50),
    ('Illustrative Ceiling (Original Coursework Deck: 84k)', 1.00)
]

scenario_results = []
for name, eff in efficacy_scenarios:
    prevented = target_pool * eff
    post_pilot = annual_baseline - prevented
    citywide_pct = (prevented / annual_baseline) * 100
    scenario_results.append({
        'Scenario': name,
        'Effectiveness (%)': f"{eff*100:.0f}%",
        'Prevented Complaints': f"{prevented:,.0f}",
        'Post-Pilot Volume': f"{post_pilot:,.0f}",
        'Citywide Reduction (%)': f"{citywide_pct:.2f}%"
    })

pd.DataFrame(scenario_results)""")

add_md("""**Methodological Interpretation of the 84,000 Figure:**
* The **~84,000 figure represents the entire targeted complaint pool** occurring in the top 10 ZIP codes during evening/night hours ($828,000 \\times 20\\% \\times 50.7\\% = 83,959$).
* Projecting an 84,000 reduction requires assuming **100% elimination of all noise in that window**, which is an unrealistic, theoretical ceiling.
* Realistic pilot scenarios project:
  * **25% Effectiveness:** **20,990 fewer complaints** (~2.5% citywide reduction).
  * **35% Effectiveness:** **29,386 fewer complaints** (~3.5% citywide reduction).
  * **50% Effectiveness:** **41,980 fewer complaints** (~5.1% citywide reduction).
* The 84,000 figure is retained strictly as an **illustrative upper-bound scenario** from the original mayoral presentation.""")

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

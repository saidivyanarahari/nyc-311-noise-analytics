# Analytical Methodology & Mathematical Framework

This document details the analytical workflow, data extraction architecture, feature engineering definitions, and quantitative modeling frameworks used in the **NYC 311 Noise Analytics** project.

---

## 1. Project Objective & Decision Context

Municipal service centers face resource constraints when addressing quality-of-life complaints. In New York City, noise complaints represent the single largest complaint category handled by the New York City Police Department (NYPD) and Department of Environmental Protection (DEP).

**Core Business Problem:**
* How can civic leadership shift municipal response from reactive, dispersed patrols ("peanut-butter spreading") toward evidence-based, prioritized spatial and temporal resource allocation?

---

## 2. Ingestion & Population Verification Layer

### Data Origin
Data was sourced via the NYC Open Data Socrata Open Data API (`erm2-nwe9` dataset).
* **Extraction Period:** January 1, 2023, 00:00:00 to December 31, 2024, 23:59:59 (two full calendar years).
* **Population Query Filter:**
  ```sql
  SELECT *
  WHERE created_date >= '2023-01-01T00:00:00'
    AND created_date < '2025-01-01T00:00:00'
    AND complaint_type LIKE '%Noise%'
  ```
* **Total Citywide Population:** Exactly **1,439,558 incident records** (~1.44 million).

### Documented API Query Endpoints for Population Metrics
Any population-level metric can be regenerated live from Socrata via `src/data_processing.py --regenerate-population-metrics`:
1. **Borough Counts:**
   `$select=borough, count(*)&$where=created_date >= '2023-01-01T00:00:00' and created_date < '2025-01-01T00:00:00' and complaint_type like '%Noise%'&$group=borough`
2. **Complaint Types:**
   `$select=complaint_type, count(*)&$where=created_date >= '2023-01-01T00:00:00' and created_date < '2025-01-01T00:00:00' and complaint_type like '%Noise%'&$group=complaint_type`
3. **Day-of-Week Volumes:**
   `$select=date_extract_dow(created_date) as dow, count(*)&$group=dow`
4. **Hourly Distribution:**
   `$select=date_extract_hh(created_date) as hour, count(*)&$group=hour`
5. **Top Residential ZIP Codes:**
   `$select=incident_zip, count(*)&$where=complaint_type = 'Noise - Residential' and incident_zip is not null&$group=incident_zip&$order=count desc&$limit=10`

---

## 3. Concentration Metrics & Explicit Denominators

To maintain mathematical integrity, every reported metric declares its exact numerator, denominator, and filtering scope:

### A. Borough Concentration
$$\text{Top 3 Borough Share} = \frac{387,561 \text{ (MHT)} + 377,416 \text{ (BK)} + 354,909 \text{ (BX)}}{1,439,558 \text{ (Total Records)}} \times 100 = \mathbf{77.79\% \approx 78\%}$$
$$\text{Top 2 Borough Share (MHT + BK)} = \frac{387,561 + 377,416}{1,439,558} \times 100 = \mathbf{53.14\% \approx 53\%}$$

### B. ZIP-Code Concentration
1. **50k Stratified Sample (All Noise Types):**
   * **Numerator:** Top 10 ZIP complaint count $= 8,730$.
   * **Denominator:** All records with a valid 5-digit postal code $= 49,970$ (30 records were null/unparseable).
   * **Result:** $\frac{8,730}{49,970} \times 100 = \mathbf{17.47\%}$ (or $17.46\%$ of all 50,000 sample records).
2. **Citywide Population (Residential Noise Only):**
   * **Numerator:** Top 10 residential ZIP complaint count $= 176,147$.
   * **Denominator:** Total citywide `Noise - Residential` complaints $= 677,749$.
   * **Result:** $\frac{176,147}{677,749} \times 100 = \mathbf{25.99\%}$.
3. **Original Coursework Deck Heuristic:** Reported as **~20%**, representing a rounded operational heuristic summarizing the extreme geographic Pareto distribution.

### C. Day-of-Week Surges
Across the 1,439,558 complaint population:
* Monday: 181,441; Tuesday: 162,758; Wednesday: 154,235; Thursday: 158,975; Friday: 195,514; Saturday: 282,440; Sunday: 304,195.
* **Friday-versus-Thursday Daily Volume Surge:**
  $$\text{Friday Surge} = \left(\frac{195,514}{158,975} - 1\right) \times 100 = \mathbf{+22.98\% \approx 23\%}$$
* **Saturday/Sunday Daily Average vs. Monday–Thursday Baseline:**
  $$\text{Mon–Thu Daily Average} = \frac{181,441 + 162,758 + 154,235 + 158,975}{4} = 164,352.25$$
  $$\text{Sat–Sun Daily Average} = \frac{282,440 + 304,195}{2} = 293,317.50$$
  $$\text{Weekend Surge} = \left(\frac{293,317.50}{164,352.25} - 1\right) \times 100 = \mathbf{+78.47\%}$$

### D. Peak Hours & Operational Windows
1. **Core Operational Window (9:00 PM – 1:00 AM, Hours 21, 22, 23, 0):**
   * **All Days (Population):** $\frac{545,058}{1,439,558} = \mathbf{37.86\%}$ (~38%).
   * **Weekends Specifically (Sample):** $\frac{12,739}{31,703} = \mathbf{40.18\%}$ of weekend volume.
2. **Evening/Night Window (8:00 PM – 2:00 AM, Hours 20, 21, 22, 23, 0, 1):**
   * **All Days (Population):** $\frac{724,018}{1,439,558} = \mathbf{50.29\%}$ (~50.3%).
   * **Weekends Specifically (Sample):** $\frac{16,565}{31,703} = \mathbf{52.25\%}$ of weekend volume.
3. **"Ground Zero" Peak (10:00 PM – Midnight, Hours 22, 23):**
   * **All Days (Population):** $\frac{304,740}{1,439,558} = \mathbf{21.17\%}$ in just 2 hours.
   * **Weekends Specifically (Sample):** $\frac{7,785}{31,703} = \mathbf{24.56\%}$ of weekend volume.

### E. Loud Music Descriptor Breakdown
In the 50,000-record sample:
* Total citing `Loud Music/Party` across ALL complaint types: $26,228 = \mathbf{52.46\%}$.
  * Noise - Residential: $12,507$ ($25.01\%$ of sample total; $47.69\%$ of all loud music)
  * Noise - Street/Sidewalk: $8,459$ ($16.92\%$ of sample total; $32.25\%$ of all loud music)
  * Noise - Commercial: $4,700$ ($9.40\%$ of sample total; $17.92\%$ of all loud music)
  * Noise - Park: $485$ ($0.97\%$ of sample total)
  * Noise - House of Worship: $77$ ($0.15\%$ of sample total)
* Within `Noise - Residential` specifically: $\frac{12,507}{22,741} = \mathbf{55.00\%}$ cite `Loud Music/Party`.

---

## 4. Scenario Modeling Architecture ("Quiet Force" Pilot)

### Target Problem Pool vs. Prevented Reduction
To maintain analytical rigor, the model separates:
1. **Target Problem Pool:** The volume of complaints occurring in the targeted hotspot zone.
2. **Prevented Complaints:** The projected reduction, which depends on assumed pilot effectiveness.

### Mathematical Formulation
$$\text{Target Pool} = B \times S_{\text{ZIP}} \times S_{\text{Window}}$$
$$\text{Prevented Complaints} = \text{Target Pool} \times E$$

Where:
* $B$ = Annual Baseline Status Quo ($828,000$ complaints/yr based on 2024 run-rate)
* $S_{\text{ZIP}}$ = Proportion of complaints in Top 10 Target ZIP codes ($20.0\% = 0.20$ heuristic / $17.47\%$ sample)
* $S_{\text{Window}}$ = Proportion of complaints occurring during 8 PM – 2 AM evening window ($50.7\% = 0.507$)
* $E$ = Assumed pilot de-escalation effectiveness rate

### Sensitivity Analysis Table
$$\text{Target Pool} = 828,000 \times 0.20 \times 0.507 = \mathbf{83,959 \approx 84,000 \text{ complaints/yr in hotspots}}$$

| Scenario | Assumed Effectiveness ($E$) | Prevented Complaints/yr | Post-Pilot Annual Volume | Citywide Reduction |
| :--- | :--- | :--- | :--- | :--- |
| **Conservative Pilot** | 15% | **12,594** | 815,406 | 1.52% |
| **Moderate Pilot** | 25% | **20,990** | 807,010 | 2.54% |
| **High-Engagement Pilot**| 35% | **29,386** | 798,614 | 3.55% |
| **Aggressive Pilot** | 50% | **41,980** | 786,020 | 5.07% |
| **Theoretical Ceiling** | 100% | **83,959 (~84,000)** | 744,041 | 10.14% |

> [!IMPORTANT]
> **Methodological Boundary:** The 84,000 figure is an **illustrative upper-bound scenario** representing 100% elimination of the target pool in those 10 ZIPs (or a 50.7% reduction across all hours in those ZIPs). It is **not** an observed historical outcome.

# Analytical Methodology & Mathematical Framework

This document details the analytical workflow, data extraction architecture, feature engineering definitions, sampling audit, and quantitative modeling frameworks used in the **NYC 311 Noise Analytics** project.

---

## 1. Project Objective & Decision Context

Municipal service centers face severe resource constraints when addressing quality-of-life complaints. In New York City, noise complaints represent the single largest complaint category handled by the New York City Police Department (NYPD) and Department of Environmental Protection (DEP).

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
6. **Empirical Joint Intersection (Top 10 ZIPs $\cap$ 8 PM–2 AM):**
   `$select=count(*)&$where=incident_zip in ('10466', '10456', '10468', '11226', '10457', '11221', '10452', '10031', '10467', '11207') and date_extract_hh(created_date) in (20, 21, 22, 23, 0, 1) and complaint_type like '%Noise%'`

---

## 3. Sampling Audit: Root Cause Diagnosis & Complete-Week Resolution

### The Sampling Truncation Anomaly
An earlier 50,000-record sample contained an anomalous 31,703 weekend records (63.41%), compared to the true population weekend share of 54.33%.

**Root Cause Analysis:**
* Socrata queries that partition data into 7-day windows using `$limit=6250` without an explicit sort default to `created_date desc`.
* In New York City, weekly noise volume averages 14,000 to 16,000 complaints.
* Because the query started at Sunday 23:59:59 and pulled descending in time, the 6,250 record quota was filled after only 4.2 to 4.8 days.
* In high-volume summer weeks (e.g., July 2024), 6,250 records accumulated entirely between Friday evening and Saturday night, completely truncating Sunday, Monday, Tuesday, Wednesday, and Thursday.
* Across 8 quarters, this truncation artificially depressed Monday (2,161 records) and Tuesday (3,544 records) while over-indexing Saturday (11,674) and Sunday (10,905).

### The Complete-Week Solution
To eliminate sampling bias, `download_stratified_sample` was updated to pull **4 complete Monday 00:00:00 to Sunday 23:59:59 calendar weeks** across Winter, Spring, Summer, and Fall (January 9–16, April 10–17, July 10–17, October 9–16, 2023) with `$limit=30000`:
* Total sample records: **51,441**.
* Sample Day-of-Week distribution: Saturday (9,527), Sunday (9,097), Friday (8,080), Thursday (7,013), Wednesday (6,540), Monday (5,622), Tuesday (5,562).
* **Sample Weekend Share:** **51.91%** (closely matching the population's **54.33%** within 2.4%).

---

## 4. Concentration Metrics & Explicit Denominators

### A. Borough Concentration
$$\text{Top 3 Borough Share} = \frac{387,561 \text{ (MHT)} + 377,416 \text{ (BK)} + 354,909 \text{ (BX)}}{1,439,558 \text{ (Total Records)}} \times 100 = \mathbf{77.79\% \approx 78\%}$$
$$\text{Top 2 Borough Share (MHT + BK)} = \frac{387,561 + 377,416}{1,439,558} \times 100 = \mathbf{53.14\% \approx 53\%}$$

### B. ZIP-Code Concentration
1. **Multi-Season Complete-Week Sample (All Noise Types):**
   * **Numerator:** Top 10 ZIP complaint count $= 9,724$.
   * **Denominator:** All records with valid postal codes $= 51,425$ (16 unparseable).
   * **Result:** $\frac{9,724}{51,425} \times 100 = \mathbf{18.91\%}$ (or $18.90\%$ of all 51,441 sample records).
2. **Citywide Population (Residential Noise Only):**
   * **Numerator:** Top 10 residential ZIP complaint count $= 176,147$.
   * **Denominator:** Total citywide `Noise - Residential` complaints $= 677,749$.
   * **Result:** $\frac{176,147}{677,749} \times 100 = \mathbf{25.99\%}$.
3. **Citywide Population (All Noise Types):**
   * **Numerator:** Top 10 residential ZIPs complaint count across all noise types $= 276,631$.
   * **Denominator:** Total citywide noise complaints $= 1,439,558$.
   * **Result:** $\frac{276,631}{1,439,558} \times 100 = \mathbf{19.22\%}$.
4. **Original Coursework Deck Heuristic:** Reported as **~20%**, representing an operational heuristic for geographic Pareto clustering.

### C. Day-of-Week Volatility
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
   * **All Days (Population):** $\frac{545,058}{1,439,558} = \mathbf{37.86\%}$ (38.75% in sample).
2. **Evening/Night Window (8:00 PM – 2:00 AM, Hours 20, 21, 22, 23, 0, 1):**
   * **All Days (Population):** $\frac{724,018}{1,439,558} = \mathbf{50.29\%}$ (51.40% in sample).
3. **"Ground Zero" Peak (10:00 PM – Midnight, Hours 22, 23):**
   * **All Days (Population):** $\frac{304,740}{1,439,558} = \mathbf{21.17\%}$ in just 2 hours.

---

## 5. Empirical Joint Probability vs. Naive Marginal Multiplication

### Mathematical Distinction
A common analytical error is assuming independence between location and time:
$$P(\text{ZIP} \cap \text{Window}) \stackrel{?}{=} P(\text{ZIP}) \times P(\text{Window})$$

In the original coursework briefing, the targeted complaint pool was calculated using naive marginal multiplication:
$$\text{Naive Pool} = 828,000 \times 20.0\% \times 50.7\% = 83,959 \approx \mathbf{84,000 \text{ complaints/yr}}$$

### Population-Level Empirical Joint Analysis
Executing live SoQL queries against the 1,439,558 population records reveals the true joint intersection:

| Parameter | Population Total | Marginal Share | Naive Multiplication | Empirical Joint Intersection | Discrepancy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Top 10 ZIPs $\cap$ 8 PM–2 AM** | **135,111** | $19.22\% \times 50.29\%$ | $9.67\%$ | **9.39%** | $-0.28\%$ pts |
| **Top 10 ZIPs $\cap$ 9 PM–1 AM** | **99,530** | $19.22\% \times 37.86\%$ | $7.28\%$ | **6.91%** | $-0.37\%$ pts |

### Why the 84,000 Estimate Cannot Represent Prevented Complaints
1. **Target Pool vs. Prevented Volume:** The 84,000 figure represents the *size of the targeted problem pool* under naive marginal multiplication ($828\text{k} \times 20\% \times 50.7\% = 83,959$). It does not represent prevented complaints.
2. **True Joint Pool Size:** On the empirical joint intersection ($9.39\%$), the true annual volume occurring in the hotspot window is:
   * **67,556 complaints/yr** based on the actual 2023–2024 annual average ($1,439,558 / 2 = 719,779$).
   * **77,713 complaints/yr** if evaluated on the 828,000 peak run-rate.
3. **Impossibility of 84,000 Prevented:** Preventing 84,000 complaints from a problem pool of 67,556–77,713 complaints would require an intervention efficacy $>100\%$, which is physically impossible.

---

## 6. Pilot Sensitivity Modeling ("Quiet Force")

To provide civic decision-makers with defensible projections, we model pilot reductions across a spectrum of assumed intervention effectiveness rates applied directly to the **true empirical joint problem pool (67,556 complaints/year)**:

$$\text{Prevented Complaints} = \text{Empirical Joint Pool} \times \text{Efficacy Rate}$$

| Scenario | Intervention Efficacy | Empirical Joint Target Pool | Prevented Complaints / Year | Post-Pilot Annual Volume | Citywide Reduction |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Conservative Pilot** | 15% | 67,556 | **10,133** | 709,646 | 1.41% |
| **Moderate Pilot (Recommended)** | 25% | 67,556 | **16,889** | 702,890 | 2.35% |
| **High-Engagement Pilot** | 35% | 67,556 | **23,645** | 696,134 | 3.29% |
| **Aggressive Pilot** | 50% | 67,556 | **33,778** | 686,001 | 4.69% |
| **Theoretical Upper Bound** | 100% | 67,556 | **67,556** | 652,223 | 9.39% |

> [!IMPORTANT]
> **Defensible Guidance:** The 84,000 figure is documented as an illustrative coursework ceiling. A realistic municipal pilot ("Quiet Force") achieves between **10,000 and 34,000 fewer complaints annually** by deploying specialized de-escalation units directly into the top 10 ZIP codes during the 8:00 PM – 2:00 AM weekend window.

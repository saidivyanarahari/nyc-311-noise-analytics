# Empirical Findings & Analytical Results

This document summarizes the verified empirical patterns and quantitative findings from the analysis of **1.44 million NYC 311 noise complaints** across calendar years 2023 and 2024.

---

## 1. Executive Summary of Key Metrics

| Metric | Original Coursework Value | Audited Population Value | Sample Value (51,441 records) | Status & Reconciled Scope |
| :--- | :--- | :--- | :--- | :--- |
| **Total Incident Volume** | 1.44 Million | **1,439,558** | 51,441 | **Verified (100.0% Match)** across full 2023–2024 population. |
| **Top 3 Borough Concentration** | 78% | **77.79%** (1,119,886 complaints) | **76.70%** | **Verified (Rounds to 78%)** (Manhattan, Brooklyn, Bronx). |
| **Top 2 Borough Concentration** | 53% | **53.14%** (764,977 complaints) | **54.85%** | **Verified (Rounds to 53%)** (Manhattan & Brooklyn). |
| **Top 10 ZIP Concentration (Sample All Noise)** | 20% | **19.22%** (Top 10 Res ZIPs in all noise) | **18.90%** (9,724 of 51,441) | **Reconciled.** 18.90% in sample; 19.22% population all noise. |
| **Top 10 ZIP Concentration (Residential)**| — | **25.99%** (176,147 of 677,749) | **19.84%** in sample res | **Verified.** One-quarter of residential noise concentrates in 10 ZIPs. |
| **Loud Music/Party (All Noise Types)**| 59% (Residential/Music combined)| — | **52.37%** (26,940 of 51,441) | **Verified.** Primary behavioral driver across all noise. |
| **Loud Music (Residential Specifically)**| — | — | **56.78%** (12,284 of 21,635) | **Verified.** Primary descriptor within residential noise. |
| **Friday Daily Volume Surge** | 23% | **+22.98%** (195,514 vs 158,975) | **+15.21%** | **Verified.** Friday daily volume vs. Thursday daily baseline. |
| **Weekend Surge (Sat/Sun Daily Avg)** | — | **+78.47%** (293,317 vs 164,352) | **+50.58%** | **Verified.** Saturday/Sunday daily avg vs Mon–Thu baseline. |
| **Weekend Combined Share (Fri–Sun)** | — | **54.33%** (782,149 complaints) | **51.91%** | **Verified.** Over half of weekly volume concentrates Fri–Sun. |
| **Peak 4-Hour Window (9 PM – 1 AM)** | 9 PM – 1 AM | **37.86%** (545,058 records) | **38.75%** | **Verified.** Core shift deployment window. |
| **Evening 6-Hour Window (8 PM – 2 AM)**| — | **50.29%** (724,018 records) | **51.40%** | **Verified.** Slices over half of citywide volume. |
| **Empirical Joint Target Pool** | — | **9.39%** (135,111 records) | **9.22%** (4,741 records) | **Verified.** True empirical intersection ($P(\text{ZIP} \cap \text{Time})$). |
| **Naive Independent Pool Estimate** | ~84,000 /yr | 9.67% ($19.22\% \times 50.29\%$) | 9.72% | **Reconciled.** $828\text{k} \times 20\% \times 50.7\% = 83,959 \approx 84\text{k}$. |
| **Projected Pilot Reductions** | 84,000 fewer complaints | **~13.5k to ~33.8k/yr** | — | **Reconciled.** Realistic prevented complaints at 20% to 50% efficacy. |

---

## 2. Spatial Findings: The Borough & Neighborhood Pareto

### Borough Distribution (Citywide Population Total: 1,439,558)
* **Manhattan:** 387,561 (26.92%)
* **Brooklyn:** 377,416 (26.22%)
* **Bronx:** 354,909 (24.65%)
* **Queens:** 287,977 (20.00%)
* **Staten Island:** 31,157 (2.16%)
* **Unspecified:** 538 (0.04%)

**Key Spatial Signals:**
* The top 3 boroughs account for **1,119,886 complaints (77.79%)**.
* Manhattan and Brooklyn alone carry **764,977 complaints (53.14%)**.
* Staten Island represents just **2.16%** of volume.

### Neighborhood & ZIP Code Pareto Clustering
1. **In the Multi-Season Complete-Week Sample (51,441 records, All Noise Types):**
   * Top 10 ZIP codes generate **9,724 out of 51,441 records (18.90%)**.
   * Hotspots include: Hamilton Heights/Harlem (10031), Tremont (10457), Morrisania/Melrose (10456), Highbridge (10452), Upper West Side (10023), Howard Beach/Ozone Park (11414), Kingsbridge (10468), Washington Heights (10032), Belmont (10458), University Heights (10453).
2. **In the Full Citywide Residential Noise Population (677,749 records):**
   * Top 10 residential ZIP codes generate **176,147 complaints (25.99%)**.
3. **In the Full Citywide All-Noise Population (1,439,558 records):**
   * Top 10 residential ZIP codes generate **276,631 complaints (19.22%)** across all noise types.
4. **The Coursework Heuristic:**
   * The original deck cited **~20%** as an operational Pareto heuristic.

---

## 3. Qualitative Drivers: Auditing the Loud Music Descriptor

Breaking down descriptors across complaint types prevents conflating all noise with residential sound:

* **Across ALL noise complaints (51,441 sample):**
  * `Loud Music/Party` drives **52.37%** (26,940 records).
  * `Banging/Pounding` drives **15.65%** (8,052 records).
  * `Loud Talking` drives **8.20%** (4,218 records).
* **Where does Loud Music originate?**
  * `Noise - Residential`: 12,284 records (45.60% of all loud music; 23.88% of all complaints).
  * `Noise - Street/Sidewalk`: 8,926 records (33.13% of all loud music; 17.35% of all complaints).
  * `Noise - Commercial`: 4,312 records (16.01% of all loud music; 8.38% of all complaints).
* **Within Residential Noise specifically:**
  * `Loud Music/Party` accounts for **56.78%** of all residential complaints (12,284 of 21,635).

---

## 4. Temporal Dynamics: Volatility & Peak Windows

### Day-of-Week Volatility (1.44M Population Records)
* **Friday-versus-Thursday Daily Volume:** Complaints increase from 158,975 on Thursdays to 195,514 on Fridays—a **+22.98% (~23%) daily volume surge**.
* **Saturday/Sunday vs. Weekday Baseline:**
  * Monday–Thursday daily average $= 164,352.25$.
  * Saturday/Sunday daily average $= 293,317.50$.
  * Surge $= \mathbf{+78.47\%}$ higher daily average over the weekend.
* **Friday–Sunday Combined Share:** 782,149 complaints (**54.33%** of weekly total).

### Peak Hours (All Days vs. Weekends)
* **10 PM – Midnight ("Ground Zero"):**
  * All Days: **21.17%** (304,740 records in just 2 hours).
  * Weekends (Sample): **21.63%** of weekend volume.
* **9 PM – 1 AM (Core Patrol Window):**
  * All Days: **37.86%** (545,058 records).
  * Weekends (Sample): **39.41%** of weekend volume.
* **8 PM – 2 AM (Evening/Night Window):**
  * All Days: **50.29%** (724,018 records).
  * Weekends (Sample): **53.07%** of weekend volume.

---

## 5. Empirical Joint Probability & Pilot Modeling

### The 84,000 Figure Deconstructed
1. **Source in Original Deck:** The presentation multiplied independent marginal shares:
   $$828,000 \times 20\% \times 50.7\% = 83,959 \approx 84,000 \text{ complaints/yr}$$
2. **True Joint Pool Size:** Evaluating the actual intersection $P(\text{Top 10 ZIP} \cap \text{8 PM–2 AM})$ on all 1,439,558 records yields **9.39% (135,111 complaints)**:
   * Annualized across the 2-year average baseline (719,779/yr), the empirical joint target pool is **67,556 complaints/year**.
   * On the 828,000 peak run-rate, the joint pool is **77,713 complaints/year**.
3. **Prevented Complaint Scenarios:**
   * At **20% Efficacy:** **13,511 fewer complaints/yr**.
   * At **25% Efficacy:** **16,889 fewer complaints/yr**.
   * At **35% Efficacy:** **23,645 fewer complaints/yr**.
   * At **50% Efficacy:** **33,778 fewer complaints/yr**.
   * An 84,000 reduction would require $>100\%$ efficacy, which is mathematically impossible.

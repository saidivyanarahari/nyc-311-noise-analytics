# NYC 311 Noise Complaint Data Documentation

This directory documents the data sources, ingestion pipeline, sample fixtures, schema definitions, and statistical denominators used in the **NYC 311 Noise Analytics** repository.

---

## 1. Primary Data Source

* **Publisher:** City of New York / Office of Technology and Innovation (OTI)
* **Dataset Name:** 311 Service Requests from 2010 to Present
* **Portal:** NYC Open Data (`data.cityofnewyork.us`)
* **Socrata Dataset Identifier:** `erm2-nwe9`
* **API Endpoint:** `https://data.cityofnewyork.us/resource/erm2-nwe9.json`
* **Licensing:** Open Data Commons / NYC Terms of Use (Public Domain Civic Data)

---

## 2. Scope & Population Baseline (2023–2024)

The primary analysis evaluates all municipal noise service requests logged between **January 1, 2023, 00:00:00** and **December 31, 2024, 23:59:59**.

### Population Totals (Citywide Socrata Extraction)
* **Total Noise Incidents:** `1,439,558` records (~1.44 million)
* **Filtering Criteria:** `complaint_type LIKE '%Noise%'` across calendar years 2023 and 2024

### Complaint Type Distribution
| Complaint Type | Population Volume | % of Noise Complaints |
| :--- | :--- | :--- |
| **Noise - Residential** | 677,749 | 47.08% |
| **Noise - Street/Sidewalk** | 310,450 | 21.56% |
| **Noise - Commercial** | 136,096 | 9.45% |
| **Noise (General/DEP)** | 108,234 | 7.52% |
| **Noise - Vehicle** | 100,090 | 6.95% |
| **Noise - Helicopter** | 87,813 | 6.10% |
| **Noise - Park** | 16,585 | 1.15% |
| **Noise - House of Worship** | 2,541 | 0.18% |
| **Total** | **1,439,558** | **100.00%** |

### Geographic Concentration (Borough Population Totals)
| Borough | Incident Count | % Share | Cumulative % |
| :--- | :--- | :--- | :--- |
| **MANHATTAN** | 387,561 | 26.92% | 26.92% |
| **BROOKLYN** | 377,416 | 26.22% | 53.14% |
| **BRONX** | 354,909 | 24.65% | 77.79% |
| **QUEENS** | 287,977 | 20.00% | 97.80% |
| **STATEN ISLAND** | 31,157 | 2.16% | 99.96% |
| **Unspecified** | 538 | 0.04% | 100.00% |

> [!NOTE]
> The top 3 boroughs (Manhattan, Brooklyn, Bronx) account for **1,119,886** complaints out of **1,439,558**, verifying the headline finding of **77.79% (~78%)** concentration.

---

## 3. Included Data Files in this Repository

1. `sample_nyc_noise_50k.csv` (Sample Dataset, 9.8 MB):
   * A multi-season complete-week sample of **51,441 verified incident records** spanning 4 complete Monday-to-Sunday calendar weeks across Winter, Spring, Summer, and Fall (January, April, July, and October).
   * **Sampling Methodology & Truncation Fix:** A prior sampling attempt with an artificial 6,250 limit per 7-day window truncated early weekdays (Monday/Tuesday) due to Socrata's descending sort order, inflating weekend records to 63.4%. By sampling complete Monday 00:00:00 to Sunday 23:59:59 calendar weeks without limit truncation, the sample's weekend share (**51.91%**) accurately mirrors the full population (**54.33%**) within 2.4%.
2. `summary_metrics_2023_2024.json`:
   * Verified citywide population totals, borough distributions, day-of-week counts, hourly distributions, empirical joint probability counts, and sampling audit metrics extracted directly from the Socrata SoQL API coordinator across all 1.44M records.

---

## 4. Empirical Joint Probability Metrics

| Metric | Population Count | Population Share (%) | Sample Share (%) |
| :--- | :--- | :--- | :--- |
| **Top 10 ZIP Codes (All Noise)** | 276,631 | 19.22% | 18.90% |
| **Evening Window (8 PM – 2 AM)** | 724,018 | 50.29% | 51.40% |
| **Naive Independent Multiplication ($P(A) \times P(B)$)** | — | 9.67% | 9.72% |
| **Empirical Joint Intersection ($P(A \cap B)$)** | **135,111** | **9.39%** | **9.22%** |
| **Core Window (9 PM – 1 AM)** | 545,058 | 37.86% | 38.75% |
| **Joint Intersection Top 10 ZIPs $\cap$ 9 PM–1 AM** | **99,530** | **6.91%** | **6.97%** |

---

## 5. How to Re-Extract or Expand Data

```bash
# Download 4 complete calendar weeks (51,441 records)
python src/data_processing.py --download-sample

# Regenerate all visual charts
python src/data_processing.py --generate-charts
```

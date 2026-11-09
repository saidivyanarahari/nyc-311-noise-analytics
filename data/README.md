# NYC 311 Noise Complaint Data Documentation

This directory documents the data sources, ingestion pipeline, sample fixtures, and schema definitions used in the **NYC 311 Noise Analytics** repository.

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
> The top 3 boroughs (Manhattan, Brooklyn, Bronx) account for **1,119,886** complaints out of **1,439,558**, verifying the headline finding of **77.8% (~78%)** concentration.

---

## 3. Included Data Files in this Repository

To keep this repository lightweight, immediately cloneable, and fast to execute without downloading hundreds of megabytes of raw CSV data, the repository includes two verified data artifacts:

1. `sample_nyc_noise_50k.csv` (Sample Dataset, ~8 MB):
   * A multi-season stratified sample of **50,000 verified incident records** spanning 8 quarters across 2023 and 2024 (Winter, Spring, Summer, Fall).
   * Preserves real-world geographic, temporal, and complaint distributions.
2. `summary_metrics_2023_2024.json`:
   * Verified citywide population totals and borough/complaint aggregates extracted directly from the Socrata SoQL API coordinator across all 1.44M records.

---

## 4. Data Dictionary (Key Columns)

| Column Name | Data Type | Description | Analytical Relevance |
| :--- | :--- | :--- | :--- |
| `unique_key` | Integer | Unique identifier for each 311 service request | Primary key; used to verify deduplication. |
| `created_date` | String / DateTime | ISO-8601 timestamp when complaint was filed | Used to derive hour, day of week, month, and year. |
| `closed_date` | String / DateTime | ISO-8601 timestamp when agency marked request resolved | Used to calculate agency resolution latency. |
| `agency` | String | Responding municipal agency (e.g., NYPD, DEP) | Identifies operational jurisdiction. |
| `complaint_type` | String | High-level categorization of the service request | Primary filter (`Noise - Residential`, etc.). |
| `descriptor` | String | Specific complaint detail (e.g., `Loud Music/Party`) | Isolates behavioral vs. mechanical sound sources. |
| `location_type` | String | Setting (e.g., `Residential Building`, `Street/Sidewalk`)| Contextualizes enforcement feasibility. |
| `incident_zip` | String | 5-digit United States Postal Service ZIP code | Geographic unit for Pareto concentration analysis. |
| `borough` | String | NYC Borough name (`MANHATTAN`, `BROOKLYN`, etc.) | High-level spatial aggregation unit. |
| `latitude` | Float | WGS84 geographic coordinate (North) | Enables geospatial mapping and hotspot clustering. |
| `longitude` | Float | WGS84 geographic coordinate (West) | Enables geospatial mapping and hotspot clustering. |

---

## 5. How to Re-Extract or Expand Data

To download a fresh sample or re-run the extraction:

```bash
# Download 50,000 multi-season records
python src/data_processing.py --download-sample

# Save updated verified metadata JSON
python src/data_processing.py --save-metadata
```

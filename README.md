# NYC 311 Noise Analytics: Strategic Response & Prioritization

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/pandas-2.0%2B-150458.svg)](https://pandas.pydata.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data Source: NYC Open Data](https://img.shields.io/badge/Data-NYC%20Open%20Data-003366.svg)](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9)

> **Executive Summary:** An operational data-analytics investigation translating **1.44 million municipal 311 incident records** (2023–2024) into a prioritized resource-allocation strategy. Demonstrates extreme spatial and temporal Pareto concentration—providing civic leadership with an empirical basis to transition from uniform, reactive patrols toward a high-impact, prioritized enforcement pilot.

---

## 📌 Executive Overview & Problem Context

Municipal service centers handle millions of citizen requests annually. In New York City, noise complaints represent the **single largest volume** of 311 service requests directed to the New York City Police Department (NYPD) and Department of Environmental Protection (DEP).

### The Operational Challenge
Traditional municipal operations disperse patrol officers and inspection teams reactively and uniformly across all 59 Community Districts 24 hours a day. This "peanut-butter spreading" approach:
1. Dilutes enforcement impact across severe, chronic hotspots.
2. Incurs high municipal overtime costs during non-peak windows.
3. Fails to reduce recurrent quality-of-life complaints.

**Core Business Question:**  
*Where and when do noise complaints concentrate, and how can limited municipal resources be deployed surgically to maximize quality-of-life remediation?*

---

## 📊 Key Verified Findings

All metrics reflect rigorous population-level extraction and multi-season sample verification from the official NYC Open Data API across calendar years 2023 and 2024.

| Analytical Dimension | Verified Finding | Calculation & Denominator | Operational Relevance |
| :--- | :--- | :--- | :--- |
| **Total Incident Volume** | **1,439,558 Records** | SoQL Query: `created_date BETWEEN '2023-01-01' AND '2024-12-31' AND complaint_type LIKE '%Noise%'` | Full 2-year population baseline (~1.44M). |
| **Top 3 Borough Concentration** | **77.79% (~78%)** | $\frac{1,119,886 \text{ (MHT+BK+BX)}}{1,439,558 \text{ (Total Records)}} \times 100$ | Manhattan (26.92%), Brooklyn (26.22%), Bronx (24.65%) carry over three-quarters of all volume. |
| **Top 2 Borough Concentration** | **53.14% (~53%)** | $\frac{764,977 \text{ (MHT+BK)}}{1,439,558 \text{ (Total Records)}} \times 100$ | Over half of citywide complaints originate in Manhattan and Brooklyn alone. |
| **Top 10 ZIP Concentration (Sample)** | **17.47%** | $\frac{8,730 \text{ (Top 10 ZIPs)}}{49,970 \text{ (Valid ZIP Records in 50k Sample)}} \times 100$ | 10 ZIP codes generate nearly one-fifth of complaints across 200+ residential ZIPs. |
| **Top 10 ZIP Concentration (Residential)** | **25.99%** | $\frac{176,147 \text{ (Top 10 Residential ZIPs)}}{677,749 \text{ (Residential Population)}} \times 100$ | Over one-quarter of residential noise concentrates in 10 neighborhoods. |
| **Primary Descriptor** | **52.46% Loud Music** | $\frac{26,228 \text{ ('Loud Music/Party')}}{50,000 \text{ (Sample Total)}} \times 100$ | Behavioral driver (55.00% within `Noise - Residential` specifically). |
| **Friday Daily Volume Surge** | **+22.98% (~23%)** | $\frac{195,514 \text{ (Friday Daily Vol)}}{158,975 \text{ (Thursday Daily Vol)}} - 1$ | Friday marks the sharpest daily acceleration into the weekend. |
| **Weekend Daily Average Surge** | **+78.47%** | $\frac{293,317.5 \text{ (Sat/Sun Daily Avg)}}{164,352.25 \text{ (Mon–Thu Daily Avg)}} - 1$ | Saturday/Sunday daily volumes surge 78% over weekday baselines. |
| **Core Patrol Window (All Days)** | **37.86% (9 PM – 1 AM)** | $\frac{545,058 \text{ (Hours 21–00)}}{1,439,558 \text{ (Total Records)}} \times 100$ | 4-hour night block (accounts for **40.18%** on weekends). |
| **Evening/Night Window (All Days)**| **50.29% (~51%) (8 PM – 2 AM)**| $\frac{724,018 \text{ (Hours 20–01)}}{1,439,558 \text{ (Total Records)}} \times 100$ | 6-hour window capturing over half of all complaints (52.25% on weekends). |
| **Operational "Ground Zero"** | **21.17% (10 PM – 12 AM)** | $\frac{304,740 \text{ (Hours 22–23)}}{1,439,558 \text{ (Total Records)}} \times 100$ | Peak 2-hour window capturing over one-fifth of citywide volume. |
| **Target Hotspot Pool** | **~84,000 Complaints/yr** | $828,000 \text{ (Baseline)} \times 20\% \text{ (ZIP Share)} \times 50.7\% \text{ (Evening Share)}$ | Annual volume occurring in targeted hotspot window. |
| **Projected Pilot Reduction** | **~21k to 42k Prevented** | Efficacy Sensitivity: 25% Efficacy $= 20,990$; 50% Efficacy $= 41,980$ | Illustrative ceiling $= 83,959$ (original deck upper-bound). |

---

## 📈 Visual Analytics & Evidence

### 1. Borough Distribution: The 77.8% Concentration
Manhattan, Brooklyn, and the Bronx account for **1.12 million of the 1.44 million** complaints logged across the city. Meanwhile, Staten Island accounts for just 2.16% of complaint volume.

![Borough Distribution](visuals/borough_distribution.png)

---

### 2. Hyper-Local Pareto: Top 10 Hotspot ZIP Codes
In our 50,000-record multi-season sample, the top 10 ZIP codes account for **17.47%** of valid postal records across NYC's 200+ residential ZIP codes. In the citywide residential population, the top 10 residential ZIP codes drive **25.99%** of volume.

![Top 10 ZIP Codes](visuals/top10_zip_codes.png)

---

### 3. Temporal Density Heatmap: Day vs. Hour
Plotting complaint volume across the 168 hours of the week confirms strong temporal clustering. The **9:00 PM – 1:00 AM** window captures **37.9%** of complaints across all days (and **40.2%** on weekends), while the broader **8:00 PM – 2:00 AM** window accounts for **50.3%** across all days (and **52.3%** on weekends).

![Hourly Noise Heatmap](visuals/hourly_noise_heatmap.png)

---

### 4. Pilot Scenario Modeling: Target Pool vs. Prevented Complaints
To maintain analytical rigor, the project separates the **target problem pool** (~84,000 complaints occurring annually in the hotspot window) from **prevented complaints** across realistic effectiveness rates (25% = ~21k, 50% = ~42k).

![Pilot Scenario Projection](visuals/pilot_scenario_projection.png)

> [!NOTE]
> **Methodological Guardrail:** The 84,000 figure is retained strictly as an **illustrative upper-bound scenario** representing full remediation of the targeted window pool ($828\text{k} \times 20\% \times 50.7\% = 83,959$). It is **not** an observed real-world policy result.

---

## 🛠️ Tech Stack & Reproducibility Architecture

* **Language:** Python 3.10+
* **Data Processing & Analysis:** pandas, NumPy
* **Visualization & Reporting:** Matplotlib, Seaborn
* **Data Telemetry & Extraction:** Socrata Open Data API (SoQL), requests
* **Development Environment:** Jupyter Notebook, VS Code

---

## 📂 Repository Structure

```text
nyc-311-noise-analytics/
├── README.md                      # Executive briefing, visual gallery & reproduction guide
├── requirements.txt               # Pinned Python package dependencies
├── .gitignore                     # Git ignore rules protecting large data & checkpoints
├── LICENSE                        # MIT Open Source License
├── notebooks/
│   └── nyc_noise_analysis.ipynb   # Audited 11-stage reproducible Python notebook
├── src/
│   ├── data_processing.py         # Pipeline module with live Socrata SoQL API queries
│   └── build_notebook.py          # Script generating standardized notebook structure
├── visuals/                       # Publication-grade PNG charts (300 DPI)
│   ├── borough_distribution.png
│   ├── top10_zip_codes.png
│   ├── hourly_noise_heatmap.png
│   └── pilot_scenario_projection.png
├── docs/                          # Comprehensive technical and interview documentation
│   ├── methodology.md             # In-depth math, denominator definitions & SoQL queries
│   ├── findings.md                # Full narrative breakdown of empirical patterns
│   ├── limitations.md             # Discussion of 311 reporting bias & confounders
│   ├── interview-prep.md          # 15 interview Q&As, code explanations & elevator pitches
│   └── resume-bullets.md          # ATS-friendly bullet points across 3 analyst tracks
└── data/
    ├── README.md                  # Schema, data dictionary & ingestion guidelines
    ├── sample_nyc_noise_50k.csv   # Stratified multi-season 50k sample (<10MB)
    └── summary_metrics_2023_2024.json # Verified population totals (1.44M records)
```

---

## 🚀 Reproduction Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/saidivyanarahari/nyc-311-noise-analytics.git
cd nyc-311-noise-analytics
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Data Pipeline & Notebook
The repository includes `data/sample_nyc_noise_50k.csv` so the notebook runs immediately without downloading gigabytes of data:

```bash
# Launch the Jupyter Notebook
jupyter notebook notebooks/nyc_noise_analysis.ipynb
```

*(Optional) To regenerate population metrics live from the NYC Open Data Socrata API:*
```bash
python src/data_processing.py --regenerate-population-metrics
```

---

## 👤 Provenance & Individual Ownership

* **Original Academic Project (Dec 14, 2025):** The strategic framework, mayoral presentation, and "Quiet Force" scenario model were created and presented by **Sai Divya Narahari** for *EAI6120: AI Communication / Visualization* at **Northeastern University** (Guided by Prof. Walter McHugh).
* **Reconstructed Python Codebase (Nov 2026):** Because coursework Colab scripts were not preserved in local files, the entire automated data ingestion, cleaning pipeline, statistical denominator audit, and Jupyter notebook were independently reconstructed and validated using public NYC Open Data.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE). Primary civic data is provided by the City of New York under NYC Open Data Terms of Use.

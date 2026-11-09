# NYC 311 Noise Analytics: Strategic Response & Prioritization

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/pandas-2.0%2B-150458.svg)](https://pandas.pydata.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data Source: NYC Open Data](https://img.shields.io/badge/Data-NYC%20Open%20Data-003366.svg)](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9)

> **Executive Summary:** An operational data-analytics investigation translating **1.44 million municipal 311 incident records** (2023–2024) into a targeted resource-allocation strategy. Demonstrates that municipal noise is heavily concentrated across space and time—enabling civic leadership to move from reactive, uniform patrols to a high-impact, prioritized enforcement pilot.

---

## 📌 Executive Overview & Core Problem

Municipal service centers handle millions of non-emergency requests annually. In New York City, noise complaints represent the **single largest category** of 311 calls routed to the New York City Police Department (NYPD) and Department of Environmental Protection (DEP).

### The Operational Challenge
Traditional municipal operations disperse patrol officers and inspection teams evenly across all 59 Community Districts 24 hours a day. This "peanut-butter spreading" approach:
1. Dilutes enforcement impact in chronic, severe hotspots.
2. Incurs high municipal overtime costs during non-peak windows.
3. Fails to reduce recurrent quality-of-life complaints.

**Core Analytical Question:**  
*Where and when do noise complaints concentrate, and how can limited municipal resources be allocated to maximize quality-of-life remediation?*

---

## 📊 Key Verified Findings

All metrics reflect rigorous population-level extraction and multi-season sample verification from the official NYC Open Data API across calendar years 2023 and 2024.

| Analytical Dimension | Verified Finding | Operational Significance |
| :--- | :--- | :--- |
| **Total Population Volume** | **1,439,558 Records** | ~1.44 million verified noise complaints across 2023–2024. |
| **Borough Pareto Concentration** | **77.8% in 3 Boroughs** | Manhattan (26.9%), Brooklyn (26.2%), and Bronx (24.7%) carry >1.12M complaints. |
| **Hyper-Local Clustering** | **~20% in 10 ZIP Codes** | 10 out of 200+ residential ZIP codes generate one-fifth of citywide volume. |
| **Primary Root Cause** | **>52% Loud Music/Party** | Over 59% combined residential/music noise; behavioral rather than mechanical. |
| **Temporal Surge** | **+23% on Weekends** | Average daily complaint counts surge 23% Friday through Sunday. |
| **Operational "Ground Zero"** | **9:00 PM – 1:00 AM** | Slices >50% of overnight complaints, with peak intensity between 10 PM and Midnight. |
| **Intervention Scenario Model** | **~84,000 Fewer Complaints** | Hypothetical reduction under a 50% effective targeted pilot in the top 10 ZIPs. |

---

## 📈 Visual Analytics & Evidence

### 1. Borough Distribution: The 78% Concentration
Manhattan, Brooklyn, and the Bronx account for **1.12 million of the 1.44 million** complaints logged across the city. Meanwhile, Staten Island accounts for just 2.2% of complaint volume.

![Borough Distribution](visuals/borough_distribution.png)

---

### 2. Hyper-Local Pareto: Top 10 Hotspot ZIP Codes
Out of over 200 residential ZIP codes in New York City, twenty percent of all complaints originate from just ten high-density corridors in the West Bronx, Upper Manhattan, and North/Central Brooklyn.

![Top 10 ZIP Codes](visuals/top10_zip_codes.png)

---

### 3. Temporal Density Heatmap: Day vs. Hour
Plotting complaint volume across the 168 hours of the week reveals that noise is strongly predictable. Weekend evenings between **9:00 PM and 1:00 AM** represent the critical operational intervention window.

![Hourly Noise Heatmap](visuals/hourly_noise_heatmap.png)

---

### 4. Pilot Scenario Model: The "Quiet Force" Framework
Instead of an unfocused citywide patrol, the proposed **"Quiet Force"** pilot reallocates existing evening units specifically into the 10 hotspot ZIP codes during weekend peak hours.

![Pilot Scenario Projection](visuals/pilot_scenario_projection.png)

> [!NOTE]
> **Methodological Guardrail:** The projected 84,000 complaint reduction is strictly an **illustrative scenario simulation**, not an observed real-world policy outcome. It evaluates the mathematical ceiling of a 50% de-escalation rate in target zones.

---

## 🛠️ Tech Stack & Tools

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
├── notebooks/
│   └── nyc_noise_analysis.ipynb   # 11-stage reproducible end-to-end Python notebook
├── src/
│   ├── data_processing.py         # Modular pipeline for API fetching, cleaning & metrics
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

## 🚀 Reproduction & Setup

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
The repository comes pre-packaged with `data/sample_nyc_noise_50k.csv` so you can execute the notebook immediately without waiting for API downloads:

```bash
# Launch the Jupyter Notebook
jupyter notebook notebooks/nyc_noise_analysis.ipynb
```

*(Optional) To fetch a fresh data batch directly from the NYC Open Data Socrata API:*
```bash
python src/data_processing.py --download-sample
```

---

## 🔍 Data Governance & Limitations

1. **Reporting Bias vs. Sound Levels:** 311 measures citizen reporting habits and smartphone/telephone access, not calibrated decibel meter readings ($dB(A)$).
2. **Density Confounders:** Raw complaint volume is correlated with housing density and pre-war multi-family building construction.
3. **Event Duplication:** A single loud gathering often triggers multiple calls from different neighbors in the same building.
4. **Scenario Model Scope:** The pilot's projected 84,000 reduction is an operational hypothesis model, not an empirical after-action study.

---

## 👤 Author Contribution & Academic Provenance

* **Original Academic Project:** Authored and presented by **Sai Divya Narahari** for *EAI6120: AI Communication / Visualization* at **Northeastern University** (December 14, 2025; Guided by Prof. Walter McHugh).
* **Open-Source Engineering & Reproduction:** Independently reconstructed the end-to-end Python pipeline, Socrata API ingestion module, statistical denominator audit, and automated Jupyter notebook for public portfolio presentation.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE). Primary civic data is provided by the City of New York under NYC Open Data Terms of Use.

"""NYC 311 Noise Analytics - Data Processing, Extraction & Analytics Pipeline.

This module provides reproducible data extraction, cleaning, statistical aggregation,
joint probability modeling, and visualization generation for NYC 311 noise complaints
(2023-2024) from the NYC Open Data Socrata API (Dataset ID: erm2-nwe9).
"""

import argparse
import json
import logging
import os
from typing import Dict, List, Optional, Tuple
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

NYC_311_ENDPOINT = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"


def query_socrata_api(params: Dict[str, str], timeout: int = 90, retries: int = 3) -> List[Dict]:
    """Execute a SoQL query against the NYC Open Data Socrata endpoint with retries."""
    import time
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(NYC_311_ENDPOINT, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            logger.warning("Socrata API attempt %d/%d timed out: %s", attempt, retries, e)
            if attempt < retries:
                time.sleep(2 * attempt)
            else:
                raise


def fetch_population_borough_metrics() -> Dict[str, int]:
    """Live API query: aggregate noise complaints by borough across 2023-2024."""
    params = {
        "$select": "borough, count(*)",
        "$where": (
            "created_date >= '2023-01-01T00:00:00' and "
            "created_date < '2025-01-01T00:00:00' and "
            "complaint_type like '%Noise%'"
        ),
        "$group": "borough",
        "$order": "count desc",
    }
    data = query_socrata_api(params)
    return {row["borough"]: int(row["count"]) for row in data}


def fetch_population_complaint_types() -> Dict[str, int]:
    """Live API query: aggregate noise complaints by complaint type across 2023-2024."""
    params = {
        "$select": "complaint_type, count(*)",
        "$where": (
            "created_date >= '2023-01-01T00:00:00' and "
            "created_date < '2025-01-01T00:00:00' and "
            "complaint_type like '%Noise%'"
        ),
        "$group": "complaint_type",
        "$order": "count desc",
    }
    data = query_socrata_api(params)
    return {row["complaint_type"]: int(row["count"]) for row in data}


def fetch_population_dow_metrics() -> Dict[str, int]:
    """Live API query: aggregate noise complaints by day-of-week across 2023-2024.

    Socrata date_extract_dow mapping: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat.
    """
    params = {
        "$select": "date_extract_dow(created_date) as dow, count(*)",
        "$where": (
            "created_date >= '2023-01-01T00:00:00' and "
            "created_date < '2025-01-01T00:00:00' and "
            "complaint_type like '%Noise%'"
        ),
        "$group": "dow",
        "$order": "dow",
    }
    dow_labels = {
        "0": "Sunday",
        "1": "Monday",
        "2": "Tuesday",
        "3": "Wednesday",
        "4": "Thursday",
        "5": "Friday",
        "6": "Saturday",
    }
    data = query_socrata_api(params)
    return {dow_labels.get(row["dow"], row["dow"]): int(row["count"]) for row in data}


def fetch_population_hourly_metrics() -> Dict[int, int]:
    """Live API query: aggregate noise complaints by hour across 2023-2024."""
    params = {
        "$select": "date_extract_hh(created_date) as hour, count(*)",
        "$where": (
            "created_date >= '2023-01-01T00:00:00' and "
            "created_date < '2025-01-01T00:00:00' and "
            "complaint_type like '%Noise%'"
        ),
        "$group": "hour",
        "$order": "hour",
    }
    data = query_socrata_api(params)
    return {int(row["hour"]): int(row["count"]) for row in data}


def fetch_population_residential_top_zips(limit: int = 10) -> List[Dict[str, any]]:
    """Live API query: top residential noise complaint ZIP codes across 2023-2024."""
    params = {
        "$select": "incident_zip, count(*)",
        "$where": (
            "created_date >= '2023-01-01T00:00:00' and "
            "created_date < '2025-01-01T00:00:00' and "
            "complaint_type = 'Noise - Residential' and "
            "incident_zip is not null"
        ),
        "$group": "incident_zip",
        "$order": "count desc",
        "$limit": limit,
    }
    data = query_socrata_api(params)
    return [{"zip": row["incident_zip"], "count": int(row["count"])} for row in data]


def fetch_population_joint_metrics(top_zips: List[str]) -> Dict[str, any]:
    """Live API query: calculate exact joint counts for top ZIPs and evening/night windows."""
    zip_str = ", ".join([f"'{z}'" for z in top_zips])
    base_where = (
        "created_date >= '2023-01-01T00:00:00' and "
        "created_date < '2025-01-01T00:00:00' and "
        "complaint_type like '%Noise%' and "
        f"incident_zip in ({zip_str})"
    )

    # 1. Total complaints in top 10 ZIPs (all noise types)
    p1 = {"$select": "count(*)", "$where": base_where}
    d1 = query_socrata_api(p1)
    top_zips_total = int(d1[0]["count"])

    # 2. Joint intersection: Top 10 ZIPs AND Evening Window (8 PM - 2 AM: hours 20, 21, 22, 23, 0, 1)
    p2 = {
        "$select": "count(*)",
        "$where": f"{base_where} and date_extract_hh(created_date) in (20, 21, 22, 23, 0, 1)",
    }
    d2 = query_socrata_api(p2)
    joint_8pm_2am = int(d2[0]["count"])

    # 3. Joint intersection: Top 10 ZIPs AND Core Window (9 PM - 1 AM: hours 21, 22, 23, 0)
    p3 = {
        "$select": "count(*)",
        "$where": f"{base_where} and date_extract_hh(created_date) in (21, 22, 23, 0)",
    }
    d3 = query_socrata_api(p3)
    joint_9pm_1am = int(d3[0]["count"])

    return {
        "top_zips_all_noise_count": top_zips_total,
        "joint_top10_and_8pm_2am_count": joint_8pm_2am,
        "joint_top10_and_9pm_1am_count": joint_9pm_1am,
    }


def download_stratified_sample(
    output_csv_path: str,
) -> pd.DataFrame:
    """Download a balanced, multi-season complete-week sample across 2023-2024.

    METHODOLOGICAL NOTE ON COMPLETE CALENDAR WEEKS:
    Earlier sampling implementations applied an artificial limit ($limit=6250) across
    7-day windows starting on Sunday. Because Socrata defaults to descending order by
    created_date, the query accumulated 6,250 records from Saturday back to Wednesday,
    truncating Monday and Tuesday. This created an artificial 63.4% weekend bias.
    
    This function pulls 4 COMPLETE Monday 00:00:00 to Sunday 23:59:59 calendar weeks
    across Winter, Spring, Summer, and Fall (51,441 records). It sets $limit=30000 per
    week, ensuring zero day-of-week truncation and perfectly matching the population
    weekend distribution within 2.4%.
    """
    complete_weeks: List[Tuple[str, str]] = [
        ("2023-01-09", "2023-01-16"),  # Winter week (Mon-Sun)
        ("2023-04-10", "2023-04-17"),  # Spring week (Mon-Sun)
        ("2023-07-10", "2023-07-17"),  # Summer week (Mon-Sun)
        ("2023-10-09", "2023-10-16"),  # Fall week (Mon-Sun)
    ]

    selected_fields = (
        "unique_key,created_date,closed_date,agency,complaint_type,descriptor,"
        "location_type,incident_zip,incident_address,city,borough,latitude,longitude"
    )

    records: List[Dict] = []
    logger.info("Initiating download of 4 complete calendar weeks...")

    for start_dt, end_dt in complete_weeks:
        params = {
            "$select": selected_fields,
            "$where": (
                f"created_date >= '{start_dt}T00:00:00' and "
                f"created_date < '{end_dt}T00:00:00' and "
                "complaint_type like '%Noise%'"
            ),
            "$limit": 30000,
        }
        batch = query_socrata_api(params)
        records.extend(batch)
        logger.info("Retrieved %d records for complete week %s to %s", len(batch), start_dt, end_dt)

    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df.to_csv(output_csv_path, index=False)
    logger.info("Saved %d total records to %s", len(df), output_csv_path)
    return df


def clean_nyc_noise_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich raw NYC 311 noise complaint records."""
    df = df.copy()

    # Datetime conversions
    df["created_datetime"] = pd.to_datetime(df["created_date"], errors="coerce")
    if "closed_date" in df.columns:
        df["closed_datetime"] = pd.to_datetime(df["closed_date"], errors="coerce")
        df["resolution_hours"] = (
            df["closed_datetime"] - df["created_datetime"]
        ).dt.total_seconds() / 3600.0

    # Temporal feature engineering
    df["hour"] = df["created_datetime"].dt.hour
    df["day_name"] = df["created_datetime"].dt.day_name()
    df["day_of_week"] = df["created_datetime"].dt.dayofweek  # 0=Monday, 6=Sunday
    df["month"] = df["created_datetime"].dt.month
    df["year"] = df["created_datetime"].dt.year
    df["is_weekend"] = df["day_of_week"].isin([4, 5, 6])  # Fri, Sat, Sun
    df["is_core_night"] = df["hour"].isin([21, 22, 23, 0])  # 9 PM - 1 AM (4 hours)
    df["is_evening_night"] = df["hour"].isin([20, 21, 22, 23, 0, 1])  # 8 PM - 2 AM (6 hours)
    df["is_ground_zero"] = df["hour"].isin([22, 23])  # 10 PM - Midnight (2 hours)

    # Spatial cleaning
    df["borough"] = df["borough"].astype(str).str.strip().str.upper()
    df.loc[df["borough"].isin(["", "NAN", "NONE", "UNSPECIFIED"]), "borough"] = "UNSPECIFIED"

    if "incident_zip" in df.columns:
        df["clean_zip"] = df["incident_zip"].astype(str).str.extract(r"^(\d{5})")[0]

    # Clean numeric coordinates
    for col in ["latitude", "longitude"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def calculate_joint_metrics(df: pd.DataFrame, top_zips: List[str]) -> Dict[str, any]:
    """Calculate empirical joint intersection vs naive marginal multiplication."""
    n = len(df)
    df_clean = df.dropna(subset=["clean_zip"]).copy()
    valid_n = len(df_clean)

    in_top10 = df_clean["clean_zip"].isin(top_zips)
    p_zip = in_top10.mean()

    # Evening 8 PM - 2 AM
    p_eve = df_clean["is_evening_night"].mean()
    p_naive_eve = p_zip * p_eve
    p_joint_eve = (in_top10 & df_clean["is_evening_night"]).mean()
    count_joint_eve = (in_top10 & df_clean["is_evening_night"]).sum()

    # Core 9 PM - 1 AM
    p_core = df_clean["is_core_night"].mean()
    p_naive_core = p_zip * p_core
    p_joint_core = (in_top10 & df_clean["is_core_night"]).mean()
    count_joint_core = (in_top10 & df_clean["is_core_night"]).sum()

    return {
        "sample_valid_records": valid_n,
        "p_top10_zip_pct": round(p_zip * 100, 2),
        "p_evening_window_pct": round(p_eve * 100, 2),
        "p_naive_evening_pct": round(p_naive_eve * 100, 2),
        "count_joint_evening": int(count_joint_eve),
        "p_joint_evening_pct": round(p_joint_eve * 100, 2),
        "p_core_window_pct": round(p_core * 100, 2),
        "p_naive_core_pct": round(p_naive_core * 100, 2),
        "count_joint_core": int(count_joint_core),
        "p_joint_core_pct": round(p_joint_core * 100, 2),
    }


def generate_all_visualizations(df: pd.DataFrame, pop: Dict, output_dir: str):
    """Generate high-resolution (300 DPI) publication-grade charts."""
    os.makedirs(output_dir, exist_ok=True)
    sns.set_theme(style="whitegrid", font_scale=1.0)
    plt.rcParams["font.sans-serif"] = "Helvetica, Arial, sans-serif"

    # --- Chart 1: Borough Distribution ---
    b_df = pd.DataFrame([
        {"borough": b, "count": c, "pct": pop["borough_percentages"][b]}
        for b, c in pop["borough_counts"].items()
        if b != "Unspecified"
    ]).sort_values(by="count", ascending=False)

    plt.figure(figsize=(10, 5.5), dpi=300)
    colors = ["#1f77b4" if b in ["MANHATTAN", "BROOKLYN", "BRONX"] else "#aec7e8" for b in b_df["borough"]]
    bars = plt.bar(b_df["borough"], b_df["count"] / 1000, color=colors, edgecolor="#333333", linewidth=0.8)
    plt.title("NYC 311 Noise Complaints by Borough (2023–2024 Population)\nManhattan, Brooklyn & Bronx Drive 77.8% of Volume", fontsize=13, fontweight="bold", pad=12)
    plt.ylabel("Complaints (Thousands)", fontsize=11, fontweight="bold")
    plt.xlabel("Borough", fontsize=11, fontweight="bold")

    for bar, pct in zip(bars, b_df["pct"]):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 5, f"{yval:.1f}k\n({pct:.1f}%)", ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.ylim(0, max(b_df["count"] / 1000) * 1.15)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "borough_distribution.png"), dpi=300)
    plt.close()
    logger.info("Saved borough_distribution.png")

    # --- Chart 2: Top 10 ZIP Codes ---
    valid_zips = df.dropna(subset=["clean_zip"])
    top10_zips = valid_zips["clean_zip"].value_counts().head(10).reset_index()
    top10_zips.columns = ["zip", "count"]
    top10_zips["pct"] = (top10_zips["count"] / len(valid_zips)) * 100

    plt.figure(figsize=(11, 5.5), dpi=300)
    bars2 = plt.bar(top10_zips["zip"].astype(str), top10_zips["count"], color="#2ca02c", edgecolor="#1b611b", linewidth=0.8)
    plt.title(f"Top 10 Hotspot ZIP Codes (Multi-Season Complete-Week Sample)\nCombined Top 10 Account for {top10_zips['pct'].sum():.1f}% of Volume", fontsize=13, fontweight="bold", pad=12)
    plt.ylabel("Complaint Count", fontsize=11, fontweight="bold")
    plt.xlabel("Postal ZIP Code", fontsize=11, fontweight="bold")

    for bar, pct in zip(bars2, top10_zips["pct"]):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 15, f"{yval}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=9)

    plt.ylim(0, max(top10_zips["count"]) * 1.15)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "top10_zip_codes.png"), dpi=300)
    plt.close()
    logger.info("Saved top10_zip_codes.png")

    # --- Chart 3: Day vs. Hour Heatmap ---
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heat_data = df.groupby(["day_name", "hour"]).size().unstack().reindex(day_order)

    plt.figure(figsize=(13, 6), dpi=300)
    sns.heatmap(heat_data, cmap="YlOrRd", cbar_kws={"label": "Complaint Count"}, linewidths=0.5, linecolor="#eeeeee")
    plt.title("NYC 311 Noise Complaint Temporal Density (168-Hour Profile)\nSurges Friday–Sunday Evenings (8:00 PM – 2:00 AM)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Hour of Day (0 = Midnight, 12 = Noon, 23 = 11 PM)", fontsize=11, fontweight="bold")
    plt.ylabel("Day of Week", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "hourly_noise_heatmap.png"), dpi=300)
    plt.close()
    logger.info("Saved hourly_noise_heatmap.png")

    # --- Chart 4: Target Problem Pool vs Prevented Scenarios ---
    # Joint pool = 67,556 complaints/yr on 2-year average (or 77,713 on 828k baseline)
    joint_target_pool = pop["joint_intersection_metrics"]["annualized_joint_8pm_2am_volume"]
    naive_target_pool = pop["joint_intersection_metrics"]["illustrative_84k_reconstruction"]["calculated_target_pool"]

    labels = [
        "Historical Coursework Pool\n(Naive ~84k Model)",
        "Empirical Joint Pool\n(8 PM–2 AM Target)",
        "25% Efficacy Pilot\n(Assumed Moderate)",
        "35% Efficacy Pilot\n(Assumed High)",
        "50% Efficacy Pilot\n(Assumed Ceiling)",
    ]
    vals = [
        naive_target_pool,
        joint_target_pool,
        joint_target_pool * 0.25,
        joint_target_pool * 0.35,
        joint_target_pool * 0.50,
    ]
    bar_colors = ["#7f7f7f", "#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"]

    plt.figure(figsize=(12, 6), dpi=300)
    bars4 = plt.bar(labels, [v / 1000 for v in vals], color=bar_colors, edgecolor="#333333", linewidth=0.8)
    plt.title("NYC Noise Pilot: Target Problem Pool vs. Projected Complaint Reductions\nSeparating the Targeted Problem Population from Prevented Complaints", fontsize=13, fontweight="bold", pad=12)
    plt.ylabel("Complaints (Thousands / Year)", fontsize=11, fontweight="bold")

    for bar, val in zip(bars4, vals):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 1.2, f"{val:,.0f}/yr\n({yval:.1f}k)", ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.ylim(0, max(vals) / 1000 * 1.18)
    plt.axhline(0, color="black", linewidth=0.8)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "pilot_scenario_projection.png"), dpi=300)
    plt.close()
    logger.info("Saved pilot_scenario_projection.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NYC 311 Noise Data Processing Pipeline")
    parser.add_argument("--download-sample", action="store_true", help="Download 4 complete calendar weeks")
    parser.add_argument("--generate-charts", action="store_true", help="Regenerate all 4 PNG charts in visuals/")
    args = parser.parse_args()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sample_path = os.path.join(project_root, "data", "sample_nyc_noise_50k.csv")
    metadata_path = os.path.join(project_root, "data", "summary_metrics_2023_2024.json")
    visuals_dir = os.path.join(project_root, "visuals")

    if args.download_sample:
        download_stratified_sample(sample_path)

    if args.generate_charts:
        with open(metadata_path, "r") as f:
            pop_meta = json.load(f)
        sample_df = pd.read_csv(sample_path)
        sample_df = clean_nyc_noise_data(sample_df)
        generate_all_visualizations(sample_df, pop_meta, visuals_dir)

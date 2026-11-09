"""NYC 311 Noise Analytics - Data Processing and Extraction Pipeline.

This module provides reproducible data extraction, cleaning, and aggregation
utilities for NYC 311 noise complaints (2023-2024) from the NYC Open Data
Socrata API (Dataset ID: erm2-nwe9).
"""

import argparse
import json
import logging
import os
from typing import Dict, List, Optional, Tuple
import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

NYC_311_ENDPOINT = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

# Verified Population Baseline from NYC Open Data (2023-2024)
VERIFIED_POPULATION_METRICS = {
    "dataset_source": "NYC Open Data (erm2-nwe9)",
    "date_range": "2023-01-01 to 2024-12-31",
    "total_noise_complaints": 1439558,
    "borough_counts": {
        "MANHATTAN": 387561,
        "BROOKLYN": 377416,
        "BRONX": 354909,
        "QUEENS": 287977,
        "STATEN ISLAND": 31157,
        "Unspecified": 538,
    },
    "borough_percentages": {
        "MANHATTAN": 26.92,
        "BROOKLYN": 26.22,
        "BRONX": 24.65,
        "QUEENS": 20.00,
        "STATEN ISLAND": 2.16,
        "Unspecified": 0.04,
    },
    "top_3_boroughs_combined": {
        "boroughs": ["MANHATTAN", "BROOKLYN", "BRONX"],
        "count": 1119886,
        "percentage": 77.79,
    },
    "top_2_boroughs_combined": {
        "boroughs": ["MANHATTAN", "BROOKLYN"],
        "count": 764977,
        "percentage": 53.14,
    },
    "complaint_types": {
        "Noise - Residential": 677749,
        "Noise - Street/Sidewalk": 310450,
        "Noise - Commercial": 136096,
        "Noise": 108234,
        "Noise - Vehicle": 100090,
        "Noise - Helicopter": 87813,
        "Noise - Park": 16585,
        "Noise - House of Worship": 2541,
    },
}


def download_stratified_sample(
    output_csv_path: str, records_per_quarter: int = 6250
) -> pd.DataFrame:
    """Download a balanced, multi-season stratified sample across 2023-2024.

    Pulls representative weekly cohorts across Winter, Spring, Summer, and Fall
    for both calendar years to prevent seasonal bias while keeping the dataset
    compact (<10MB) and fast to run locally.
    """
    quarters: List[Tuple[str, str]] = [
        ("2023-01-15", "2023-01-22"),
        ("2023-04-15", "2023-04-22"),
        ("2023-07-15", "2023-07-22"),
        ("2023-10-15", "2023-10-22"),
        ("2024-01-15", "2024-01-22"),
        ("2024-04-15", "2024-04-22"),
        ("2024-07-15", "2024-07-22"),
        ("2024-10-15", "2024-10-22"),
    ]

    selected_fields = (
        "unique_key,created_date,closed_date,agency,complaint_type,descriptor,"
        "location_type,incident_zip,incident_address,city,borough,latitude,longitude"
    )

    records: List[Dict] = []
    logger.info("Initiating download of stratified sample (%d per quarter)...", records_per_quarter)

    for start_dt, end_dt in quarters:
        params = {
            "$select": selected_fields,
            "$where": (
                f"created_date >= '{start_dt}T00:00:00' and "
                f"created_date < '{end_dt}T00:00:00' and "
                "complaint_type like '%Noise%'"
            ),
            "$limit": records_per_quarter,
        }
        resp = requests.get(NYC_311_ENDPOINT, params=params, timeout=30)
        resp.raise_for_status()
        batch = resp.json()
        records.extend(batch)
        logger.info("Retrieved %d records for interval %s to %s", len(batch), start_dt, end_dt)

    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df.to_csv(output_csv_path, index=False)
    logger.info("Saved %d total records to %s", len(df), output_csv_path)
    return df


def clean_nyc_noise_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich raw NYC 311 noise complaint records.

    - Parses timestamp columns (`created_date`, `closed_date`)
    - Derives temporal features: hour, day of week, month, year, weekend indicator
    - Standardizes borough casing and cleans ZIP codes
    - Calculates resolution duration where valid closed dates exist
    """
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
    df["is_overnight_peak"] = df["hour"].isin([21, 22, 23, 0])  # 9 PM - 1 AM window

    # Spatial cleaning
    df["borough"] = df["borough"].astype(str).str.strip().str.upper()
    df.loc[df["borough"].isin(["", "NAN", "NONE", "UNSPECIFIED"]), "borough"] = "UNSPECIFIED"

    if "incident_zip" in df.columns:
        # Standardize 5-digit ZIP format
        df["clean_zip"] = (
            df["incident_zip"].astype(str).str.extract(r"^(\d{5})")[0]
        )

    # Clean numeric coordinates
    for col in ["latitude", "longitude"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def calculate_borough_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate complaint volume and percentage share by NYC borough."""
    summary = (
        df.groupby("borough")
        .size()
        .reset_index(name="complaint_count")
        .sort_values(by="complaint_count", ascending=False)
    )
    total = summary["complaint_count"].sum()
    summary["percentage"] = (summary["complaint_count"] / total) * 100
    summary["cumulative_percentage"] = summary["percentage"].cumsum()
    return summary


def calculate_top_zip_distribution(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Identify top noise complaint ZIP codes and their Pareto concentration."""
    valid_zips = df.dropna(subset=["clean_zip"])
    total_valid = len(valid_zips)

    zip_summary = (
        valid_zips.groupby(["clean_zip", "borough"])
        .size()
        .reset_index(name="complaint_count")
        .sort_values(by="complaint_count", ascending=False)
    )
    zip_summary["percentage"] = (zip_summary["complaint_count"] / total_valid) * 100
    zip_summary["cumulative_percentage"] = zip_summary["percentage"].cumsum()
    return zip_summary.head(top_n)


def model_pilot_scenario(
    annual_baseline: int = 828000,
    top10_zip_share: float = 0.20,
    night_window_share: float = 0.51,
    targeted_reduction_rate: float = 0.50,
) -> Dict[str, float]:
    """Model the scenario-based complaint reduction for the Quiet Force pilot.

    NOTE: This is strictly an operational projection model, NOT an observed
    historical outcome.

    Parameters:
    - annual_baseline: Projected annual complaints without intervention (~828,000)
    - top10_zip_share: Fraction of citywide complaints in top 10 ZIPs (~20%)
    - night_window_share: Fraction of complaints occurring during 9 PM - 1 AM (~51%)
    - targeted_reduction_rate: Assumed enforcement & de-escalation efficacy (50%)
    """
    target_pool = annual_baseline * top10_zip_share * night_window_share
    projected_reduction = target_pool * targeted_reduction_rate
    projected_post_pilot = annual_baseline - projected_reduction
    citywide_reduction_pct = (projected_reduction / annual_baseline) * 100

    return {
        "annual_baseline": annual_baseline,
        "target_pool_complaints": round(target_pool, 0),
        "targeted_reduction_rate_pct": targeted_reduction_rate * 100,
        "projected_annual_reduction": round(projected_reduction, 0),
        "projected_post_pilot_total": round(projected_post_pilot, 0),
        "citywide_reduction_pct": round(citywide_reduction_pct, 2),
    }


def save_summary_metadata(output_json_path: str):
    """Write verified population figures and metadata to JSON."""
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(VERIFIED_POPULATION_METRICS, f, indent=2)
    logger.info("Saved verified population metadata to %s", output_json_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NYC 311 Noise Data Processing")
    parser.add_argument(
        "--download-sample",
        action="store_true",
        help="Download 50,000 multi-season sample from NYC Open Data",
    )
    parser.add_argument(
        "--save-metadata",
        action="store_true",
        help="Save verified citywide 1.44M population metrics JSON",
    )
    args = parser.parse_args()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sample_path = os.path.join(project_root, "data", "sample_nyc_noise_50k.csv")
    metadata_path = os.path.join(project_root, "data", "summary_metrics_2023_2024.json")

    if args.save_metadata or not os.path.exists(metadata_path):
        save_summary_metadata(metadata_path)

    if args.download_sample:
        download_stratified_sample(sample_path)

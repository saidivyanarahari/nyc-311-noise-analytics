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


def regenerate_and_save_population_metadata(output_json_path: str):
    """Regenerate complete population metrics live from documented Socrata API queries."""
    logger.info("Querying Socrata API live for borough metrics...")
    borough_counts = fetch_population_borough_metrics()
    total_complaints = sum(borough_counts.values())

    logger.info("Querying Socrata API live for complaint type breakdown...")
    complaint_types = fetch_population_complaint_types()

    logger.info("Querying Socrata API live for day-of-week distribution...")
    dow_counts = fetch_population_dow_metrics()

    logger.info("Querying Socrata API live for hourly distribution...")
    hourly_counts = fetch_population_hourly_metrics()

    logger.info("Querying Socrata API live for top residential ZIP codes...")
    top_res_zips = fetch_population_residential_top_zips(10)
    top_res_sum = sum(z["count"] for z in top_res_zips)
    res_total = complaint_types.get("Noise - Residential", 677749)

    # Calculate exact shares
    borough_percentages = {
        b: round((count / total_complaints) * 100, 2)
        for b, count in borough_counts.items()
    }
    top_3_sum = (
        borough_counts.get("MANHATTAN", 0)
        + borough_counts.get("BROOKLYN", 0)
        + borough_counts.get("BRONX", 0)
    )
    top_2_sum = borough_counts.get("MANHATTAN", 0) + borough_counts.get("BROOKLYN", 0)

    # Core 9 PM - 1 AM hours (21, 22, 23, 0)
    h_9_1 = sum(hourly_counts.get(h, 0) for h in [21, 22, 23, 0])
    # Evening 8 PM - 2 AM hours (20, 21, 22, 23, 0, 1)
    h_8_2 = sum(hourly_counts.get(h, 0) for h in [20, 21, 22, 23, 0, 1])
    # Ground zero 10 PM - Midnight hours (22, 23)
    h_10_12 = sum(hourly_counts.get(h, 0) for h in [22, 23])

    # Day of week surges
    mon_thu_avg = (
        dow_counts.get("Monday", 0)
        + dow_counts.get("Tuesday", 0)
        + dow_counts.get("Wednesday", 0)
        + dow_counts.get("Thursday", 0)
    ) / 4.0
    fri_surge_vs_thu = (
        (dow_counts.get("Friday", 0) / dow_counts.get("Thursday", 1)) - 1
    ) * 100
    sat_sun_avg = (dow_counts.get("Saturday", 0) + dow_counts.get("Sunday", 0)) / 2.0
    sat_sun_surge_vs_wkday = ((sat_sun_avg / mon_thu_avg) - 1) * 100

    metadata = {
        "dataset_source": "NYC Open Data (erm2-nwe9) via Socrata SoQL API",
        "date_range": "2023-01-01 to 2024-12-31",
        "total_noise_complaints": total_complaints,
        "borough_counts": borough_counts,
        "borough_percentages": borough_percentages,
        "top_3_boroughs_combined": {
            "boroughs": ["MANHATTAN", "BROOKLYN", "BRONX"],
            "count": top_3_sum,
            "percentage": round((top_3_sum / total_complaints) * 100, 2),
        },
        "top_2_boroughs_combined": {
            "boroughs": ["MANHATTAN", "BROOKLYN"],
            "count": top_2_sum,
            "percentage": round((top_2_sum / total_complaints) * 100, 2),
        },
        "complaint_types": complaint_types,
        "day_of_week_counts": dow_counts,
        "day_of_week_metrics": {
            "mon_thu_daily_average": round(mon_thu_avg, 2),
            "friday_daily_volume": dow_counts.get("Friday", 0),
            "thursday_daily_volume": dow_counts.get("Thursday", 0),
            "friday_vs_thursday_daily_surge_pct": round(fri_surge_vs_thu, 2),
            "sat_sun_daily_average": round(sat_sun_avg, 2),
            "sat_sun_surge_vs_weekday_avg_pct": round(sat_sun_surge_vs_wkday, 2),
        },
        "hourly_distribution_all_days": {
            "ground_zero_10pm_to_midnight_count": h_10_12,
            "ground_zero_10pm_to_midnight_pct": round(
                (h_10_12 / total_complaints) * 100, 2
            ),
            "core_window_9pm_to_1am_count": h_9_1,
            "core_window_9pm_to_1am_pct": round((h_9_1 / total_complaints) * 100, 2),
            "evening_window_8pm_to_2am_count": h_8_2,
            "evening_window_8pm_to_2am_pct": round((h_8_2 / total_complaints) * 100, 2),
        },
        "top_residential_zip_codes": {
            "top_10_zips": top_res_zips,
            "top_10_count": top_res_sum,
            "residential_population_total": res_total,
            "residential_top_10_share_pct": round((top_res_sum / res_total) * 100, 2),
        },
    }

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Successfully updated %s from live API queries.", output_json_path)
    return metadata


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
        # Standardize 5-digit ZIP format
        df["clean_zip"] = df["incident_zip"].astype(str).str.extract(r"^(\d{5})")[0]

    # Clean numeric coordinates
    for col in ["latitude", "longitude"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def calculate_sample_zip_metrics(df: pd.DataFrame, top_n: int = 10) -> Dict[str, any]:
    """Calculate ZIP-code concentration metrics with explicit denominators."""
    total_sample = len(df)
    valid_zip_df = df.dropna(subset=["clean_zip"])
    total_valid_zips = len(valid_zip_df)

    top_zips = valid_zip_df["clean_zip"].value_counts().head(top_n)
    top_n_sum = top_zips.sum()

    return {
        "total_sample_records": total_sample,
        "valid_zip_records": total_valid_zips,
        "valid_zip_rate_pct": round((total_valid_zips / total_sample) * 100, 2),
        "top_n": top_n,
        "top_n_sum": int(top_n_sum),
        "share_of_valid_zips_pct": round((top_n_sum / total_valid_zips) * 100, 2),
        "share_of_all_records_pct": round((top_n_sum / total_sample) * 100, 2),
        "top_zip_counts": top_zips.to_dict(),
    }


def model_pilot_sensitivity(
    annual_baseline: int = 828000,
    top10_zip_share: float = 0.20,
    evening_window_share: float = 0.507,
    efficacy_rates: Optional[List[float]] = None,
) -> Dict[str, any]:
    """Model targeted pilot scenarios and evaluate sensitivity parameters.

    NOTE: The 84,000 figure is retained as an illustrative scenario representing
    the aggregate complaint volume occurring in the targeted hotspot window.
    Real-world prevented complaints depend on the assumed intervention efficacy.
    """
    if efficacy_rates is None:
        efficacy_rates = [0.15, 0.25, 0.35, 0.50, 1.00]

    target_pool_annual = annual_baseline * top10_zip_share * evening_window_share

    scenarios = []
    for eff in efficacy_rates:
        prevented = target_pool_annual * eff
        scenarios.append({
            "efficacy_rate_pct": round(eff * 100, 1),
            "prevented_complaints": int(round(prevented, 0)),
            "post_pilot_complaints": int(round(annual_baseline - prevented, 0)),
            "citywide_reduction_pct": round((prevented / annual_baseline) * 100, 2),
        })

    return {
        "annual_baseline": annual_baseline,
        "top10_zip_share_assumption": top10_zip_share,
        "evening_window_share_assumption": evening_window_share,
        "targeted_pool_volume": int(round(target_pool_annual, 0)),
        "illustrative_deck_upper_bound": 84000,
        "scenarios": scenarios,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NYC 311 Noise Data Processing Pipeline")
    parser.add_argument(
        "--download-sample",
        action="store_true",
        help="Download 50,000 multi-season sample from NYC Open Data",
    )
    parser.add_argument(
        "--regenerate-population-metrics",
        action="store_true",
        help="Execute live Socrata SoQL API queries to regenerate data/summary_metrics_2023_2024.json",
    )
    args = parser.parse_args()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sample_path = os.path.join(project_root, "data", "sample_nyc_noise_50k.csv")
    metadata_path = os.path.join(project_root, "data", "summary_metrics_2023_2024.json")

    if args.regenerate_population_metrics:
        regenerate_and_save_population_metadata(metadata_path)

    if args.download_sample:
        download_stratified_sample(sample_path)

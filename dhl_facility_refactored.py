#!/usr/bin/env python3
"""DHL facilities cleaning and exploratory analysis pipeline."""

import argparse
import os
import re
from pathlib import Path

# Ensure matplotlib has a writable config/cache path in restricted environments.
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean and analyze DHL facilities CSV.")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "outputs"),
        help="Directory for cleaned data and charts",
    )
    return parser.parse_args()


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return pd.read_csv(path)


def derive_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Normalize facility category if missing.
    if "LOCATION_CATEGORY" not in df.columns:
        if "LOCATION_TH" in df.columns:
            df["LOCATION_CATEGORY"] = df["LOCATION_TH"]
        else:
            df["LOCATION_CATEGORY"] = "Unknown"

    # Normalize Saturday pickup flag if missing.
    if "HAS_SATURDAY_PICKUP" not in df.columns:
        src = df.get("LAST_PICKUP", pd.Series(["" for _ in range(len(df))], index=df.index)).astype(str).str.lower()
        df["HAS_SATURDAY_PICKUP"] = src.str.contains("sat") & ~src.str.contains("no sat")

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()

    # Standardize placeholder missing marker.
    object_cols = cleaned.select_dtypes(include=["object"]).columns
    for col in object_cols:
        cleaned[col] = cleaned[col].replace("NOT AVAILABLE", pd.NA)

    # Remove mostly-empty column and rows with missing core address.
    if "ADDRESS2" in cleaned.columns:
        cleaned = cleaned.drop(columns=["ADDRESS2"])
    if "ADDRESS" in cleaned.columns:
        cleaned = cleaned.dropna(subset=["ADDRESS"])

    # Extract first pickup time token from text and convert to datetime.
    if "LAST_PICKUP" in cleaned.columns:
        time_pattern = r"(\d{1,2}:\d{2}\s?(?:AM|PM|am|pm))"
        extracted = cleaned["LAST_PICKUP"].astype(str).str.extract(time_pattern, flags=re.IGNORECASE)[0]
        cleaned["LAST_PICKUP_TIME"] = pd.to_datetime(extracted, format="%I:%M %p", errors="coerce")

    return derive_columns(cleaned)


def save_outputs(df: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    cleaned_csv = output_dir / "dhl_facilities_cleaned_for_tableau.csv"
    missing_csv = output_dir / "missing_values_summary.csv"
    chart_cat = output_dir / "facility_category_distribution.png"
    chart_ty = output_dir / "facility_type_distribution.png"
    chart_pickup = output_dir / "last_pickup_distribution.png"

    df.to_csv(cleaned_csv, index=False)

    missing = pd.DataFrame(
        {
            "missing_count": df.isnull().sum(),
            "missing_pct": (df.isnull().sum() / len(df)) * 100,
        }
    ).sort_values("missing_pct", ascending=False)
    missing.to_csv(missing_csv)

    sns.set_theme(style="whitegrid")

    if "LOCATION_CATEGORY" in df.columns:
        plt.figure(figsize=(10, 6))
        order = df["LOCATION_CATEGORY"].value_counts().index
        sns.countplot(data=df, x="LOCATION_CATEGORY", order=order)
        plt.title("Distribution of Facilities by Category")
        plt.xlabel("Category")
        plt.ylabel("Count")
        plt.xticks(rotation=35, ha="right")
        plt.tight_layout()
        plt.savefig(chart_cat, dpi=150)
        plt.close()

    if "LOCATION_TY" in df.columns:
        plt.figure(figsize=(12, 6))
        order = df["LOCATION_TY"].value_counts().index
        sns.countplot(data=df, x="LOCATION_TY", order=order)
        plt.title("Distribution of Facilities by Location Type")
        plt.xlabel("Location Type")
        plt.ylabel("Count")
        plt.xticks(rotation=55, ha="right")
        plt.tight_layout()
        plt.savefig(chart_ty, dpi=150)
        plt.close()

    if "LAST_PICKUP_TIME" in df.columns:
        valid = df["LAST_PICKUP_TIME"].dropna()
        if not valid.empty:
            pickup_seconds = valid.dt.hour * 3600 + valid.dt.minute * 60 + valid.dt.second
            plt.figure(figsize=(10, 6))
            sns.histplot(pickup_seconds, bins=40, kde=True)
            max_seconds = int(pickup_seconds.max())
            ticks = list(range(0, max_seconds + 3600, 3600))
            labels = [f"{t // 3600:02d}:{(t % 3600) // 60:02d}" for t in ticks]
            plt.xticks(ticks, labels, rotation=35, ha="right")
            plt.title("Distribution of Last Pickup Times")
            plt.xlabel("Time of Day")
            plt.ylabel("Count")
            plt.tight_layout()
            plt.savefig(chart_pickup, dpi=150)
            plt.close()

    print("=== Export Complete ===")
    print(f"Rows: {len(df):,}")
    print(f"Clean CSV: {cleaned_csv}")
    print(f"Missing summary: {missing_csv}")
    print(f"Charts: {chart_cat}, {chart_ty}, {chart_pickup}")



def print_quality_summary(df: pd.DataFrame) -> None:
    duplicate_rows = df.duplicated().sum()
    sat_rate = float(df["HAS_SATURDAY_PICKUP"].mean() * 100) if "HAS_SATURDAY_PICKUP" in df.columns else 0.0
    print("=== Data Quality ===")
    print(f"Columns: {df.shape[1]}")
    print(f"Rows: {df.shape[0]:,}")
    print(f"Duplicate rows: {duplicate_rows}")
    print(f"Saturday pickup rate: {sat_rate:.2f}%")



def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    df = load_data(input_path)
    cleaned = clean_data(df)
    print_quality_summary(cleaned)
    save_outputs(cleaned, output_dir)


if __name__ == "__main__":
    main()

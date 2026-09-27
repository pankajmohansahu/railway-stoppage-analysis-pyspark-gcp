"""
OPPE 1 Exam - Train Stoppage Analysis
Section A + B: Stop Duration Statistics & Station Load Analysis
Author: Roll 21f2001203
Date: 2026-04-04
"""

import argparse
import csv
from io import StringIO
from google.cloud import storage
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# ═══════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════
BUCKET = "gs://iitm-ibd-oppe1-21f2001203"
INPUT_PATH = f"{BUCKET}/data/Train_details_22122017.csv"
OUTPUT_PATH = f"{BUCKET}/output/train_analysis_results.csv"


def parse_time_to_minutes(time_str):
    """Convert HH:MM:SS to minutes since midnight. Handle edge cases."""
    if not time_str or time_str.strip() == "" or time_str == "00:00:00":
        return None
    try:
        parts = time_str.strip().split(":")
        if len(parts) != 3:
            return None
        hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
        return hours * 60 + minutes + seconds / 60
    except:
        return None


def calculate_stop_duration(arr_str, dep_str):
    """
    Calculate stop duration in minutes.
    Handle midnight crossing (if dep < arr, it's next day).
    """
    arr_min = parse_time_to_minutes(arr_str)
    dep_min = parse_time_to_minutes(dep_str)

    if arr_min is None or dep_min is None:
        return None

    if arr_min == 0:
        return 0

    if dep_min >= arr_min:
        return dep_min - arr_min

    return (24 * 60 - arr_min) + dep_min


def main(input_path, output_path):

    spark = (
        SparkSession.builder
        .appName("TrainStoppageAnalysis_OPPE1")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    print("\n" + "="*80)
    print("RAILWAY STOPPAGE ANALYSIS - SECTION A & B")
    print("="*80)

    # ─────────────────────────────────────────────────────────────────────────
    # LOAD DATA
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[STEP 1] Loading data from GCS...")
    df = spark.read.csv(input_path, header=True, inferSchema=True)

    print("Data loaded successfully.")

    # ─────────────────────────────────────────────────────────────────────────
    # DATA CLEANING & STOP DURATION CALCULATION
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[STEP 2] Calculating stop durations...")

    calculate_stop_duration_udf = F.udf(calculate_stop_duration, returnType="double")

    df_with_duration = df.withColumn(
        "stop_duration_minutes",
        calculate_stop_duration_udf(F.col("Arrival time"), F.col("Departure Time"))
    )

    df_clean = df_with_duration.filter(F.col("stop_duration_minutes").isNotNull()).cache()

    print("Stop duration calculations complete.")

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION A: STOP DURATION STATISTICS
    # ═════════════════════════════════════════════════════════════════════════

    print("\n" + "="*80)
    print("SECTION A: STOP DURATION STATISTICS")
    print("="*80)

    # ─────────────────────────────────────────────────────────────────────────
    # A1: Min, Max, Avg, 90th Percentile per station — collect ONCE to driver
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[A1] Computing Min/Max/Avg/90th Percentile per station...")

    section_a1_rows = (
        df_clean
        .groupBy("Station Name")
        .agg(
            F.min("stop_duration_minutes").alias("min_stop_duration"),
            F.max("stop_duration_minutes").alias("max_stop_duration"),
            F.round(F.avg("stop_duration_minutes"), 2).alias("avg_stop_duration"),
            F.round(F.percentile_approx("stop_duration_minutes", 0.9), 2).alias("p90_stop_duration"),
            F.count("*").alias("num_stoppages")
        )
        .orderBy(F.desc("num_stoppages"))
        .collect()  # Single collect — reused for top5 and CSV write
    )

    print(f"Stop Duration Statistics computed. Total stations: {len(section_a1_rows)}")

    # ─────────────────────────────────────────────────────────────────────────
    # A2: Top 5 stations by number of stoppages (from collected data, no re-compute)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[A2] Top 5 Stations by Number of Stoppages:")
    top5 = section_a1_rows[:5]
    for i, row in enumerate(top5, 1):
        print(f"  {i}. {row['Station Name']} — {row['num_stoppages']} stoppages")

    top5_station = section_a1_rows[0]["Station Name"]

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION B: STATION LOAD ANALYSIS
    # ═════════════════════════════════════════════════════════════════════════

    print("\n" + "="*80)
    print("SECTION B: STATION LOAD ANALYSIS")
    print("="*80)

    # ─────────────────────────────────────────────────────────────────────────
    # B1: Total & Avg stop duration per station
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[B1] Station Load Analysis:")

    section_b1 = (
        df_clean
        .groupBy("Station Name")
        .agg(
            F.round(F.sum("stop_duration_minutes"), 2).alias("total_stop_duration"),
            F.round(F.avg("stop_duration_minutes"), 2).alias("avg_stop_duration"),
            F.max("stop_duration_minutes").alias("max_stop_duration")
        )
    )

    print("\n[B1] Station Load Analysis computed.")

    # ─────────────────────────────────────────────────────────────────────────
    # B2: Stations where max > 3 × avg
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[B2] Stations where MAX > 3 × AVG (computing...)")

    section_b2_rows = (
        section_b1
        .filter(F.col("max_stop_duration") > 3 * F.col("avg_stop_duration"))
        .select("Station Name", "max_stop_duration", "avg_stop_duration")
        .withColumn("max_div_avg_ratio",
                    F.round(F.col("max_stop_duration") / F.col("avg_stop_duration"), 2))
        .orderBy(F.desc("max_div_avg_ratio"))
        .collect()
    )

    print(f"Anomalous stations (max > 3x avg): {len(section_b2_rows)}")

    # ─────────────────────────────────────────────────────────────────────────
    # B3: For TOP 1 station, max trains in 2-hour window
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[B3] Max Trains in 2-Hour Sliding Window:")
    print(f"\nAnalyzing Top station: {top5_station}")

    top_station_data = (
        df_clean
        .filter(F.col("Station Name") == top5_station)
        .select("Arrival time")
        .withColumn(
            "arrival_minutes",
            F.udf(parse_time_to_minutes, returnType="double")(F.col("Arrival time"))
        )
        .filter(F.col("arrival_minutes").isNotNull())
    )

    # Collect small dataset (735 rows) to driver and use Python two-pointer
    arrival_times = sorted([
        row["arrival_minutes"]
        for row in top_station_data.select("arrival_minutes").collect()
    ])

    print(f"Total stoppages at {top5_station}: {len(arrival_times)}")

    left = 0
    max_trains_in_window = 0
    for right in range(len(arrival_times)):
        while arrival_times[right] - arrival_times[left] > 120:
            left += 1
        max_trains_in_window = max(max_trains_in_window, right - left + 1)

    print(f"\nMaximum trains in any 2-hour window @ {top5_station}: {max_trains_in_window}")

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION C: WRITE RESULTS TO GCS (Python GCS client — no Spark write)
    # ═════════════════════════════════════════════════════════════════════════

    print("\n" + "="*80)
    print("WRITING RESULTS TO GCS")
    print("="*80)

    print(f"\n[STEP 3] Writing results to GCS: {output_path}")

    # Build CSV in memory from already-collected section_a1_rows
    fieldnames = ["Station Name", "min_stop_duration", "max_stop_duration",
                  "avg_stop_duration", "p90_stop_duration", "num_stoppages"]
    csv_buffer = StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in section_a1_rows:
        writer.writerow({k: row[k] for k in fieldnames})

    # Upload to GCS: strip gs:// and split bucket/path
    gcs_path = output_path.replace("gs://", "")
    bucket_name, blob_prefix = gcs_path.split("/", 1)
    blob_name = blob_prefix + "/part-00000.csv"

    storage_client = storage.Client()
    bucket_obj = storage_client.bucket(bucket_name)
    blob = bucket_obj.blob(blob_name)
    blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")

    print(f"Results written to: gs://{bucket_name}/{blob_name}")

    # ─────────────────────────────────────────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Top station by stoppages : {top5_station}")
    print(f"Max trains in 2-hr window: {max_trains_in_window}")
    print(f"Anomalous stations (B2)  : {len(section_b2_rows)}")
    print(f"Results written to       : gs://{bucket_name}/{blob_name}")
    print("="*80 + "\n")

    spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Stoppage Analysis - OPPE 1")
    parser.add_argument("--input_path", default=INPUT_PATH, help="GCS path to input CSV")
    parser.add_argument("--output_path", default=OUTPUT_PATH, help="GCS path for output CSV")

    args = parser.parse_args()
    main(args.input_path, args.output_path)

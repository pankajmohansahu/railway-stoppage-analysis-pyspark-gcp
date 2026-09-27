# OPPE 1 – Railway Stoppage Analysis
**Course:** JAN 2026 – Introduction to Big Data (IBD)
**Roll Number:** 21f2001203
**Exam Date:** 2026-04-04

---

## Problem Statement

Analyze train stoppage patterns and platform utilization at railway stations using arrival and departure data, using PySpark on Google Cloud Platform (GCP).

**Dataset:** `Train_details_22122017.csv`
**GCS Input Path:** `gs://iitm-ibd-oppe1-21f2001203/data/Train_details_22122017.csv`
**GCS Output Path:** `gs://iitm-ibd-oppe1-21f2001203/output/train_analysis_results.csv/part-00000.csv`

---

## GCP Setup

| Component | Details |
|---|---|
| Project | `project-399f087e-fef4-4831-b4e` |
| Region | `europe-west1` |
| Dataproc Cluster | `oppe1-cluster` |
| GCS Bucket | `iitm-ibd-oppe1-21f2001203` |
| Cloud Function | `process_results` |

---

## Files

| File | Purpose |
|---|---|
| `train_analysis_section_a_b.py` | PySpark job — Sections A, B, C (writes CSV to GCS) |
| `cloud_function.py` | Google Cloud Function — triggers on CSV upload, prints station with highest avg stop duration |

---

## Section A – Stop Duration Statistics

**Script:** `train_analysis_section_a_b.py`

### What it computes

For each station, using `groupBy("Station Name").agg(...)`:

| Metric | PySpark Function |
|---|---|
| Minimum stop duration | `F.min("stop_duration_minutes")` |
| Maximum stop duration | `F.max("stop_duration_minutes")` |
| Average stop duration | `F.avg("stop_duration_minutes")` |
| 90th percentile | `F.percentile_approx("stop_duration_minutes", 0.9)` |
| Number of stoppages | `F.count("*")` |

### Stop Duration Calculation

```python
def calculate_stop_duration(arr_str, dep_str):
    # Converts HH:MM:SS → minutes since midnight
    # Handles midnight crossing: if dep < arr, train departs next day
    if dep_min >= arr_min:
        return dep_min - arr_min
    return (24 * 60 - arr_min) + dep_min
```

Missing/malformed rows (where arrival or departure is null/empty/`00:00:00`) are excluded via `.filter(col("stop_duration_minutes").isNotNull())`.

### Results

- **Raw rows:** 186,124
- **Rows after cleaning:** 182,147
- **Top station by stoppages:** CHENNAI BEAC

---

## Section B – Station Load Analysis

### B1: Total and Average Stop Duration per Station

```python
df_clean.groupBy("Station Name").agg(
    F.sum("stop_duration_minutes"),   # total_stop_duration
    F.avg("stop_duration_minutes"),   # avg_stop_duration
    F.max("stop_duration_minutes")    # max_stop_duration
)
```

### B2: Anomalous Stations (max > 3 × avg)

```python
section_b1.filter(F.col("max_stop_duration") > 3 * F.col("avg_stop_duration"))
```

Stations where a single unusually long stop is far above the average — indicates outlier events (breakdowns, special halts, etc.).

### B3: Maximum Trains in Any 2-Hour Sliding Window (Top Station)

For **CHENNAI BEAC** (735 stoppages), arrival times are collected to the driver and a Python two-pointer algorithm finds the maximum number of trains present in any 2-hour window:

```python
arrival_times = sorted([...])  # collect 735 rows to driver
left = 0
max_trains_in_window = 0
for right in range(len(arrival_times)):
    while arrival_times[right] - arrival_times[left] > 120:
        left += 1
    max_trains_in_window = max(max_trains_in_window, right - left + 1)
```

**Result:** Maximum trains in any 2-hour window at CHENNAI BEAC = **112**

---

## Section C – Automation

### Writing Results to GCS

Instead of using `df.write.csv()` (which triggers a heavy Spark shuffle and caused OOM), results are written using the **Python GCS client** after a single `.collect()`:

```python
from google.cloud import storage
import csv
from io import StringIO

csv_buffer = StringIO()
writer = csv.DictWriter(csv_buffer, fieldnames=[...])
writer.writeheader()
for row in section_a1_rows:
    writer.writerow({k: row[k] for k in fieldnames})

blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")
```

### Google Cloud Function

**File:** `cloud_function.py`
**Trigger:** `google.storage.object.finalize` on bucket `iitm-ibd-oppe1-21f2001203`
**Entry point:** `process_results`

When the CSV is uploaded, the function:
1. Reads the file from GCS
2. Parses all rows
3. Finds and logs the station with the highest `avg_stop_duration`

```python
def process_results(event, context):
    bucket_name = event['bucket']
    file_name = event['name']
    # reads CSV, finds max avg_stop_duration station
    logger.info(f"Station with HIGHEST AVERAGE STOP DURATION: {station_with_max_avg}")
```

---

## How to Run

### Step 1 – Upload script to GCS

```bash
gsutil cp train_analysis_section_a_b.py gs://iitm-ibd-oppe1-21f2001203/scripts/
```

### Step 2 – Submit PySpark job on Dataproc

```bash
gcloud dataproc jobs submit pyspark \
  --cluster=oppe1-cluster \
  --region=europe-west1 \
  gs://iitm-ibd-oppe1-21f2001203/scripts/train_analysis_section_a_b.py
```

### Step 3 – Deploy Cloud Function

```bash
gcloud functions deploy process_results \
  --runtime python311 \
  --trigger-resource iitm-ibd-oppe1-21f2001203 \
  --trigger-event google.storage.object.finalize \
  --entry-point process_results \
  --region europe-west1 \
  --source gs://iitm-ibd-oppe1-21f2001203/scripts/ \
  --timeout 60s
```

### Step 4 – View Cloud Function logs

```bash
gcloud functions logs read process_results --region europe-west1 --limit 50
```

---

## Key Design Decisions

### Memory Management (OOM Prevention)

The Dataproc cluster had limited memory. Three strategies were used to prevent OOM:

1. **Cache `df_clean`** — `df_clean.cache()` prevents recomputing the 182K-row cleaned dataset on every action.
2. **Collect `section_a1` once** — The groupBy result is collected to the driver with `.collect()` and reused for both the top-5 query and the CSV write, avoiding a second expensive shuffle.
3. **Python GCS write instead of Spark write** — `df.write.csv()` with `coalesce(1)` was causing OOM by shuffling all aggregated data to a single partition. The Python GCS client writes the already-collected data directly.

### Two-Pointer for Sliding Window (B3)

The Spark `Window.orderBy(...).rangeBetween(0, 120)` function without `partitionBy` moves **all data to a single partition**, causing OOM even for 735 rows in the context of a memory-constrained cluster. The Python two-pointer on collected data is O(n) and uses negligible memory.

---

## Summary of Results

| Analysis | Result |
|---|---|
| Raw rows | 186,124 |
| Cleaned rows | 182,147 |
| Top station (most stoppages) | CHENNAI BEAC |
| Max trains in 2-hr window (CHENNAI BEAC) | 112 |
| Output CSV location | `gs://iitm-ibd-oppe1-21f2001203/output/train_analysis_results.csv/part-00000.csv` |

"""
OPPE 1 Exam - Section C: Cloud Function
Triggered on CSV upload - prints station with highest avg stop duration
"""

import logging
import csv
from io import StringIO
from google.cloud import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_results(event, context):
    """
    Cloud Function triggered when train_analysis_results.csv is uploaded.
    Reads the CSV and prints the station with highest average stop duration.
    """

    bucket_name = event['bucket']
    file_name = event['name']

    logger.info(f"Function triggered by upload of '{file_name}'")

    # Skip non-result files to prevent infinite loops
    if not 'train_analysis_results.csv' in file_name and not 'part-' in file_name:
        logger.info(f"Skipping file: {file_name}")
        return

    try:
        # Read the CSV from GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        logger.info(f"Reading file from GCS: gs://{bucket_name}/{file_name}")
        csv_content = blob.download_as_text(encoding='utf-8')

        # Parse CSV and find station with highest avg stop duration
        csv_reader = csv.DictReader(StringIO(csv_content))

        max_avg_stop_duration = -1
        station_with_max_avg = None

        for row in csv_reader:
            try:
                avg_stop_duration = float(row.get('avg_stop_duration', 0))
                if avg_stop_duration > max_avg_stop_duration:
                    max_avg_stop_duration = avg_stop_duration
                    station_with_max_avg = row.get('Station Name', 'Unknown')
            except (ValueError, TypeError):
                continue

        logger.info("=" * 80)
        logger.info("SECTION C: CLOUD FUNCTION RESULTS")
        logger.info("=" * 80)
        logger.info(f"\nStation with HIGHEST AVERAGE STOP DURATION:")
        logger.info(f"  Station Name: {station_with_max_avg}")
        logger.info(f"  Avg Stop Duration: {max_avg_stop_duration} minutes")
        logger.info("\n" + "=" * 80)
        logger.info("Cloud Function execution completed successfully!")
        logger.info("=" * 80 + "\n")

        return f"Success: {station_with_max_avg} has highest avg stop duration"

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise

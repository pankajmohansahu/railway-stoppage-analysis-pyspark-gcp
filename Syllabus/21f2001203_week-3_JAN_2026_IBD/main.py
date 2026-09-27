"""
Google Cloud Function — Longest Line Finder
============================================
IIT Madras | Intro to Big Data | Week 3 Graded Assignment 2

This function is triggered automatically when any file is uploaded to the
Google Cloud Storage (GCS) bucket. It:
  1. Downloads the uploaded text file
  2. Finds the line(s) with the maximum character length
  3. Logs the full analysis to Cloud Logging (visible in Logs Explorer)
  4. Saves a formatted result file back to the same GCS bucket

Deployment:
  Project : project-399f087e-fef4-4831-b4e
  Bucket  : iitm-ibd-21f2001203
  Region  : asia-east1
  Runtime : Python 3.11 (python311, Gen1 / --no-gen2)
  Trigger : google.storage.object.finalize
"""

import logging
from google.cloud import storage
from datetime import datetime


def find_longest_lines(file_content):
    """
    Identify the longest line(s) in the provided text content.

    The function splits the content into individual lines, determines the
    maximum character length, and collects all lines that share that maximum
    length (handles ties where multiple lines are equally long).

    Args:
        file_content (str): Raw text content of the uploaded file.

    Returns:
        tuple:
            longest_lines (list[str]): All lines with the maximum length.
            max_length    (int):       Number of characters in the longest line.
            total_lines   (int):       Total number of lines in the file.
    """
    lines = file_content.splitlines()

    if not lines:
        return [], 0, 0

    # Determine the maximum line length across all lines
    max_length = max(len(line) for line in lines)

    # Collect every line that matches the maximum length (handles ties)
    longest_lines = [line for line in lines if len(line) == max_length]

    return longest_lines, max_length, len(lines)


def process_file(event, context):
    """
    Entry point for the GCS-triggered Cloud Function.

    Called automatically by Cloud Functions whenever a file is uploaded
    (finalized) to the configured GCS bucket. Orchestrates the full
    pipeline: download → analyse → log → save result.

    Args:
        event   (dict): GCS event payload containing 'bucket' and 'name'.
        context (google.cloud.functions.Context): Metadata about the event.
    """
    # Configure logging so all logger.info() calls appear in Cloud Logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------ #
    # Step 1: Extract file metadata from the GCS event payload
    # ------------------------------------------------------------------ #
    bucket_name = event['bucket']   # e.g. "iitm-ibd-21f2001203"
    file_name   = event['name']     # e.g. "sample_input.txt"

    logger.info(f"Function triggered by upload of '{file_name}' "
                f"in bucket '{bucket_name}'")

    # ------------------------------------------------------------------ #
    # Step 2: Skip output files to prevent an infinite trigger loop
    # (When this function writes result_<file>, that upload would trigger
    #  the function again if we did not skip it here.)
    # ------------------------------------------------------------------ #
    if file_name.startswith('result_') or file_name.endswith('_result.txt'):
        logger.info(f"Skipping result file to avoid infinite loop: {file_name}")
        return

    # ------------------------------------------------------------------ #
    # Step 3: Initialise the GCS client and get a reference to the blob
    # ------------------------------------------------------------------ #
    storage_client = storage.Client()
    bucket         = storage_client.bucket(bucket_name)
    blob           = bucket.blob(file_name)

    try:
        # ------------------------------------------------------------------ #
        # Step 4: Download the file content from GCS as UTF-8 text
        # ------------------------------------------------------------------ #
        file_content = blob.download_as_text(encoding='utf-8')
        logger.info(f"Successfully downloaded file: {file_name}")

        # ------------------------------------------------------------------ #
        # Step 5: Analyse — find the longest line(s)
        # ------------------------------------------------------------------ #
        longest_lines, max_length, total_lines = find_longest_lines(file_content)

        # ------------------------------------------------------------------ #
        # Step 6: Log the analysis results to Cloud Logging
        # (These lines appear in Logs Explorer under the function's logs)
        # ------------------------------------------------------------------ #
        logger.info("=" * 80)
        logger.info(f"Analysis of file: {file_name}")
        logger.info(f"Total lines in file: {total_lines}")
        logger.info(f"Maximum line length: {max_length} characters")
        logger.info(f"Number of lines with maximum length: {len(longest_lines)}")
        logger.info("-" * 80)

        if longest_lines:
            logger.info("Longest line(s):")
            for idx, line in enumerate(longest_lines, 1):
                logger.info(f"Line {idx}: {line}")
        else:
            logger.info("No lines found in the file.")

        logger.info("=" * 80)

        # ------------------------------------------------------------------ #
        # Step 7: Build the formatted result file content
        # ------------------------------------------------------------------ #
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        result_content = (
            f"Analysis Results for: {file_name}\n"
            f"{'=' * 80}\n"
            f"Timestamp             : {timestamp}\n"
            f"Total lines in file   : {total_lines}\n"
            f"Maximum line length   : {max_length} characters\n"
            f"Number of longest lines: {len(longest_lines)}\n\n"
            f"{'=' * 80}\n"
            f"Longest Line(s):\n"
            f"{'=' * 80}\n\n"
        )

        if longest_lines:
            for idx, line in enumerate(longest_lines, 1):
                result_content += (
                    f"Line {idx} ({max_length} characters):\n"
                    f"{line}\n"
                    f"{'-' * 80}\n"
                )
        else:
            result_content += "No lines found in the file.\n"

        # ------------------------------------------------------------------ #
        # Step 8: Write the result file back to the same GCS bucket
        # The file is named "result_<original_filename>" so the skip logic
        # in Step 2 above prevents this upload from re-triggering the function.
        # ------------------------------------------------------------------ #
        result_file_name = f"result_{file_name}"
        result_blob = bucket.blob(result_file_name)
        result_blob.upload_from_string(result_content, content_type='text/plain')

        logger.info(f"Results saved to: gs://{bucket_name}/{result_file_name}")
        logger.info("Processing completed successfully!")

    except Exception as e:
        logger.error(f"Error processing file '{file_name}': {str(e)}")
        raise

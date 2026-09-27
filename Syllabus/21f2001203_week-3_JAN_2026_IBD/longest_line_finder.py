import subprocess
import os
from datetime import datetime

BUCKET_NAME = "iitm-ibd-21f2001203"
INPUT_FILE_NAME = "sample_input.txt"
OUTPUT_FILE_NAME = "longest_lines_output.txt"
LOCAL_INPUT_FILE = "downloaded_input.txt"
LOCAL_OUTPUT_FILE = "longest_lines_output.txt"

def download_file_from_gcs(bucket_name, source_blob_name, destination_file_name):
    cmd = f"gsutil cp gs://{bucket_name}/{source_blob_name} {destination_file_name}"
    result = subprocess.run(cmd, shell=True)
    if result.returncode == 0:
        print(f"File downloaded from gs://{bucket_name}/{source_blob_name}")
        return True
    else:
        print("Error downloading file.")
        return False

def find_longest_lines(file_path):
    longest_lines = []
    max_length = 0
    line_numbers = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, start=1):
            line_content = line.rstrip('\n\r')
            line_length = len(line_content)
            if line_length > max_length:
                max_length = line_length
                longest_lines = [line_content]
                line_numbers = [line_num]
            elif line_length == max_length and max_length > 0:
                longest_lines.append(line_content)
                line_numbers.append(line_num)
    return max_length, longest_lines, line_numbers

def create_output_file(max_length, longest_lines, line_numbers, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("LONGEST LINE(S) ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Maximum Line Length: {max_length} characters\n")
        f.write(f"Number of lines with maximum length: {len(longest_lines)}\n")
        f.write("\n" + "-" * 80 + "\n")
        f.write("LONGEST LINE(S):\n")
        f.write("-" * 80 + "\n\n")
        for idx, (line_num, line) in enumerate(zip(line_numbers, longest_lines), start=1):
            f.write(f"Line {line_num} (Length: {max_length}):\n")
            f.write(f"{line}\n\n")
    print(f"Output file created: {output_file_path}")

def upload_file_to_gcs(bucket_name, source_file_name, destination_blob_name):
    cmd = f"gsutil cp {source_file_name} gs://{bucket_name}/{destination_blob_name}"
    result = subprocess.run(cmd, shell=True)
    if result.returncode == 0:
        print(f"File uploaded to gs://{bucket_name}/{destination_blob_name}")
        return True
    else:
        print("Error uploading file.")
        return False

def main():
    print("=" * 80)
    print("WEEK 2 - GRADED ASSIGNMENT 1: LONGEST LINE FINDER")
    print("=" * 80)

    print("\n[Step 1] Downloading file from GCS...")
    download_file_from_gcs(BUCKET_NAME, INPUT_FILE_NAME, LOCAL_INPUT_FILE)

    print("\n[Step 2] Finding longest line(s)...")
    max_length, longest_lines, line_numbers = find_longest_lines(LOCAL_INPUT_FILE)

    print("\n" + "=" * 80)
    print("RESULTS: LONGEST LINE(S) IN FILE")
    print("=" * 80)
    print(f"Maximum Line Length: {max_length} characters")
    print(f"Number of lines with maximum length: {len(longest_lines)}")
    print("-" * 80)
    for idx, (line_num, line) in enumerate(zip(line_numbers, longest_lines), start=1):
        print(f"[{idx}] Line {line_num} (Length: {max_length}):")
        print(f"    {line}")
    print("=" * 80)

    print("\n[Step 3] Creating output file...")
    create_output_file(max_length, longest_lines, line_numbers, LOCAL_OUTPUT_FILE)

    print("\n[Step 4] Uploading output file to GCS...")
    upload_file_to_gcs(BUCKET_NAME, LOCAL_OUTPUT_FILE, OUTPUT_FILE_NAME)

    print("\nDONE! All steps completed successfully.")

if __name__ == "__main__":
    main()

# Week 3 - Graded Assignment 2: Longest Line Finder Cloud Function

## Overview

This Google Cloud Function automatically identifies the longest line(s) in text files uploaded to Google Cloud Storage (GCS). The function is triggered on every file upload, downloads and processes the file, logs the full analysis to Cloud Logging, and saves a formatted result file back to the same GCS bucket.

---

## Project Configuration (Actual Details Used)

| Parameter        | Value                                   |
|------------------|-----------------------------------------|
| **GCP Project ID**   | `project-399f087e-fef4-4831-b4e`    |
| **Project Number**   | `783203102174`                      |
| **GCS Bucket**       | `iitm-ibd-21f2001203`               |
| **Cloud Function**   | `process_file`                      |
| **Region**           | `asia-east1`                        |
| **Runtime**          | `python311` (Python 3.11)           |
| **Generation**       | Gen1 (`--no-gen2` required)         |
| **Memory**           | `256MB`                             |
| **Timeout**          | `60s`                               |
| **Trigger Event**    | `google.storage.object.finalize`    |
| **Entry Point**      | `process_file`                      |

> **Why `--no-gen2`?**  
> The GCS bucket `iitm-ibd-21f2001203` is in the **multi-region `asia`** location.  
> Gen2 Cloud Functions require Eventarc triggers, which do **not** support multi-region bucket locations.  
> Gen1 with `--no-gen2` and `--region asia-east1` works correctly for this bucket.

---

## Files in This Assignment

| File | Description |
|------|-------------|
| `main.py` | Cloud Function source code (entry point: `process_file`) |
| `requirements.txt` | Python package dependencies |
| `sample_input.txt` | 10-line test file used to trigger and verify the function |
| `deploy.sh` | Bash deployment script with all steps automated |
| `deploy.ps1` | PowerShell equivalent of `deploy.sh` for Windows |
| `VIDEO_DEMO_COMMANDS.txt` | Step-by-step commands reference for the screencast video |
| `README.md` | This file — full setup, deployment and submission guide |

---

## How the Code Works

### `find_longest_lines(file_content)`

```python
def find_longest_lines(file_content):
    lines = file_content.splitlines()
    if not lines:
        return [], 0, 0
    max_length = max(len(line) for line in lines)
    longest_lines = [line for line in lines if len(line) == max_length]
    return longest_lines, max_length, len(lines)
```

- Splits the raw file content into individual lines using `.splitlines()`
- Calculates the maximum character length across all lines
- Returns **all** lines that share that maximum length (handles ties correctly)
- Returns a tuple: `(longest_lines, max_length, total_lines)`

### `process_file(event, context)`

```python
def process_file(event, context):
    bucket_name = event['bucket']
    file_name   = event['name']
```

- **Triggered automatically** when any file is uploaded to the GCS bucket
- Extracts `bucket_name` and `file_name` from the GCS event payload
- **Skips files starting with `result_`** to avoid triggering itself infinitely
- Downloads the uploaded file content as UTF-8 text
- Calls `find_longest_lines()` to analyse the content
- Logs all results (`total lines`, `max length`, `longest line(s)`) to Cloud Logging
- Saves a formatted analysis report as `result_<original_filename>` back to the same GCS bucket

---

## Prerequisites

- Google Cloud Platform account with billing enabled
- GCS bucket `iitm-ibd-21f2001203` already created (multi-region: asia)
- Access to **Google Cloud Shell** (browser-based; no local install needed)
- gcloud CLI and gsutil are pre-installed in Cloud Shell

---

## One-Time Setup (Run ONCE Before First Deployment)

Open Google Cloud Shell and run these steps **once**. They persist across sessions.

### A. Set Project Permanently in Cloud Shell

```bash
# Add project config to shell startup file so it loads every session
echo 'gcloud config set project project-399f087e-fef4-4831-b4e --quiet' >> ~/.bashrc
source ~/.bashrc

# Verify correct project is active
gcloud config get-value project
# Expected: project-399f087e-fef4-4831-b4e
```

### B. Upload Assignment Files to Cloud Shell

1. In Cloud Shell, click the **⋮ (three-dot menu)** in the top-right toolbar
2. Select **Upload**
3. Upload all five files:
   - `main.py`
   - `requirements.txt`
   - `sample_input.txt`
   - `deploy.sh`
   - `deploy.ps1`
4. Files land in your home directory `~/`

### C. Organise Files into a Function Folder

```bash
# Create dedicated folder for the Cloud Function
mkdir -p ~/longest-line-function

# Move all files into it
mv ~/main.py ~/requirements.txt ~/sample_input.txt ~/deploy.sh ~/deploy.ps1 ~/longest-line-function/

# Confirm all files are present
ls -la ~/longest-line-function/
# Expected: deploy.ps1  deploy.sh  main.py  requirements.txt  sample_input.txt
```

### D. Grant Storage Permissions to the Function Service Account

```bash
# This allows the deployed function to read from and write to your bucket
gsutil iam ch \
  serviceAccount:project-399f087e-fef4-4831-b4e@appspot.gserviceaccount.com:roles/storage.objectAdmin \
  gs://iitm-ibd-21f2001203
```

---

## Deployment Steps (Run for Each Video/Demo Session)

### Step 1: Verify Project and Navigate to Folder

```bash
# Confirm the correct project is active
gcloud config get-value project
# Expected: project-399f087e-fef4-4831-b4e

# Navigate to the function directory
cd ~/longest-line-function/

# Confirm all files are present
ls -la
# Expected: deploy.ps1  deploy.sh  main.py  requirements.txt  sample_input.txt
```

### Step 2: Inspect the Code Files

```bash
# View the Cloud Function source code
cat main.py

# View the Python dependencies
cat requirements.txt

# View the sample input file
cat sample_input.txt
```

### Step 3: Enable Required GCP APIs

```bash
# Enable all APIs needed for Cloud Functions deployment
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable eventarc.googleapis.com
gcloud services enable logging.googleapis.com
```

### Step 4: Grant Required IAM Roles (Build Permissions)

```bash
PROJECT_ID="project-399f087e-fef4-4831-b4e"
PROJECT_NUMBER=783203102174

# Grant Cloud Build role to compute service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
  --role=roles/cloudbuild.builds.builder

# Grant Cloud Build role to Google APIs service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:${PROJECT_NUMBER}@cloudservices.gserviceaccount.com \
  --role=roles/cloudbuild.builds.builder
```

### Step 5: Deploy the Cloud Function

```bash
gcloud functions deploy process_file \
  --no-gen2 \
  --runtime python311 \
  --trigger-resource iitm-ibd-21f2001203 \
  --trigger-event google.storage.object.finalize \
  --entry-point process_file \
  --region asia-east1 \
  --memory 256MB \
  --timeout 60s
```

**Flag explanations:**

| Flag | Value | Purpose |
|------|-------|---------|
| `--no-gen2` | — | Forces Gen1 (required for multi-region bucket) |
| `--runtime` | `python311` | Python 3.11 runtime |
| `--trigger-resource` | `iitm-ibd-21f2001203` | GCS bucket to watch |
| `--trigger-event` | `google.storage.object.finalize` | Fires on every file upload |
| `--entry-point` | `process_file` | Python function to invoke |
| `--region` | `asia-east1` | Deployment region (compatible with asia multi-region bucket) |
| `--memory` | `256MB` | RAM allocated |
| `--timeout` | `60s` | Maximum execution duration |

Wait 1–2 minutes for deployment. Final output will show `status: ACTIVE`.

> **Alternative:** Use the provided deployment script for the same result:
> ```bash
> chmod +x ~/longest-line-function/deploy.sh
> bash ~/longest-line-function/deploy.sh
> ```

### Step 6: Confirm the Function is Deployed

```bash
# List all deployed Cloud Functions in the project
gcloud functions list

# Show detailed information about the function
gcloud functions describe process_file --region asia-east1
```

Expected output includes:
- `status: ACTIVE`
- `eventTrigger.resource: projects/_/buckets/iitm-ibd-21f2001203`
- `eventTrigger.eventType: google.storage.object.finalize`

---

## Testing the Function (Live Trigger Demo)

### Step 7: Clean the Bucket for a Fresh Demo

```bash
# Remove any leftover files for a clean state
gsutil rm -f gs://iitm-ibd-21f2001203/sample_input.txt
gsutil rm -f gs://iitm-ibd-21f2001203/result_sample_input.txt

# Confirm the bucket is empty
gsutil ls gs://iitm-ibd-21f2001203/
# Expected: (no output — bucket is empty)
```

### Step 8: Upload the Sample Input File (Triggers the Function!)

```bash
# This upload TRIGGERS the Cloud Function automatically
gsutil cp ~/longest-line-function/sample_input.txt gs://iitm-ibd-21f2001203/

# Confirm file was uploaded
gsutil ls gs://iitm-ibd-21f2001203/
# Expected: gs://iitm-ibd-21f2001203/sample_input.txt
```

### Step 9: Wait and Verify the Result File Appears

```bash
# Wait approximately 30 seconds for the function to execute, then check:
gsutil ls gs://iitm-ibd-21f2001203/
# Expected (BOTH files should now be present):
#   gs://iitm-ibd-21f2001203/sample_input.txt
#   gs://iitm-ibd-21f2001203/result_sample_input.txt
```

### Step 10: Download and Display the Result File

```bash
# Download the result file from GCS
gsutil cp gs://iitm-ibd-21f2001203/result_sample_input.txt ~/longest-line-function/

# Display its contents
cat ~/longest-line-function/result_sample_input.txt
```

---

## Viewing Logs

### Option A: Cloud Shell (CLI)

```bash
# Read the 50 most recent function execution logs
gcloud functions logs read process_file --region asia-east1 --limit 50
```

**What each log line means:**

| Log Message | Meaning |
|---|---|
| `Function execution started` | GCS upload successfully triggered the function |
| `Processing file: sample_input.txt` | Function identified the uploaded file |
| `Successfully downloaded file: sample_input.txt` | File content read from GCS |
| `Analysis of file: sample_input.txt` | Processing started |
| `Total lines in file: 10` | The sample input has 10 lines |
| `Maximum line length: 138 characters` | Length of the longest line |
| `Line 1: Data Science is an interdisciplinary...` | The actual longest line content |
| `Results saved to: gs://iitm-ibd-21f2001203/result_sample_input.txt` | Result saved back to GCS |
| `Function execution took ... ok` | Completed successfully |

### Option B: Cloud Console — Logs Explorer (for Screenshot)

1. Open this URL:  
   `https://console.cloud.google.com/logs/query;project=project-399f087e-fef4-4831-b4e`
2. Paste this query in the Logs Explorer query box:
   ```
   resource.type="cloud_function"
   resource.labels.function_name="process_file"
   resource.labels.region="asia-east1"
   ```
3. Click **Run Query**
4. Expand the successful execution log entry to see all `INFO` log lines
5. Take a **screenshot** showing the full expanded log output

---

## Expected Output for `sample_input.txt`

After the function executes, the result file `result_sample_input.txt` will contain:

```
Analysis Results for: sample_input.txt
================================================================================
Timestamp: <UTC timestamp>
Total lines in file: 10
Maximum line length: 138 characters
Number of lines with maximum length: 1

================================================================================
Longest Line(s):
================================================================================

Line 1 (138 characters):
Data Science is an interdisciplinary field that uses scientific methods, processes, algorithms and systems to extract knowledge from data.
```

Cloud Logging will show the same values:
- **Total lines:** 10
- **Maximum line length:** 138 characters
- **Longest line:** Line starting with `"Data Science is an interdisciplinary field..."`

---

## Architecture

```
┌─────────────────────┐         upload          ┌──────────────────────┐
│   Developer / User  │ ──── gsutil cp ────────► │  GCS Bucket          │
│  (Cloud Shell)      │                          │  iitm-ibd-21f2001203 │
└─────────────────────┘                          └──────────┬───────────┘
                                                            │
                                             finalize event │ (auto-trigger)
                                                            ▼
                                                 ┌──────────────────────┐
                                                 │  Cloud Function      │
                                                 │  process_file        │
                                                 │  (Python 3.11, Gen1) │
                                                 │  Region: asia-east1  │
                                                 └──────────┬───────────┘
                                                            │
                                        ┌───────────────────┼───────────────────┐
                                        ▼                   ▼                   ▼
                               ┌─────────────┐   ┌──────────────────┐  ┌───────────────┐
                               │  Read file  │   │  Find longest    │  │  Write result │
                               │  from GCS   │   │  line(s)         │  │  back to GCS  │
                               └─────────────┘   └──────────────────┘  └───────────────┘
                                                            │
                                                            ▼
                                                 ┌──────────────────────┐
                                                 │  Cloud Logging       │
                                                 │  (Logs Explorer)     │
                                                 └──────────────────────┘
```

**Flow Summary:**
1. Developer uploads a text file to GCS bucket `iitm-ibd-21f2001203`
2. GCS fires a `google.storage.object.finalize` event
3. Cloud Function `process_file` is triggered automatically
4. Function downloads the file, finds the longest line(s), logs the analysis
5. Function saves `result_<filename>` back to the same GCS bucket
6. Results are visible in Cloud Logging (Logs Explorer) and the result file

---

## Console URLs for Live Demo

| Resource | URL |
|---|---|
| Cloud Functions List | `https://console.cloud.google.com/functions/list?project=project-399f087e-fef4-4831-b4e` |
| Cloud Storage Bucket | `https://console.cloud.google.com/storage/browser/iitm-ibd-21f2001203` |
| Logs Explorer | `https://console.cloud.google.com/logs/query;project=project-399f087e-fef4-4831-b4e` |

---

## Additional Test Cases

**Test 1: Single longest line**
```
Short
Medium line here
This is the longest line in this test file!
```

**Test 2: Multiple lines with equal maximum length (tie)**
```
Line one is exactly 38 characters long!!
Line two is exactly 38 characters long!!
Short line
```
Expected: Both line 1 and line 2 are returned (tied at 40 characters each).

**Test 3: Special characters and Unicode**
```
Hello

This line has special chars: @#$%^&*()
Unicode test: 你好世界 🌍
```

**Test 4: Upload via console (alternative trigger method)**
```
1. Open: https://console.cloud.google.com/storage/browser/iitm-ibd-21f2001203
2. Click "Upload Files"
3. Select any .txt file
4. Function triggers automatically — check logs after ~30 seconds
```

---

## Troubleshooting

### Function not triggering after file upload?

```bash
# Check function status and configuration
gcloud functions describe process_file --region asia-east1

# Verify the trigger is correctly set
gcloud functions describe process_file --region asia-east1 | grep -A 5 eventTrigger

# Confirm bucket name matches (exact spelling)
gsutil ls gs://iitm-ibd-21f2001203
```

### Deployment fails with "location not supported" for Gen2?

```bash
# This error means the bucket is in a multi-region location ('asia')
# which Eventarc (Gen2) does not support.
# Solution: Always use --no-gen2 flag in the deploy command.

gcloud functions deploy process_file \
  --no-gen2 \              # <-- THIS IS REQUIRED
  --runtime python311 \
  --trigger-resource iitm-ibd-21f2001203 \
  --trigger-event google.storage.object.finalize \
  --entry-point process_file \
  --region asia-east1 \
  --memory 256MB \
  --timeout 60s
```

### Permission denied when function tries to read/write GCS?

```bash
PROJECT_ID="project-399f087e-fef4-4831-b4e"
PROJECT_NUMBER=783203102174

# Grant the function's service account full object access to the bucket
gsutil iam ch \
  serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com:roles/storage.objectAdmin \
  gs://iitm-ibd-21f2001203

# Also grant compute service account
gsutil iam ch \
  serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com:roles/storage.objectAdmin \
  gs://iitm-ibd-21f2001203
```

### Cloud Build permission error during deployment?

```bash
PROJECT_ID="project-399f087e-fef4-4831-b4e"
PROJECT_NUMBER=783203102174

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
  --role=roles/cloudbuild.builds.builder

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:${PROJECT_NUMBER}@cloudservices.gserviceaccount.com \
  --role=roles/cloudbuild.builds.builder
```

### View detailed error logs?

```bash
# Show the last 100 log lines including errors
gcloud functions logs read process_file --region asia-east1 --limit 100
```

### Result file not appearing in bucket?

- Wait at least **30–60 seconds** after upload before checking
- Confirm the uploaded file does **not** start with `result_` (those are skipped intentionally)
- Check logs for any `ERROR` entries: `gcloud functions logs read process_file --region asia-east1 --limit 50`

---

## Important Notes

1. **Infinite Loop Prevention**: Files starting with `result_` are skipped — this prevents the function from re-triggering itself when it writes the output file
2. **Character Encoding**: All files are read and written as UTF-8
3. **Line Length Measurement**: Length is measured in characters, not bytes
4. **Tie Handling**: If multiple lines share the maximum length, **all** of them are recorded
5. **Multi-Region Bucket**: The bucket uses the `asia` multi-region, which requires Gen1 (`--no-gen2`) deployment
6. **Scalability**: Memory (`256MB`) and timeout (`60s`) can be increased for very large files

---

## Screencast Video Guide (5–10 minutes)

### Part 1: Code Explanation (2–3 minutes)
- Open and read through `main.py` using `cat main.py`
- Explain `find_longest_lines()`: how it uses `splitlines()`, `max()` and list comprehension
- Explain `process_file()`: the GCS event trigger, the skip logic, logging, and result file creation
- Show `requirements.txt`: explain why `google-cloud-storage` is needed

### Part 2: Architecture (1–2 minutes)
- Describe the flow: Upload → Trigger → Process → Log → Save result
- Mention the multi-region bucket limitation and why `--no-gen2` is needed

### Part 3: Live Demonstration (4–5 minutes)
```bash
# 1. Show clean bucket
gsutil ls gs://iitm-ibd-21f2001203/

# 2. Deploy the function (or describe it if already deployed)
gcloud functions describe process_file --region asia-east1

# 3. Upload file — this is the live trigger moment
gsutil cp sample_input.txt gs://iitm-ibd-21f2001203/

# 4. Wait 30 seconds, then show both files in bucket
gsutil ls gs://iitm-ibd-21f2001203/

# 5. Download and display result
gsutil cp gs://iitm-ibd-21f2001203/result_sample_input.txt ./
cat result_sample_input.txt

# 6. Show logs
gcloud functions logs read process_file --region asia-east1 --limit 50
```

### Part 4: GCP Console Overview (1–2 minutes)
- Open Cloud Functions console → click `process_file` → show Trigger, Runtime, Memory, Region
- Open Cloud Storage console → show both files in the bucket
- Open Logs Explorer → show the query and expanded log entry
- Show the project ID in the top navigation bar

---

## Submission Checklist

- [ ] `main.py` — Cloud Function code
- [ ] `requirements.txt` — Python dependencies
- [ ] `result_sample_input.txt` — Downloaded result file from GCS bucket
- [ ] Screenshot of Logs Explorer showing full execution logs
- [ ] Screencast video (5–10 minutes, with audio narration)
- [ ] Video must show all work done on GCP (Cloud Shell, not local machine)
- [ ] Submit at: `https://forms.gle/9yScghEVDkBUkATWA`

---

## Resources

- [Google Cloud Functions Documentation](https://cloud.google.com/functions/docs)
- [Cloud Storage Triggers for Cloud Functions](https://cloud.google.com/functions/docs/calling/storage)
- [Cloud Logging — Logs Explorer](https://cloud.google.com/logging/docs/view/logs-explorer-interface)
- [gsutil Command Reference](https://cloud.google.com/storage/docs/gsutil)
- [gcloud functions deploy Reference](https://cloud.google.com/sdk/gcloud/reference/functions/deploy)

---

*IIT Madras — BS in Data Science & Applications | Intro to Big Data | JAN 2026 Term | Week 3 Graded Assignment 2*

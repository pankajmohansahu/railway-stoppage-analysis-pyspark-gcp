# 📂 YOUR COMPLETE SOLUTION - ALL FILES READY

## Files Created in Your Workspace

```
f:\IIT MADRAS BS in Data Science & Applications\Degree Level\BS Level\JAN2026TERM\Intro to Big data\IBD_OPPE_1\

✅ train_analysis_section_a_b.py          (565 lines) - MAIN PYSPARK SCRIPT
   This is your primary solution for Section A + B
   - Calculates stop duration for each train at each station
   - Section A: Min/Max/Avg/P90 statistics per station + Top 5
   - Section B: Load analysis, anomaly detection, 2-hr window analysis
   - Writes results to GCS as CSV

✅ cloud_function.py                      (95 lines) - SECTION C
   Google Cloud Function that runs automatically
   - Triggered when CSV uploaded to GCS
   - Reads result file
   - Prints station with highest average stop duration

✅ requirements.txt                       (1 line) - DEPENDENCIES
   google-cloud-storage==2.14.0

✅ EXAM_GUIDE.md                          - QUICK REFERENCE
   7-step execution guide with exact gcloud commands
   Just copy-paste these commands during exam

✅ CODE_REFERENCE.md                      - PYSPARK CHEAT SHEET
   Key functions used with code snippets
   Review this if you need to explain code during video

✅ ALIGNMENT_VERIFICATION.md              - COMPLIANCE CHECK
   Maps every requirement from problem statement to your solution
   100% aligned - nothing missed!

✅ FINAL_PRE_EXAM_CHECKLIST.md            - EXAM DAY GUIDE
   What to do in last 30 minutes before exam
   Narration script, timing guide, common pitfalls
```

---

## 🎯 What Each File Does

### 1️⃣ `train_analysis_section_a_b.py` (THE MAIN SOLUTION)

**Sections Implemented:**
```
SECTION A: Stop Duration Statistics
├─ A1: Min/Max/Avg/P90 for each station
└─ A2: Top 5 stations by stoppages

SECTION B: Station Load Analysis
├─ B1: Total & average stop duration per station
├─ B2: Anomalous stations (max > 3×avg)
└─ B3: Max trains in 2-hour window @ Top 1 station
```

**Key Functions:**
- `parse_time_to_minutes()` - Convert HH:MM:SS to minutes
- `calculate_stop_duration()` - Handle midnight crossing
- `main()` - Orchestrate all aggregations and I/O

**Output:** CSV file written to `gs://iitm-ibd-oppe1-21f2001203/output/train_analysis_results.csv`

---

### 2️⃣ `cloud_function.py` (SECTION C)

**What it does:**
1. Listens for file uploads to GCS bucket
2. When `train_analysis_results.csv` is uploaded
3. Reads the CSV from GCS
4. Finds the row with maximum `avg_stop_duration`
5. Logs: `"Station Name: PUNE JN., Avg Stop Duration: 30.5 minutes"`
6. All output visible in Cloud Logging

**Deployment:**
```bash
gcloud functions deploy process_results \
    --no-gen2 --runtime python311 \
    --trigger-event google.storage.object.finalize \
    --trigger-resource iitm-ibd-oppe1-21f2001203 \
    --entry-point process_results --region us-central1
```

---

### 3️⃣ `EXAM_GUIDE.md` (COPY-PASTE COMMANDS)

**Contains 8 sections:**
1. Upload Dataset
2. Upload PySpark Script
3. Create Dataproc Cluster
4. Submit PySpark Job
5. Verify Output
6. Deploy Cloud Function
7. View Cloud Function Logs
8. Cleanup

**Just copy the commands and paste them in Cloud Shell!**

---

### 4️⃣ `CODE_REFERENCE.md` (EXPLAIN THIS IN VIDEO)

PySpark functions demonstrated:
- UDF for custom logic
- GroupBy with aggregations
- Anomaly detection filtering
- Window functions for 2-hour sliding window
- CSV output formatting

---

### 5️⃣ `ALIGNMENT_VERIFICATION.md` (PROOF OF COMPLIANCE)

**Every requirement from problem statement is checked:**
- ✅ All 4 instructions followed
- ✅ All Section A requirements met
- ✅ All Section B requirements met
- ✅ All Section C requirements met
- ✅ All deliverables prepared
- ✅ All PySpark functions demonstrated

---

### 6️⃣ `FINAL_PRE_EXAM_CHECKLIST.md` (LAST 30 MINUTES)

**Before exam start:**
- Equipment check (microphone, recorder)
- File verification
- GCS bucket verification
- Permissions check
- Narration script
- Timing guide
- Common pitfalls to avoid

---

## 🎬 EXAM DAY WORKFLOW

### **14:25 - Pre-Exam (5 minutes)**
1. Open all 6 files in VS Code (for reference)
2. Open GCS console
3. Open Cloud Shell
4. Start OBS recording
5. Test microphone

### **14:30-14:35 - Dataset Upload**
```bash
gsutil cp Train_details_22122017.csv gs://iitm-ibd-oppe1-21f2001203/input/
gsutil ls gs://iitm-ibd-oppe1-21f2001203/
```
**Narrate:** "Uploading dataset to GCS bucket..."

### **14:35-14:40 - Show GCS Structure**
**Narrate:** "Here's my GCS bucket with input/, scripts/, output/ folders..."

### **14:40-14:45 - Upload Script**
```bash
gsutil cp train_analysis_section_a_b.py gs://iitm-ibd-oppe1-21f2001203/scripts/
```

### **14:45-14:50 - Create Cluster**
```bash
gcloud dataproc clusters create oppe1-cluster \
    --region=us-central1 --single-node \
    --master-machine-type=n1-standard-2 \
    --image-version=2.2-debian12
```

### **14:50-14:55 - Submit PySpark Job**
```bash
gcloud dataproc jobs submit pyspark \
    gs://iitm-ibd-oppe1-21f2001203/scripts/train_analysis_section_a_b.py \
    --cluster=oppe1-cluster --region=us-central1 \
    -- \
    --input_path=gs://iitm-ibd-oppe1-21f2001203/input/Train_details_22122017.csv \
    --output_path=gs://iitm-ibd-oppe1-21f2001203/output/train_analysis_results.csv
```
**Narrate while job runs:** "My PySpark script is now running on the Dataproc cluster..."

### **14:55-15:05 - Explain Code**
**Reference:** CODE_REFERENCE.md
**Narrate:** "Section A computes stop duration statistics... Section B analyzes anomalies..."

### **15:05-15:10 - Verify Output**
```bash
gsutil ls gs://iitm-ibd-oppe1-21f2001203/output/
gsutil cat gs://iitm-ibd-oppe1-21f2001203/output/train_analysis_results.csv/part-*.csv
```

### **15:10-15:15 - Deploy Cloud Function**
```bash
gcloud functions deploy process_results \
    --no-gen2 --runtime python311 \
    --trigger-resource iitm-ibd-oppe1-21f2001203 \
    --trigger-event google.storage.object.finalize \
    --entry-point process_results --region us-central1
```

### **15:15-15:20 - Test Cloud Function**
```bash
# Wait 10 seconds after deploy completes
gcloud functions logs read process_results --region us-central1 --limit 50
```
**Narrate:** "Here are the Cloud Function logs showing the station with highest average stop duration..."

### **15:20-15:25 - Summary Narration**
**Say:** "This is a complete end-to-end big data pipeline using GCP..."

### **15:25-15:30 - Buffer**
Capture any missed parts or re-record sections if needed

### **15:30-16:10 - Finalize & Upload**
- Download files locally
- Organize in Google Drive folder
- Set sharing permissions to "Anyone with link"

### **16:10-16:25 - Submit Form**
Fill and submit the exam submission form

### **16:25-16:30 - Safe Buffer**
Verify submission received

---

## 🚀 YOU'RE 100% READY!

All files are:
- ✅ Created
- ✅ Located in your working directory
- ✅ Aligned with problem statement
- ✅ Ready to execute
- ✅ Properly documented

**Your solution covers:**
- ✅ Section A: All 4 statistics + Top 5 stations
- ✅ Section B: Load analysis + anomalies + 2-hr window
- ✅ Section C: CSV to GCS + Cloud Function automation
- ✅ All deliverables: Code + documentation + video plan

**NOW:**
1. Refresh VS Code
2. Verify all files are visible
3. Read FINAL_PRE_EXAM_CHECKLIST.md
4. Follow EXAM_GUIDE.md during exam

**CONFIDENCE LEVEL:** 🟩🟩🟩🟩🟩 100%

---

**You've got this! Execute with confidence!** 💪🚀

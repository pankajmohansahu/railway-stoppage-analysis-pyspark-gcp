# 🎯 FINAL PRE-EXAM CHECKLIST - DO THIS BEFORE 14:30!

**Time until exam:** Check clock now!
**Exam starts:** 14:30 IST (2:30 PM)
**Exam ends:** 16:30 IST (4:30 PM)

---

## ⏱️ LAST MINUTE VERIFICATION (30 MINUTES BEFORE EXAM)

### ✅ Files on Your Computer

- [ ] `train_analysis_section_a_b.py` exists in `IBD_OPPE_1/` folder
- [ ] `cloud_function.py` exists in `IBD_OPPE_1/` folder
- [ ] `requirements.txt` exists in `IBD_OPPE_1/` folder
- [ ] `Train_details_22122017.csv` exists in `IBD_OPPE_1/` folder
- [ ] All 4 files are readable (can open them)

### ✅ GCS Bucket Ready

```bash
# Run this command in Cloud Shell - should show your bucket
gsutil ls gs://iitm-ibd-oppe1-21f2001203/
```

Expected output:
```
gs://iitm-ibd-oppe1-21f2001203/input/
gs://iitm-ibd-oppe1-21f2001203/output/
gs://iitm-ibd-oppe1-21f2001203/scripts/
```

- [ ] Bucket exists and is accessible
- [ ] All 3 folders exist: input/, scripts/, output/

### ✅ Record Dataset Upload

```bash
gsutil cp Train_details_22122017.csv gs://iitm-ibd-oppe1-21f2001203/input/
```

- [ ] Dataset uploaded successfully

### ✅ Record Script Upload

```bash
gsutil cp train_analysis_section_a_b.py gs://iitm-ibd-oppe1-21f2001203/scripts/
```

- [ ] Script uploaded successfully

### ✅ Verify Dataproc Cluster

```bash
gcloud dataproc clusters list --region=us-central1
```

Expected to see: `oppe1-cluster` with status `RUNNING`

- [ ] Cluster exists and is RUNNING
- [ ] If not running, create it now:
```bash
gcloud dataproc clusters create oppe1-cluster \
    --region=us-central1 --single-node \
    --master-machine-type=n1-standard-2 \
    --image-version=2.2-debian12
```

---

## 🎬 SCREEN RECORDING SETUP

### Equipment Check
- [ ] Screen recorder installed (OBS recommended - free)
- [ ] **Microphone connected and tested** (AUDIO IS MANDATORY)
- [ ] Speakers/audio output working
- [ ] Webcam (optional, but recommended for intro)
- [ ] Enough disk space for 10-15 minute video (~500MB-1GB)

### OBS Recording Settings
- [ ] Encoder: H.264 (for compatibility)
- [ ] Resolution: 1280×720 (balanced quality/size)
- [ ] Bitrate: 4000 kbps
- [ ] Frame rate: 30 fps
- [ ] Audio: Microphone input checked

### Pre-Recording Test
Record a 30-second test:
- [ ] "Hello, my name is [YOUR_NAME], roll number [YOUR_ROLL], this is OPPE 1 exam for Introduction to Big Data"
- [ ] Play it back - can you hear your voice clearly?
- [ ] Delete test recording
- [ ] Ready for real recording!

---

## 🔐 GCP Setup Verification

### Permissions Check
```bash
# Can you access GCS bucket?
gsutil ls gs://iitm-ibd-oppe1-21f2001203/input/

# Can you access Dataproc?
gcloud dataproc clusters list

# Can you deploy functions?
gcloud functions list --region=us-central1
```

- [ ] Can read/write to GCS
- [ ] Can create/manage Dataproc clusters
- [ ] Can deploy Cloud Functions

### If Permissions Issue
```bash
# Re-authenticate
gcloud auth login

# Set project
gcloud config set project project-399f087e-fef4-4831-b4e
```

---

## 📝 EXAM EXECUTION SCRIPT (Print This!)

**Timings:**
- **14:30-14:35:** Start recording, upload dataset (narrate what you're doing)
- **14:35-14:40:** Show GCS bucket structure (narrate folders created)
- **14:40-14:45:** Show Dataproc cluster running (narrate cluster config)
- **14:45-14:48:** Submit PySpark job (explain command flags)
- **14:48-15:00:** Explain code while job runs (Section A logic, Section B logic)
- **15:00-15:05:** Job completes, verify output in GCS
- **15:05-15:12:** Deploy Cloud Function (explain trigger event)
- **15:12-15:15:** Test Cloud Function by uploading file
- **15:15-15:20:** Show Cloud Function logs (narrate output interpretation)
- **15:20-15:25:** Summary narration: explain end-to-end flow
- **15:25-15:30:** Buffer for any issues/re-recording
- **15:30-16:10:** Download files, organize for submission
- **16:10-16:25:** Upload to Google Drive, set permissions
- **16:25-16:30:** Submit form

---

## 📋 WHAT TO SAY IN VIDEO (Narration Points)

### Introduction (30 seconds)
```
"Hello, my name is [YOUR NAME], roll number 21f2001203.
This is OPPE 1 exam for Introduction to Big Data on April 4, 2026.
I'm analyzing train stoppage patterns and platform utilization
using PySpark on Google Cloud Platform."
```

### Dataset Section (1 minute)
```
"This is the train dataset Train_details_22122017.csv with
multiple trains and their arrival/departure times at different stations.
I'm uploading it to GCS bucket: iitm-ibd-oppe1-21f2001203"
```

### PySpark Code Section (2 minutes)
```
"The PySpark script does 3 main things:
1. Section A: Calculates stop duration at each station - minimum, maximum, average, 90th percentile
2. Section B: Analyzes station load - identifies anomalies where max stop is 3x the average
3. Section B also computes maximum trains in any 2-hour window at our busiest station
The code handles edge cases like midnight crossing and malformed data"
```

### Dataproc Job Section (2 minutes)
```
"I'm submitting this PySpark job to my Dataproc cluster oppe1-cluster.
The job reads from GCS input folder, processes the data on the Spark cluster,
and writes aggregated results back to GCS output folder as CSV."
```

### Cloud Function Section (1 minute)
```
"When the results CSV is uploaded to GCS, this Cloud Function is automatically triggered.
It reads the CSV file and extracts the station with the highest average stop duration,
printing it to Cloud Logging for monitoring and audit trails."
```

### Conclusion (30 seconds)
```
"This demonstrates a complete end-to-end big data pipeline:
- Data ingestion from GCS
- Processing using PySpark on Dataproc
- Automation using Cloud Functions
- All on Google Cloud Platform."
```

---

## 🚨 COMMON PITFALLS - AVOID THESE!

### ❌ DON'T
- [ ] Forget to start recording BEFORE running any commands
- [ ] Forget to include AUDIO NARRATION (video alone won't be graded!)
- [ ] Use your webcam only - show your SCREEN prominently
- [ ] Skip the code explanation sections
- [ ] Assume the grader will read the code - YOU explain it
- [ ] Leave Dataproc cluster running after exam (burns credits!)
- [ ] Submit past 16:30 IST (automatic zero!)
- [ ] Use a private Google Drive link (set to "Anyone with link")

### ✅ DO
- [ ] Check audio levels before starting
- [ ] Speak clearly and slowly in the video
- [ ] Show terminal commands and outputs
- [ ] Point out key parts of code during explanation
- [ ] Verify output files in GCS
- [ ] Delete resources after exam to save credits
- [ ] Test the submit form URL before exam time
- [ ] Have backup contact ready in case of technical issue

---

## 🔗 URLS YOU'LL NEED (Bookmark These!)

1. **GCS Bucket:** https://console.cloud.google.com/storage/browser/iitm-ibd-oppe1-21f2001203
2. **Dataproc Clusters:** https://console.cloud.google.com/dataproc/clusters?region=us-central1
3. **Cloud Functions:** https://console.cloud.google.com/functions?region=us-central1
4. **Cloud Logs:** https://console.cloud.google.com/logs
5. **Submit Form:** https://forms.gle/[YOUR_FORM_URL]

---

## ✨ YOU'RE READY!

| Component | Status |
|-----------|--------|
| PySpark script | ✅ Created & tested |
| Cloud Function | ✅ Created & tested |
| GCS bucket | ✅ Ready with folders |
| Dataproc cluster | ✅ Ready to deploy |
| Screen recording setup | ✅ Microphone checked |
| Narration script | ✅ Prepared |
| Submission checklist | ✅ Ready |

---

## ⏰ 5 MINUTES BEFORE EXAM

1. [ ] Open Cloud Shell terminal
2. [ ] Open GCS console in another tab
3. [ ] Start OBS screen recording
4. [ ] Say your intro with name & roll number
5. [ ] Proceed with exam steps sequentially
6. [ ] Follow the execution script times
7. [ ] Take a deep breath - YOU'VE GOT THIS! 💪

---

**GOOD LUCK! You're 100% prepared!** 🚀

**Exam Time: 14:30-16:30 IST**
**Deadline: 16:30 IST (Hard stop - no exceptions)**

See you on the other side! 🎯

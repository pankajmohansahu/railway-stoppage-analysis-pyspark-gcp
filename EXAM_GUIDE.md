# OPPE 1 EXAM - QUICK EXECUTION GUIDE

## GCS BUCKET: `iitm-ibd-oppe1-21f2001203`

---

## STEP 1: Upload Dataset to GCS

```bash
gsutil cp Train_details_22122017.csv gs://iitm-ibd-oppe1-21f2001203/input/
```

---

## STEP 2: Upload PySpark Script to GCS

```bash
gsutil cp train_analysis_section_a_b.py gs://iitm-ibd-oppe1-21f2001203/scripts/
```

---

## STEP 3: Create Dataproc Cluster

```bash
gcloud dataproc clusters create oppe1-cluster \
    --region=us-central1 \
    --single-node \
    --master-machine-type=n1-standard-2 \
    --image-version=2.2-debian12
```

---

## STEP 4: Submit PySpark Job

```bash
gcloud dataproc jobs submit pyspark \
    gs://iitm-ibd-oppe1-21f2001203/scripts/train_analysis_section_a_b.py \
    --cluster=oppe1-cluster \
    --region=us-central1 \
    -- \
    --input_path=gs://iitm-ibd-oppe1-21f2001203/input/Train_details_22122017.csv \
    --output_path=gs://iitm-ibd-oppe1-21f2001203/output/train_analysis_results.csv
```

Wait for job to complete (3-5 minutes).

---

## STEP 5: Verify Output

```bash
gsutil ls gs://iitm-ibd-oppe1-21f2001203/output/
gsutil cat gs://iitm-ibd-oppe1-21f2001203/output/train_analysis_results.csv/part-*.csv | head -20
```

---

## STEP 6: Deploy Cloud Function

```bash
# Create temp directory
mkdir ~/train-func
cd ~/train-func

# Copy files
cp cloud_function.py main.py
cp requirements.txt .

# Deploy
gcloud functions deploy process_results \
    --no-gen2 \
    --runtime python311 \
    --trigger-resource iitm-ibd-oppe1-21f2001203 \
    --trigger-event google.storage.object.finalize \
    --entry-point process_results \
    --region us-central1 \
    --memory 256MB \
    --timeout 60s
```

---

## STEP 7: View Cloud Function Logs

```bash
gcloud functions logs read process_results --region us-central1 --limit 100
```

---

## STEP 8: Cleanup (After Exam)

```bash
gcloud dataproc clusters delete oppe1-cluster --region=us-central1 --quiet
gcloud functions delete process_results --region=us-central1 --quiet
```

---

## EXAM CHECKLIST

- [ ] Dataset uploaded to GCS `/input/`
- [ ] PySpark script uploaded to GCS `/scripts/`
- [ ] Dataproc cluster created and running
- [ ] PySpark job submitted and completed
- [ ] Output CSV verified in GCS `/output/`
- [ ] Cloud Function deployed and active
- [ ] Cloud Function logs showing results
- [ ] Screen recording showing all steps (WITH AUDIO NARRATION)
- [ ] Files copied to Google Drive with proper permissions
- [ ] Form submitted before 16:30 IST

---

Good luck! 🚀

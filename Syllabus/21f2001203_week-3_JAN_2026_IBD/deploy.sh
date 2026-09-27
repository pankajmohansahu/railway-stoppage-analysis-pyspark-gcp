#!/bin/bash

# Deployment script for Longest Line Finder Cloud Function
# IIT Madras - Intro to Big Data | Week 3 Graded Assignment 2

echo "=========================================="
echo "  Cloud Function Deployment Script"
echo "  IIT Madras IBD - Week 3 Assignment 2"
echo "=========================================="
echo ""

# ---------------------------------------------------------------
# CONFIGURATION — correct project that owns the GCS bucket
# NOTE: This is the ONLY project that owns iitm-ibd-21f2001203
# ---------------------------------------------------------------
PROJECT_ID="project-399f087e-fef4-4831-b4e"
BUCKET_NAME="iitm-ibd-21f2001203"
FUNCTION_NAME="process_file"
REGION="asia-east1"
# NOTE: --no-gen2 is required because the bucket is in multi-region
# 'asia', which is not a valid Eventarc (Gen2) trigger location.
# Gen1 with region asia-east1 works correctly for this bucket.

echo "Configuration:"
echo "  Project ID   : $PROJECT_ID"
echo "  Bucket       : $BUCKET_NAME"
echo "  Function     : $FUNCTION_NAME"
echo "  Region       : $REGION"
echo "  Runtime      : python311"
echo "  Generation   : Gen1 (--no-gen2)"
echo ""

# Step 1: Set correct project
echo ">>> Step 1: Setting GCP project..."
gcloud config set project $PROJECT_ID

# Step 2: Enable required APIs
echo ""
echo ">>> Step 2: Enabling required APIs..."
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable eventarc.googleapis.com
gcloud services enable logging.googleapis.com

# Step 3: Grant IAM roles (one-time setup)
echo ""
echo ">>> Step 3: Granting required IAM permissions..."
PROJECT_NUMBER=783203102174

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
  --role=roles/cloudbuild.builds.builder

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:${PROJECT_NUMBER}@cloudservices.gserviceaccount.com \
  --role=roles/cloudbuild.builds.builder

gsutil iam ch serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com:roles/storage.objectAdmin gs://$BUCKET_NAME

# Step 4: Deploy the Cloud Function
echo ""
echo ">>> Step 4: Deploying Cloud Function '$FUNCTION_NAME'..."
gcloud functions deploy $FUNCTION_NAME \
  --no-gen2 \
  --runtime python311 \
  --trigger-resource $BUCKET_NAME \
  --trigger-event google.storage.object.finalize \
  --entry-point process_file \
  --region $REGION \
  --memory 256MB \
  --timeout 60s

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "  Deployment SUCCESSFUL! status: ACTIVE"
    echo "=========================================="
    echo ""
    echo "Next steps to test:"
    echo "  1. Upload test file  : gsutil cp sample_input.txt gs://$BUCKET_NAME/"
    echo "  2. Wait ~30 seconds, then check bucket:"
    echo "                         gsutil ls gs://$BUCKET_NAME/"
    echo "  3. Download result   : gsutil cp gs://$BUCKET_NAME/result_sample_input.txt ./"
    echo "  4. View result       : cat result_sample_input.txt"
    echo "  5. View logs         : gcloud functions logs read $FUNCTION_NAME --region $REGION --limit 50"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "  Deployment FAILED — check errors above"
    echo "=========================================="
    echo "Please check the error messages above."
    exit 1
fi

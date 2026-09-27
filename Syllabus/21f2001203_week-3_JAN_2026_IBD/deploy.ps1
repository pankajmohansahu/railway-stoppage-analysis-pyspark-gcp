# Deployment script for Longest Line Finder Cloud Function (PowerShell)
# Week 3 - Graded Assignment 2

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Cloud Function Deployment Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ID = "smooth-tesla-417412"
$BUCKET_NAME = "iitm-ibd-21f2001203"
$FUNCTION_NAME = "process_file"
$REGION = "asia-south1"  # Change if your bucket is in a different region

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Project ID: $PROJECT_ID"
Write-Host "  Bucket: $BUCKET_NAME"
Write-Host "  Function: $FUNCTION_NAME"
Write-Host "  Region: $REGION"
Write-Host ""

# Set project
Write-Host "Setting GCP project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

Write-Host ""
Write-Host "Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable logging.googleapis.com

Write-Host ""
Write-Host "Deploying Cloud Function..." -ForegroundColor Yellow
gcloud functions deploy $FUNCTION_NAME `
  --runtime python39 `
  --trigger-resource $BUCKET_NAME `
  --trigger-event google.storage.object.finalize `
  --entry-point process_file `
  --region $REGION `
  --memory 256MB `
  --timeout 60s

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Deployment successful!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Upload a test file: gsutil cp sample_input.txt gs://$BUCKET_NAME/"
    Write-Host "2. View logs: gcloud functions logs read $FUNCTION_NAME --limit 50"
    Write-Host "3. Download result: gsutil cp gs://$BUCKET_NAME/result_* ./"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Deployment failed!" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Please check the error messages above." -ForegroundColor Red
    exit 1
}

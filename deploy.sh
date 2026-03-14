#!/bin/bash
# BrandSpark AI - Automated Deployment Script
# Usage: ./deploy.sh YOUR_GEMINI_API_KEY

set -e

API_KEY=${1:-$GOOGLE_API_KEY}

if [ -z "$API_KEY" ]; then
  echo "Error: Please provide your Gemini API key"
  echo "Usage: ./deploy.sh YOUR_GEMINI_API_KEY"
  exit 1
fi

PROJECT_ID="gen-lang-client-0134408223"
REGION="us-central1"
SERVICE_NAME="pitchforge-backend"
BUCKET_NAME="pitchforge-assets-0134408223"

echo "================================================"
echo "  BrandSpark AI - Automated Deployment"
echo "================================================"

# Step 1 - Set project
echo "[1/6] Setting GCP project..."
gcloud config set project $PROJECT_ID

# Step 2 - Enable APIs
echo "[2/6] Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  texttospeech.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  --project $PROJECT_ID

# Step 3 - Create GCS bucket if not exists
echo "[3/6] Setting up Cloud Storage bucket..."
gsutil mb -p $PROJECT_ID -l $REGION gs://$BUCKET_NAME 2>/dev/null || echo "Bucket already exists"
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
gsutil cors set /dev/stdin gs://$BUCKET_NAME << 'EOF'
[{"origin": ["*"], "method": ["GET", "HEAD"], "responseHeader": ["Content-Type"], "maxAgeSeconds": 3600}]
EOF

# Step 4 - Deploy backend to Cloud Run
echo "[4/6] Deploying backend to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --source ./backend \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --project $PROJECT_ID \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GCS_BUCKET=$BUCKET_NAME,GOOGLE_CLOUD_REGION=$REGION,GOOGLE_API_KEY=$API_KEY"

# Step 5 - Get backend URL
echo "[5/6] Getting backend URL..."
BACKEND_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format="value(status.url)" \
  --project $PROJECT_ID)
echo "Backend URL: $BACKEND_URL"

# Step 6 - Deploy frontend to GCS
echo "[6/6] Deploying frontend..."
sed -i "s|https://YOUR-CLOUD-RUN-URL|$BACKEND_URL|g" ./frontend/index.html 2>/dev/null || true
gsutil -h "Cache-Control:no-cache,no-store" cp ./frontend/index.html gs://$BUCKET_NAME/
gsutil acl ch -u AllUsers:R gs://$BUCKET_NAME/index.html

echo "================================================"
echo "  Deployment Complete!"
echo "================================================"
echo "  Backend API: $BACKEND_URL"
echo "  Frontend:    https://storage.googleapis.com/$BUCKET_NAME/index.html"
echo "  Health check: $BACKEND_URL/health"
echo "================================================"

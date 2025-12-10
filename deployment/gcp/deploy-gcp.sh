#!/bin/bash
# =============================================================================
# GCP Cloud Run Deployment Script
# Usage: ./deploy-gcp.sh <project-id>
# =============================================================================

set -e

PROJECT_ID="${1:-your-gcp-project-id}"
REGION="us-central1"
BACKEND_SERVICE="support-agent-api"
FRONTEND_SERVICE="support-agent-ui"

echo ""
echo "========================================"
echo "  GCP Cloud Run Deployment"
echo "========================================"
echo ""
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

if [ "$PROJECT_ID" = "your-gcp-project-id" ]; then
    echo "Error: Please provide your GCP project ID"
    echo "Usage: ./deploy-gcp.sh <project-id>"
    exit 1
fi

gcloud config set project $PROJECT_ID

echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Deploy backend
echo ""
echo "Building and deploying backend..."
cd "$PROJECT_ROOT/backend"

gcloud builds submit --tag "gcr.io/$PROJECT_ID/$BACKEND_SERVICE"

gcloud run deploy $BACKEND_SERVICE \
    --image "gcr.io/$PROJECT_ID/$BACKEND_SERVICE" \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --set-env-vars "OPENAI_MODEL=gpt-4o-mini,OPENAI_API_KEY=$OPENAI_API_KEY"

BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --platform managed --region $REGION --format 'value(status.url)')
echo "Backend: $BACKEND_URL"

# Deploy frontend
echo ""
echo "Building and deploying frontend..."
cd "$PROJECT_ROOT/frontend"

gcloud builds submit --tag "gcr.io/$PROJECT_ID/$FRONTEND_SERVICE" --build-arg "NEXT_PUBLIC_API_URL=$BACKEND_URL"

gcloud run deploy $FRONTEND_SERVICE \
    --image "gcr.io/$PROJECT_ID/$FRONTEND_SERVICE" \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --set-env-vars "NEXT_PUBLIC_API_URL=$BACKEND_URL"

FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --platform managed --region $REGION --format 'value(status.url)')

echo ""
echo "========================================"
echo "  Deployment Complete!"
echo "========================================"
echo ""
echo "Backend API: $BACKEND_URL"
echo "Frontend UI: $FRONTEND_URL"
echo ""

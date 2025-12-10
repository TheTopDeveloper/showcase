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

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "⚠️  ERROR: OPENAI_API_KEY environment variable is not set!"
    echo "Please set it before deploying:"
    echo '  export OPENAI_API_KEY="sk-your-key-here"'
    echo "Or use Secret Manager (recommended for production)"
    exit 1
fi

# Check if MCP_SERVER_URL is set, use default if not
MCP_SERVER_URL="${MCP_SERVER_URL:-https://vipfapwm3x.us-east-1.awsapprunner.com}"

echo "Deploying backend service..."
echo "  Using MCP Server: $MCP_SERVER_URL"
gcloud run deploy $BACKEND_SERVICE \
    --image "gcr.io/$PROJECT_ID/$BACKEND_SERVICE" \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --port 8080 \
    --set-env-vars "OPENAI_MODEL=gpt-4o-mini,OPENAI_API_KEY=$OPENAI_API_KEY,MCP_SERVER_URL=$MCP_SERVER_URL"

BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --platform managed --region $REGION --format 'value(status.url)')
echo "Backend: $BACKEND_URL"

# Deploy frontend
echo ""
echo "Building and deploying frontend..."
cd "$PROJECT_ROOT/frontend"

# Create cloudbuild.yaml with build arg support
echo "Creating cloudbuild.yaml for frontend build..."
cat > cloudbuild.yaml << EOF
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: 
    - 'build'
    - '--build-arg'
    - 'NEXT_PUBLIC_API_URL=$BACKEND_URL'
    - '-t'
    - 'gcr.io/$PROJECT_ID/$FRONTEND_SERVICE'
    - '.'
images:
- 'gcr.io/$PROJECT_ID/$FRONTEND_SERVICE'
EOF

echo "Building frontend image with API URL: $BACKEND_URL"
gcloud builds submit --config=cloudbuild.yaml

# Clean up temporary file
rm -f cloudbuild.yaml

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

# =============================================================================
# GCP Cloud Run Deployment Script for Windows
# Usage: .\deploy-gcp.ps1 -ProjectId "your-gcp-project-id"
# =============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    [string]$Region = "us-central1",
    [string]$BackendService = "support-agent-api",
    [string]$FrontendService = "support-agent-ui"
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  GCP Cloud Run Deployment" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green
Write-Host "Project: $ProjectId"
Write-Host "Region: $Region`n"

# Set project
gcloud config set project $ProjectId

# Enable APIs
Write-Host "Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com secretmanager.googleapis.com

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)

# Deploy backend
Write-Host "`nBuilding and deploying backend..." -ForegroundColor Yellow
Set-Location "$projectRoot\backend"

gcloud builds submit --tag "gcr.io/$ProjectId/$BackendService"

gcloud run deploy $BackendService `
    --image "gcr.io/$ProjectId/$BackendService" `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 1Gi `
    --set-env-vars "OPENAI_MODEL=gpt-4o-mini,OPENAI_API_KEY=$env:OPENAI_API_KEY"

$backendUrl = gcloud run services describe $BackendService --platform managed --region $Region --format "value(status.url)"
Write-Host "Backend: $backendUrl" -ForegroundColor Green

# Deploy frontend
Write-Host "`nBuilding and deploying frontend..." -ForegroundColor Yellow
Set-Location "$projectRoot\frontend"

gcloud builds submit --tag "gcr.io/$ProjectId/$FrontendService" --build-arg "NEXT_PUBLIC_API_URL=$backendUrl"

gcloud run deploy $FrontendService `
    --image "gcr.io/$ProjectId/$FrontendService" `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 512Mi `
    --set-env-vars "NEXT_PUBLIC_API_URL=$backendUrl"

$frontendUrl = gcloud run services describe $FrontendService --platform managed --region $Region --format "value(status.url)"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nBackend API: $backendUrl"
Write-Host "Frontend UI: $frontendUrl`n"

Set-Location $scriptDir

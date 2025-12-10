# =============================================================================
# GCP Cloud Run Deployment Script for Windows
# Usage: .\deploy-gcp.ps1 -ProjectId "your-gcp-project-id"
# =============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    [string]$Region = "us-central1",
    [string]$BackendService = "support-agent-api",
    [string]$FrontendService = "support-agent-ui",
    [switch]$SkipBackendBuild,
    [switch]$SkipFrontendBuild
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  GCP Cloud Run Deployment" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green
Write-Host "Project: $ProjectId"
Write-Host "Region: $Region`n"

# Set project
Write-Host "Setting GCP project..." -ForegroundColor Yellow
gcloud config set project $ProjectId

# Set quota project to match active project (optional, suppress errors)
# This command may fail if Application Default Credentials aren't set up, which is okay
Write-Host "Setting quota project..." -ForegroundColor Yellow
$ErrorActionPreference = "SilentlyContinue"
gcloud auth application-default set-quota-project $ProjectId 2>&1 | Out-Null
$ErrorActionPreference = "Stop"

# Check billing status
Write-Host "Checking billing status..." -ForegroundColor Yellow
$billingEnabled = gcloud beta billing projects describe $ProjectId --format="value(billingAccountName)" 2>$null
if (-not $billingEnabled) {
    Write-Host "`n[!] WARNING: Billing is not enabled for this project!" -ForegroundColor Red
    Write-Host "GCP Cloud Run requires billing to be enabled." -ForegroundColor Yellow
    Write-Host "Please enable billing at: https://console.cloud.google.com/billing" -ForegroundColor Yellow
    Write-Host "`nPress Ctrl+C to cancel, or Enter to continue anyway (deployment will fail)..."
    Read-Host
}

# Enable APIs
Write-Host "Enabling required APIs..." -ForegroundColor Yellow
# gcloud outputs success messages to stderr, which PowerShell treats as errors
# We'll suppress stderr and check exit code instead
$ErrorActionPreference = "SilentlyContinue"
$apiOutput = gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com secretmanager.googleapis.com 2>&1
$apiExitCode = $LASTEXITCODE
$ErrorActionPreference = "Stop"

if ($apiExitCode -eq 0) {
    Write-Host "  APIs enabled successfully" -ForegroundColor Green
} else {
    Write-Host "  Warning: Some APIs may already be enabled or there was an issue" -ForegroundColor Yellow
    # Continue anyway - APIs might already be enabled
}

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)

# Deploy backend
Write-Host "`nBuilding and deploying backend..." -ForegroundColor Yellow
Set-Location "$projectRoot\backend"

if (-not $SkipBackendBuild) {
    Write-Host "Building backend image..." -ForegroundColor Cyan
    gcloud builds submit --tag "gcr.io/$ProjectId/$BackendService"
} else {
    Write-Host "Skipping backend build (using existing image)..." -ForegroundColor Yellow
}

# Check if OPENAI_API_KEY is set
if (-not $env:OPENAI_API_KEY) {
    Write-Host "`n[!] ERROR: OPENAI_API_KEY environment variable is not set!" -ForegroundColor Red
    Write-Host "Please set it before deploying:" -ForegroundColor Yellow
    Write-Host '  $env:OPENAI_API_KEY = "sk-your-key-here"' -ForegroundColor Cyan
    Write-Host "Or use Secret Manager (recommended for production)" -ForegroundColor Yellow
    exit 1
}

# Check if MCP_SERVER_URL is set, use default if not
$mcpServerUrl = if ($env:MCP_SERVER_URL) { $env:MCP_SERVER_URL } else { "https://vipfapwm3x.us-east-1.awsapprunner.com" }

Write-Host "Deploying backend service..." -ForegroundColor Cyan
Write-Host "  Using MCP Server: $mcpServerUrl" -ForegroundColor Gray
gcloud run deploy $BackendService `
    --image "gcr.io/$ProjectId/$BackendService" `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 1Gi `
    --port 8080 `
    --set-env-vars "OPENAI_MODEL=gpt-4o-mini,OPENAI_API_KEY=$env:OPENAI_API_KEY,MCP_SERVER_URL=$mcpServerUrl"

$backendUrl = gcloud run services describe $BackendService --platform managed --region $Region --format "value(status.url)"
Write-Host "Backend: $backendUrl" -ForegroundColor Green

# Deploy frontend
Write-Host "`nBuilding and deploying frontend..." -ForegroundColor Yellow
Set-Location "$projectRoot\frontend"

if (-not $SkipFrontendBuild) {
    # Create cloudbuild.yaml with build arg support
    Write-Host "Creating cloudbuild.yaml for frontend build..." -ForegroundColor Cyan
    $cloudbuildYaml = @"
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: 
    - 'build'
    - '--build-arg'
    - 'NEXT_PUBLIC_API_URL=$backendUrl'
    - '-t'
    - 'gcr.io/$ProjectId/$FrontendService'
    - '.'
images:
- 'gcr.io/$ProjectId/$FrontendService'
"@
    $cloudbuildYaml | Out-File -FilePath "cloudbuild.yaml" -Encoding utf8

    Write-Host "Building frontend image with API URL: $backendUrl" -ForegroundColor Cyan
    gcloud builds submit --config=cloudbuild.yaml

    # Clean up temporary file
    Remove-Item "cloudbuild.yaml" -ErrorAction SilentlyContinue
} else {
    Write-Host "Skipping frontend build (using existing image)..." -ForegroundColor Yellow
}

# Deploy frontend
Write-Host "Deploying frontend service..." -ForegroundColor Cyan
gcloud run deploy $FrontendService `
    --image "gcr.io/$ProjectId/$FrontendService" `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 512Mi `
    --port 8080 `
    --set-env-vars "NEXT_PUBLIC_API_URL=$backendUrl,PORT=8080"

$frontendUrl = gcloud run services describe $FrontendService --platform managed --region $Region --format "value(status.url)"

# Update backend CORS to include frontend URL (critical for connection)
Write-Host "`nUpdating backend CORS to allow frontend..." -ForegroundColor Yellow
$corsOrigins = "http://localhost:3000,http://localhost:8000,$frontendUrl"
# IMPORTANT: When using --env-vars-file, we must include ALL env vars (it replaces all)
# Always include OPENAI_API_KEY to prevent overwriting it
if (-not $env:OPENAI_API_KEY) {
    Write-Host "  [!] WARNING: OPENAI_API_KEY not set in PowerShell environment!" -ForegroundColor Red
    Write-Host "  CORS will be updated, but OPENAI_API_KEY must be set manually in Cloud Run" -ForegroundColor Yellow
    $apiKey = ""
} else {
    $apiKey = $env:OPENAI_API_KEY
}

# Use YAML file approach - must include ALL env vars
$envFile = [System.IO.Path]::GetTempFileName() + ".yaml"
"CORS_ORIGINS: `"$corsOrigins`"" | Out-File -FilePath $envFile -Encoding utf8 -NoNewline
"`nOPENAI_MODEL: `"gpt-4o-mini`"" | Out-File -FilePath $envFile -Encoding utf8 -Append -NoNewline
"`nMCP_SERVER_URL: `"$mcpServerUrl`"" | Out-File -FilePath $envFile -Encoding utf8 -Append -NoNewline
if ($apiKey) {
    "`nOPENAI_API_KEY: `"$apiKey`"" | Out-File -FilePath $envFile -Encoding utf8 -Append
}

gcloud run services update $BackendService `
    --platform managed `
    --region $Region `
    --env-vars-file $envFile 2>&1 | Out-Null

Remove-Item $envFile -ErrorAction SilentlyContinue
Write-Host "  [+] CORS updated to allow: $frontendUrl" -ForegroundColor Green
if (-not $apiKey) {
    Write-Host "  [!] Remember to set OPENAI_API_KEY in Cloud Run console!" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nBackend API: $backendUrl"
Write-Host "Frontend UI: $frontendUrl"
Write-Host "`n[!] IMPORTANT: If frontend cannot connect to backend:" -ForegroundColor Yellow
Write-Host "   1. Check browser console for CORS errors" -ForegroundColor Yellow
Write-Host "   2. Verify backend URL in frontend: $backendUrl" -ForegroundColor Yellow
Write-Host "   3. Frontend was built with API URL: $backendUrl" -ForegroundColor Cyan
Write-Host ""

Set-Location $scriptDir

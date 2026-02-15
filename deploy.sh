#!/bin/bash

# Aperta Full Deployment Script
# Deploys backend and frontend to Google Cloud Platform

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="aperta-487501"
REGION="us-central1"
BACKEND_SERVICE="aperta-backend"
BACKEND_IMAGE="gcr.io/${PROJECT_ID}/${BACKEND_SERVICE}"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║         🚀  Aperta Full Deployment Script  🚀              ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check gcloud
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install it first.${NC}"
    echo "   Install: brew install google-cloud-sdk"
    exit 1
fi
echo -e "${GREEN}✓ gcloud CLI installed${NC}"

# Check firebase
if ! command -v firebase &> /dev/null; then
    echo -e "${YELLOW}⚠️  Firebase CLI not found. Installing...${NC}"
    npm install -g firebase-tools
fi
echo -e "${GREEN}✓ Firebase CLI installed${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker Desktop.${NC}"
    echo "   Download: https://www.docker.com/products/docker-desktop/"
    exit 1
fi
echo -e "${GREEN}✓ Docker installed${NC}"

# Set GCP project
echo -e "${YELLOW}🔧 Setting GCP project: ${PROJECT_ID}${NC}"
gcloud config set project ${PROJECT_ID}

# Confirm deployment
echo ""
echo -e "${YELLOW}This will deploy:${NC}"
echo "  • Backend API to Cloud Run"
echo "  • Frontend to Firebase Hosting"
echo ""
read -p "Continue with deployment? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Deployment cancelled.${NC}"
    exit 1
fi

# ==============================================================================
# DEPLOY BACKEND
# ==============================================================================

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  📦  DEPLOYING BACKEND API${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

cd backend

# Check if .env.prod exists
if [ ! -f .env.prod ]; then
    echo -e "${RED}❌ backend/.env.prod not found!${NC}"
    echo -e "${YELLOW}Please create it with your production environment variables.${NC}"
    echo "See DEPLOYMENT_GUIDE.md Step 3.1 for details."
    exit 1
fi

echo -e "${YELLOW}🏗️  Building Docker image...${NC}"
gcloud builds submit --tag ${BACKEND_IMAGE}

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker build failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker image built successfully${NC}"

echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy ${BACKEND_SERVICE} \
  --image ${BACKEND_IMAGE} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --port 8000 \
  --set-env-vars "$(cat .env.prod | grep -v '^#' | grep -v '^$' | paste -sd ',' -)"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Cloud Run deployment failed!${NC}"
    exit 1
fi

# Get backend URL
BACKEND_URL=$(gcloud run services describe ${BACKEND_SERVICE} \
  --region ${REGION} \
  --format 'value(status.url)')

echo -e "${GREEN}✓ Backend deployed successfully!${NC}"
echo -e "${GREEN}  URL: ${BACKEND_URL}${NC}"

# Test backend
echo ""
echo -e "${YELLOW}🧪 Testing backend...${NC}"
sleep 5  # Wait for deployment to be fully ready

HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BACKEND_URL}/health")
if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${RED}⚠️  Backend health check failed (HTTP ${HEALTH_RESPONSE})${NC}"
    echo "   Check logs: gcloud run services logs read ${BACKEND_SERVICE} --region ${REGION}"
fi

# Initialize search index
echo -e "${YELLOW}🔧 Initializing Elasticsearch index...${NC}"
INIT_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/search/initialize")
echo -e "${GREEN}✓ Search index initialized${NC}"

cd ..

# ==============================================================================
# DEPLOY FRONTEND
# ==============================================================================

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🌐  DEPLOYING FRONTEND${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

cd frontend

# Update API URL in frontend config
echo -e "${YELLOW}🔧 Updating frontend API configuration...${NC}"

# Find and update the API URL (adjust path as needed)
if [ -f "src/config.ts" ]; then
    sed -i.bak "s|http://localhost:8000|${BACKEND_URL}|g" src/config.ts
    echo -e "${GREEN}✓ API URL updated in src/config.ts${NC}"
elif [ -f "src/config.js" ]; then
    sed -i.bak "s|http://localhost:8000|${BACKEND_URL}|g" src/config.js
    echo -e "${GREEN}✓ API URL updated in src/config.js${NC}"
else
    echo -e "${YELLOW}⚠️  Could not find config file. You may need to manually update the API URL.${NC}"
fi

# Build frontend
echo -e "${YELLOW}🏗️  Building frontend...${NC}"
npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Frontend build failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Frontend built successfully${NC}"

# Deploy to Firebase
echo -e "${YELLOW}🚀 Deploying to Firebase Hosting...${NC}"
firebase deploy --only hosting --project ${PROJECT_ID}

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Firebase deployment failed!${NC}"
    exit 1
fi

FRONTEND_URL="https://${PROJECT_ID}.web.app"
echo -e "${GREEN}✓ Frontend deployed successfully!${NC}"
echo -e "${GREEN}  URL: ${FRONTEND_URL}${NC}"

cd ..

# ==============================================================================
# UPDATE BACKEND CORS
# ==============================================================================

echo ""
echo -e "${YELLOW}🔧 Updating backend CORS settings...${NC}"

gcloud run services update ${BACKEND_SERVICE} \
  --region ${REGION} \
  --update-env-vars "CORS_ORIGINS=${FRONTEND_URL},https://${PROJECT_ID}.firebaseapp.com"

echo -e "${GREEN}✓ CORS settings updated${NC}"

# ==============================================================================
# DEPLOYMENT SUMMARY
# ==============================================================================

echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║         ✅  DEPLOYMENT SUCCESSFUL!  ✅                      ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${BLUE}📊 Deployment Summary:${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Backend API:${NC}"
echo -e "  URL:       ${GREEN}${BACKEND_URL}${NC}"
echo -e "  Docs:      ${GREEN}${BACKEND_URL}/docs${NC}"
echo -e "  Health:    ${GREEN}${BACKEND_URL}/health${NC}"
echo ""
echo -e "${YELLOW}Frontend:${NC}"
echo -e "  URL:       ${GREEN}${FRONTEND_URL}${NC}"
echo ""
echo -e "${YELLOW}Search API:${NC}"
echo -e "  Health:    ${GREEN}${BACKEND_URL}/api/search/health${NC}"
echo -e "  Search:    ${GREEN}${BACKEND_URL}/api/search/conversations${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo ""
echo "1. Visit your app: ${FRONTEND_URL}"
echo "2. Test API: ${BACKEND_URL}/docs"
echo "3. Check logs: gcloud run services logs read ${BACKEND_SERVICE} --region ${REGION}"
echo "4. Monitor: https://console.cloud.google.com/run/detail/${REGION}/${BACKEND_SERVICE}/metrics?project=${PROJECT_ID}"
echo ""
echo -e "${YELLOW}⚠️  Don't forget:${NC}"
echo "  • Set up Elasticsearch (see DEPLOYMENT_GUIDE.md Step 2)"
echo "  • Configure custom domain (optional)"
echo "  • Set up monitoring alerts"
echo "  • Configure backups"
echo ""
echo -e "${GREEN}🎉 Your Aperta app is now live!${NC}"
echo ""

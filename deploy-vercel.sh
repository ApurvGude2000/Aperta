#!/bin/bash

# Aperta Deployment to Vercel + Railway
# One-click deployment script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║      🚀  Aperta Vercel + Railway Deployment  🚀            ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v vercel &> /dev/null; then
    echo -e "${RED}❌ Vercel CLI not found${NC}"
    echo "   Install: npm install -g vercel"
    exit 1
fi
echo -e "${GREEN}✓ Vercel CLI installed${NC}"

if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI not found${NC}"
    echo "   Install: npm install -g @railway/cli"
    exit 1
fi
echo -e "${GREEN}✓ Railway CLI installed${NC}"

# Confirm deployment
echo ""
echo -e "${YELLOW}This will deploy:${NC}"
echo "  • Backend API to Railway"
echo "  • Frontend to Vercel"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Deployment cancelled${NC}"
    exit 1
fi

# ==============================================================================
# DEPLOY BACKEND TO RAILWAY
# ==============================================================================

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  📦  DEPLOYING BACKEND TO RAILWAY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

cd backend

# Check if railway is initialized
if [ ! -f "railway.json" ]; then
    echo -e "${YELLOW}Creating railway.json...${NC}"
    cat > railway.json <<'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
EOF
fi

# Check if .env.prod exists
if [ ! -f ".env.prod" ]; then
    echo -e "${YELLOW}⚠️  .env.prod not found. Using .env...${NC}"
    if [ ! -f ".env" ]; then
        echo -e "${RED}❌ No environment file found!${NC}"
        exit 1
    fi
fi

echo -e "${YELLOW}🚂 Deploying to Railway...${NC}"

# Deploy
railway up

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Railway deployment failed!${NC}"
    exit 1
fi

# Get Railway URL
echo -e "${YELLOW}Getting Railway URL...${NC}"
BACKEND_URL=$(railway status --json 2>/dev/null | grep -o '"domain":"[^"]*' | sed 's/"domain":"/https:\/\//' | head -1)

if [ -z "$BACKEND_URL" ]; then
    echo -e "${YELLOW}⚠️  Could not auto-detect Railway URL${NC}"
    echo -e "${YELLOW}Please get it manually with: railway domain${NC}"
    read -p "Enter your Railway backend URL: " BACKEND_URL
fi

echo -e "${GREEN}✓ Backend deployed!${NC}"
echo -e "${GREEN}  URL: ${BACKEND_URL}${NC}"

# Test backend
echo -e "${YELLOW}🧪 Testing backend...${NC}"
sleep 10

HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "${BACKEND_URL}/health" || echo "000")
if [ "$HEALTH_CHECK" = "200" ]; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Backend might still be starting (HTTP $HEALTH_CHECK)${NC}"
fi

cd ..

# ==============================================================================
# DEPLOY FRONTEND TO VERCEL
# ==============================================================================

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🌐  DEPLOYING FRONTEND TO VERCEL${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

cd frontend

# Create or update vercel.json
echo -e "${YELLOW}Creating vercel.json...${NC}"
cat > vercel.json <<EOF
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "env": {
    "VITE_API_URL": "${BACKEND_URL}"
  }
}
EOF

# Update config file if it exists
if [ -f "src/config.ts" ]; then
    echo -e "${YELLOW}Updating src/config.ts...${NC}"
    if grep -q "API_BASE_URL" src/config.ts; then
        sed -i.bak "s|http://localhost:8000|${BACKEND_URL}|g" src/config.ts
        rm -f src/config.ts.bak
    else
        echo "export const API_BASE_URL = \"${BACKEND_URL}\";" >> src/config.ts
    fi
fi

if [ -f "src/config.js" ]; then
    echo -e "${YELLOW}Updating src/config.js...${NC}"
    sed -i.bak "s|http://localhost:8000|${BACKEND_URL}|g" src/config.js
    rm -f src/config.js.bak
fi

# Build
echo -e "${YELLOW}🏗️  Building frontend...${NC}"
npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Frontend build failed!${NC}"
    exit 1
fi

# Deploy to Vercel
echo -e "${YELLOW}🚀 Deploying to Vercel...${NC}"
vercel --prod --yes

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Vercel deployment failed!${NC}"
    exit 1
fi

# Get Vercel URL
FRONTEND_URL=$(vercel ls --prod 2>/dev/null | grep -o 'https://[^ ]*vercel.app' | head -1)

if [ -z "$FRONTEND_URL" ]; then
    echo -e "${YELLOW}⚠️  Could not auto-detect Vercel URL${NC}"
    read -p "Enter your Vercel frontend URL: " FRONTEND_URL
fi

echo -e "${GREEN}✓ Frontend deployed!${NC}"
echo -e "${GREEN}  URL: ${FRONTEND_URL}${NC}"

cd ..

# ==============================================================================
# UPDATE BACKEND CORS
# ==============================================================================

echo ""
echo -e "${YELLOW}🔧 Updating backend CORS...${NC}"

cd backend

# Update CORS to include Vercel URL
CORS_URLS="${FRONTEND_URL},${FRONTEND_URL/https:\/\//https://}/*.vercel.app"
railway variables set CORS_ORIGINS="${CORS_URLS}"

echo -e "${GREEN}✓ CORS updated${NC}"

cd ..

# ==============================================================================
# INITIALIZE SEARCH
# ==============================================================================

echo ""
echo -e "${YELLOW}🔍 Initializing search index...${NC}"

sleep 5
INIT_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/api/search/initialize" || echo "failed")

if echo "$INIT_RESPONSE" | grep -q "success\|ok\|created"; then
    echo -e "${GREEN}✓ Search index initialized${NC}"
else
    echo -e "${YELLOW}⚠️  Could not initialize search index automatically${NC}"
    echo "   Run manually: curl -X POST ${BACKEND_URL}/api/search/initialize"
fi

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
echo -e "${YELLOW}Frontend (Vercel):${NC}"
echo -e "  ${GREEN}${FRONTEND_URL}${NC}"
echo ""
echo -e "${YELLOW}Backend (Railway):${NC}"
echo -e "  URL:    ${GREEN}${BACKEND_URL}${NC}"
echo -e "  Docs:   ${GREEN}${BACKEND_URL}/docs${NC}"
echo -e "  Health: ${GREEN}${BACKEND_URL}/health${NC}"
echo ""
echo -e "${YELLOW}Search API:${NC}"
echo -e "  Health: ${GREEN}${BACKEND_URL}/api/search/health${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo ""
echo "1. Visit your app: ${FRONTEND_URL}"
echo "2. Test API docs: ${BACKEND_URL}/docs"
echo "3. Set up Elasticsearch (see VERCEL_DEPLOYMENT.md Step 1)"
echo "4. Configure environment variables:"
echo "   - Vercel: https://vercel.com/dashboard"
echo "   - Railway: railway variables"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo "  • Make sure Elasticsearch is configured"
echo "  • Add all API keys to Railway environment"
echo "  • Test search functionality"
echo "  • Set up custom domain (optional)"
echo ""
echo -e "${BLUE}📊 Monitor:${NC}"
echo "  • Vercel: https://vercel.com/dashboard"
echo "  • Railway: railway open"
echo ""
echo -e "${GREEN}🎉 Your Aperta app is live!${NC}"
echo ""

# Save URLs to file
cat > deployment-urls.txt <<EOF
Deployment completed: $(date)

Frontend: ${FRONTEND_URL}
Backend:  ${BACKEND_URL}

API Docs: ${BACKEND_URL}/docs
Health:   ${BACKEND_URL}/health
Search:   ${BACKEND_URL}/api/search/health

To redeploy:
  Frontend: cd frontend && vercel --prod
  Backend:  cd backend && railway up

To view logs:
  Frontend: vercel logs
  Backend:  railway logs
EOF

echo -e "${GREEN}✓ URLs saved to deployment-urls.txt${NC}"

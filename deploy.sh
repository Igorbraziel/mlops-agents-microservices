#!/bin/bash

# Colors for the terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"

echo -e "${BLUE}🚀 Starting microservices deployment in project: ${PROJECT_ID}${NC}\n"

# ── search-svc Deployment ──────────────────────────────────────────────────────
echo -e "${GREEN}📦 Deploying search-svc...${NC}"
gcloud run deploy search-svc \
  --source ./microservices/search-svc \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 2 \
  --quiet

SEARCH_URL=$(gcloud run services describe search-svc --platform managed --region $REGION --format 'value(status.url)')
echo -e "${GREEN}✅ search-svc online at: ${SEARCH_URL}${NC}\n"

# ── report-svc Deployment ──────────────────────────────────────────────────
echo -e "${GREEN}📄 Deploying report-svc...${NC}"
gcloud run deploy report-svc \
  --source ./microservices/report-svc \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 2 \
  --quiet

REPORT_URL=$(gcloud run services describe report-svc --platform managed --region $REGION --format 'value(status.url)')
echo -e "${GREEN}✅ report-svc online at: ${REPORT_URL}${NC}\n"

# ── Health Check Verification ──────────────────────────────────────────────
echo -e "${BLUE}🩺 Performing Health Check...${NC}"
curl -s "$SEARCH_URL/health" | grep -q "ok" && echo -e "search-svc: ${GREEN}OK${NC}" || echo "search-svc: FAIL"
curl -s "$REPORT_URL/health" | grep -q "ok" && echo -e "report-svc: ${GREEN}OK${NC}" || echo "report-svc: FAIL"

echo -e "\n${BLUE}🎯 Deployment completed! Update your .env file with the URLs above.${NC}"

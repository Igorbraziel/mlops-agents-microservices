#!/bin/bash

# Cores para o terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"

echo -e "${BLUE}🚀 Iniciando o deploy dos microsserviços no projeto: ${PROJECT_ID}${NC}\n"

# ── Deploy do search-svc ──────────────────────────────────────────────────────
echo -e "${GREEN}📦 Fazendo deploy do search-svc...${NC}"
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
echo -e "${GREEN}✅ search-svc online em: ${SEARCH_URL}${NC}\n"

# ── Deploy do report-svc ──────────────────────────────────────────────────
echo -e "${GREEN}📄 Fazendo deploy do report-svc...${NC}"
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
echo -e "${GREEN}✅ report-svc online em: ${REPORT_URL}${NC}\n"

# ── Verificação de Health Check ──────────────────────────────────────────────
echo -e "${BLUE}🩺 Realizando Health Check...${NC}"
curl -s "$SEARCH_URL/health" | grep -q "ok" && echo -e "search-svc: ${GREEN}OK${NC}" || echo "search-svc: FALHA"
curl -s "$REPORT_URL/health" | grep -q "ok" && echo -e "report-svc: ${GREEN}OK${NC}" || echo "report-svc: FALHA"

echo -e "\n${BLUE}🎯 Deploy concluído! Atualize seu arquivo .env com as URLs acima.${NC}"

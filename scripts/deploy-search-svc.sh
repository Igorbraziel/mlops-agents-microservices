#!/bin/bash
set -euo pipefail

# ── Cores para o terminal ─────────────────────────────────────────────────────
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ── Configurações ─────────────────────────────────────────────────────────────
REGION="${REGION:-us-central1}"
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

# ── Pré-checks ────────────────────────────────────────────────────────────────
if [[ -z "$PROJECT_ID" ]]; then
  echo -e "${RED}❌ Nenhum projeto GCP configurado. Execute: gcloud config set project SEU_PROJECT_ID${NC}"
  exit 1
fi

if ! gcloud auth print-access-token &>/dev/null; then
  echo -e "${RED}❌ Não autenticado no gcloud. Execute: gcloud auth login${NC}"
  exit 1
fi

echo -e "${BLUE}📦 Deploy do search-svc${NC}"
echo -e "${BLUE}   Projeto : ${PROJECT_ID}${NC}"
echo -e "${BLUE}   Região  : ${REGION}${NC}\n"

gcloud run deploy search-svc \
  --source ./microservices/search-svc \
  --region "$REGION" \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 2 \
  --quiet

SEARCH_URL=$(gcloud run services describe search-svc \
  --platform managed \
  --region "$REGION" \
  --format 'value(status.url)')

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ search-svc online em: ${SEARCH_URL}${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Health check

echo -e "\n${BLUE}🩺 Health check...${NC}"
if curl --silent --fail --max-time 10 "${SEARCH_URL}/health" | grep -q '"ok"'; then
  echo -e "${GREEN}✅ search-svc: OK${NC}"
else
  echo -e "${RED}❌ search-svc: FALHA${NC}"
  exit 1
fi

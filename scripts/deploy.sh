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

echo -e "${BLUE}🚀 Iniciando o deploy dos microsserviços${NC}"
echo -e "${BLUE}   Projeto : ${PROJECT_ID}${NC}"
echo -e "${BLUE}   Região  : ${REGION}${NC}\n"

# ── Função de health check ────────────────────────────────────────────────────
check_health() {
  local name="$1"
  local url="$2"
  if curl --silent --fail --max-time 10 "${url}/health" | grep -q '"ok"'; then
    echo -e "   ${GREEN}✅ ${name}: OK${NC}"
  else
    echo -e "   ${RED}❌ ${name}: FALHA (verifique os logs no Console GCP)${NC}"
  fi
}

# ── Deploy do search-svc ──────────────────────────────────────────────────────
echo -e "${GREEN}📦 [1/2] Fazendo deploy do search-svc...${NC}"
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
echo -e "${GREEN}✅ search-svc online em: ${SEARCH_URL}${NC}\n"

# ── Deploy do report-svc ──────────────────────────────────────────────────────
echo -e "${GREEN}📄 [2/2] Fazendo deploy do report-svc...${NC}"
gcloud run deploy report-svc \
  --source ./microservices/report-svc \
  --region "$REGION" \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 2 \
  --quiet

REPORT_URL=$(gcloud run services describe report-svc \
  --platform managed \
  --region "$REGION" \
  --format 'value(status.url)')
echo -e "${GREEN}✅ report-svc online em: ${REPORT_URL}${NC}\n"

# ── Health Checks ─────────────────────────────────────────────────────────────
echo -e "${BLUE}🩺 Verificando Health Checks...${NC}"
check_health "search-svc" "$SEARCH_URL"
check_health "report-svc" "$REPORT_URL"

# ── Resumo final ──────────────────────────────────────────────────────────────
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🎯 Deploy concluído! URLs dos serviços:${NC}"
echo -e "   SEARCH_SVC_URL=${SEARCH_URL}"
echo -e "   REPORT_SVC_URL=${REPORT_URL}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\n${BLUE}💡 Atualize seu .env local com as URLs acima para testes locais.${NC}"

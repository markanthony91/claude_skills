#!/bin/bash
# Importador n8n compatível com headers novos e antigos

WORKFLOW_DIR="/home/marcelo/Downloads/teste_backup_workflow_n8n/"
API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
N8N_URL="https://llm-server.taild42ed2.ts.net"

echo "📥 IMPORTAÇÃO EM MASSA DE WORKFLOWS"
echo "===================================="
echo ""

echo "🔍 Testando conexão (X-N8N-API-KEY)..."
RESP_A=$(curl -s -o /dev/null -w "%{http_code}" -H "X-N8N-API-KEY: $API_KEY" "$N8N_URL/rest/workflows")
if [ "$RESP_A" = "200" ]; then
  HEADER="X-N8N-API-KEY"
  echo "✅ Usando header: $HEADER"
else
  echo "🔄 Tentando header Authorization: Bearer..."
  RESP_B=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $API_KEY" "$N8N_URL/rest/workflows")
  if [ "$RESP_B" = "200" ]; then
    HEADER="Authorization: Bearer"
    echo "✅ Usando header: $HEADER"
  else
    echo "❌ Falha ao autenticar (401). Verifique o token e o endpoint."
    exit 1
  fi
fi

echo ""
echo "📊 Iniciando importação..."
for workflow_file in "$WORKFLOW_DIR"/*.json; do
  [ -f "$workflow_file" ] || continue
  FILENAME=$(basename "$workflow_file")
  echo "📄 Importando: $FILENAME"

  TMP_CLEAN="/tmp/clean_$FILENAME"
  jq 'del(.id, .versionId, .createdAt, .updatedAt, .tags, .shared, .meta, .pinData, .staticData)' "$workflow_file" > "$TMP_CLEAN"

  RESPONSE=$(curl -s -X POST "$N8N_URL/rest/workflows" \
    -H "Content-Type: application/json" \
    -H "$HEADER: $API_KEY" \
    -d @"$TMP_CLEAN")

  if echo "$RESPONSE" | grep -q '"id"'; then
    echo "   ✅ Sucesso!"
  else
    echo "   ❌ Falhou!"
    echo "   Erro: $RESPONSE"
  fi
  echo ""
done

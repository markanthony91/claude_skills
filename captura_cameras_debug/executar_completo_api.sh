#!/bin/bash
echo "🎯 EXECUÇÃO COMPLETA - API DESCOBERTA"
echo "====================================="
echo "1. Testa a API na porta 11967"
echo "2. Extrai as imagens automaticamente"
echo "====================================="

echo "🧪 PASSO 1: Testando API..."
python3 testar_api.py

if [ $? -eq 0 ]; then
    echo
    echo "🚀 PASSO 2: Executando extração..."
    python3 extrator_api_correto.py
else
    echo "❌ Teste da API falhou. Verifique a conectividade."
fi

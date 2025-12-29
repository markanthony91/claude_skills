#!/bin/bash
echo "🚀 EXECUÇÃO COMPLETA AUTOMÁTICA"
echo "================================"
echo "1. Investigar sistema"
echo "2. Extrair imagens automaticamente"
echo "================================"

echo "🕵️  PASSO 1: Investigando sistema..."
python3 investigar_site.py

echo
echo "🧠 PASSO 2: Executando extração inteligente..."
python3 extrator_auto_corrigido.py

echo
echo "🎉 EXECUÇÃO COMPLETA FINALIZADA!"

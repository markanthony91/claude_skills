#!/bin/bash
echo "🧪 TESTANDO NOVA ESTRUTURA (10 CÂMERAS)"
echo "======================================"
echo "🔧 VERSÃO COM VERIFICAÇÕES COMPLETAS"
echo "======================================"

# Verificar se os arquivos existem
if [ ! -f "test_estrutura.py" ]; then
    echo "❌ Arquivo test_estrutura.py não encontrado!"
    exit 1
fi

# Verificar Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python não encontrado!"
    exit 1
fi

$PYTHON_CMD test_estrutura.py

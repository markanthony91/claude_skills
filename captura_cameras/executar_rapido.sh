#!/bin/bash
echo "⚡ EXECUÇÃO RÁPIDA (SEM CONFIRMAÇÃO)"
echo "=================================="
echo "🔧 VERSÃO COM VERIFICAÇÕES COMPLETAS"
echo "=================================="

# Verificar se os arquivos existem
if [ ! -f "camera_downloader_complete.py" ]; then
    echo "❌ Arquivo camera_downloader_complete.py não encontrado!"
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

echo "s" | $PYTHON_CMD camera_downloader_complete.py

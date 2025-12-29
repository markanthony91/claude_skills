#!/bin/bash

# Script de execução com verificações de segurança

echo "🚀 EXECUTANDO DOWNLOADER COMPLETO"
echo "=================================="
echo "⚠️  PROCESSARÁ TODAS AS 345 CÂMERAS"
echo "⏱️  TEMPO ESTIMADO: ~12-15 minutos"
echo "🔧 VERSÃO COM VERIFICAÇÕES COMPLETAS"
echo "=================================="

# Verificar se os arquivos existem
if [ ! -f "camera_downloader_complete.py" ]; then
    echo "❌ Arquivo camera_downloader_complete.py não encontrado!"
    echo "   Execute primeiro: ./install_final.sh"
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

# Executar
$PYTHON_CMD camera_downloader_complete.py

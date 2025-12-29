#!/bin/bash
echo "🚀 EXTRATOR COM API CORRETA"
echo "============================"
echo "🌐 URL: http://35.209.243.66:11967 (PORTA CORRETA!)"
echo "📧 Login: bk@aiknow.ai"
echo "🏷️  Rótulos: d0, d1, d2, d3"
echo "📅 Data: 29/05/2025"
echo "============================"

if [ ! -f "extrator_api_correto.py" ]; then
    echo "❌ Arquivo extrator_api_correto.py não encontrado!"
    exit 1
fi

python3 extrator_api_correto.py

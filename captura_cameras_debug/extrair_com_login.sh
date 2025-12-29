#!/bin/bash
echo "🎯 EXTRATOR COM LOGIN - INTERFACE COMPLETA"
echo "=========================================="
echo "🔑 Login: bk@aiknow.ai"
echo "🌐 Site: http://35.209.243.66"
echo "🏷️  Rótulos: d0, d1, d2, d3"
echo "=========================================="

if [ ! -f "extrator_imagens_por_horario.py" ]; then
    echo "❌ Arquivo principal não encontrado!"
    exit 1
fi

python3 extrator_imagens_por_horario.py

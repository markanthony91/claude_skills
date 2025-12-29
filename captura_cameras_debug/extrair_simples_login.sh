#!/bin/bash
echo "⚡ EXTRATOR SIMPLES COM LOGIN"
echo "============================="
echo "🔑 Faz login automaticamente"
echo "📝 Configure no topo do arquivo:"
echo "   • Data (ANO, MES, DIA)"
echo "   • Horário (HORARIO_INICIO, HORARIO_FIM)"
echo "   • Lojas (LOJAS_ESPECIFICAS)"
echo "============================="

if [ ! -f "extrator_simples.py" ]; then
    echo "❌ Arquivo extrator_simples.py não encontrado!"
    exit 1
fi

python3 extrator_simples.py

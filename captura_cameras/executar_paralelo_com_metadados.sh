#!/bin/bash

# Script RÁPIDO: Download Paralelo + Metadados (2-3 minutos)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

print_color() {
    echo -e "${1}${2}${NC}"
}

clear
print_color $MAGENTA "
╔════════════════════════════════════════════════════════════════╗
║     🚀 DOWNLOAD PARALELO + METADADOS (Versão ULTRA RÁPIDA)   ║
╚════════════════════════════════════════════════════════════════╝
"

print_color $CYAN "⚡ VELOCIDADE MÁXIMA: 2-3 minutos para tudo!"
echo ""

print_color $GREEN "  📥 Download Paralelo:"
echo "     • 10 downloads simultâneos"
echo "     • Retry automático em caso de falha"
echo "     • ~2-3 minutos para 345 câmeras"
echo ""

print_color $GREEN "  📋 Extração de Metadados:"
echo "     • Lugar, Área, IPs, UUID, etc"
echo "     • Extração durante descoberta"
echo "     • Zero impacto na velocidade"
echo ""

print_color $GREEN "  💾 Resultado:"
echo "     • Imagens: cameras/Loja/*.jpg"
echo "     • Metadados: data/camera_metadata.json"
echo ""

print_color $CYAN "════════════════════════════════════════════════════════════════"
echo ""

# Detectar Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    print_color $RED "❌ Python não encontrado!"
    exit 1
fi

print_color $GREEN "✓ Python: $PYTHON_CMD"

# Verificar dependências
print_color $BLUE "\n🔍 Verificando dependências..."

$PYTHON_CMD -c "import selenium" &> /dev/null || {
    print_color $YELLOW "   ⚙️  Instalando Selenium..."
    pip3 install selenium chromedriver-autoinstaller
}

print_color $GREEN "✓ Dependências OK"

# Executar
print_color $CYAN "\n════════════════════════════════════════════════════════════════"
print_color $MAGENTA "\n🚀 Iniciando download paralelo com metadados..."
print_color $CYAN "════════════════════════════════════════════════════════════════"
echo ""

# Marcar início
inicio=$(date +%s)

$PYTHON_CMD parallel_downloader_com_metadados.py

# Calcular tempo
fim=$(date +%s)
duracao=$((fim - inicio))
minutos=$((duracao / 60))
segundos=$((duracao % 60))

# Verificar resultado
if [ $? -eq 0 ]; then
    print_color $CYAN "\n════════════════════════════════════════════════════════════════"
    print_color $GREEN "✅ EXECUÇÃO CONCLUÍDA COM SUCESSO!"
    print_color $CYAN "════════════════════════════════════════════════════════════════"

    echo ""
    print_color $MAGENTA "⚡ Tempo total: ${minutos}m ${segundos}s"
    echo ""

    # Contar resultados
    if [ -d "cameras" ]; then
        img_count=$(find cameras -name "*.jpg" -type f -mmin -10 | wc -l)
        total_img=$(find cameras -name "*.jpg" -type f | wc -l)
        print_color $GREEN "📸 Imagens baixadas agora: $img_count"
        print_color $BLUE "   Total de imagens: $total_img"
    fi

    if [ -f "data/camera_metadata.json" ]; then
        meta_count=$(python3 -c "import json; print(len(json.load(open('data/camera_metadata.json'))))" 2>/dev/null || echo "?")
        print_color $GREEN "📋 Metadados salvos: $meta_count câmeras"
    fi

    echo ""
    print_color $YELLOW "📋 Próximos passos:"
    echo ""
    print_color $BLUE "  1. Ver metadados:"
    print_color $CYAN "     python3 -c \"import json; from pprint import pprint; pprint(json.load(open('data/camera_metadata.json')), width=120)\" | less"
    echo ""
    print_color $BLUE "  2. Iniciar dashboard:"
    print_color $CYAN "     ./start_dashboard.sh"
    echo ""
    print_color $BLUE "  3. Visualizar no navegador:"
    print_color $CYAN "     http://localhost:5000"
    print_color $YELLOW "     (Ctrl+Shift+R para limpar cache)"
    echo ""

    print_color $CYAN "════════════════════════════════════════════════════════════════"
    print_color $MAGENTA "\n⚡ Download paralelo: ${minutos}m ${segundos}s"
    print_color $GREEN "🎉 Tudo pronto! Metadados + Imagens em tempo recorde!"
    print_color $CYAN "════════════════════════════════════════════════════════════════"
    echo ""

else
    print_color $RED "\n❌ Erro durante execução"
    exit 1
fi

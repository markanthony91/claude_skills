#!/bin/bash

# Script Unificado: Download de Imagens + Extração de Metadados

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_color() {
    echo -e "${1}${2}${NC}"
}

clear
print_color $CYAN "
╔════════════════════════════════════════════════════════════════╗
║     DOWNLOAD COMPLETO: IMAGENS + METADADOS (Versão Única)    ║
╚════════════════════════════════════════════════════════════════╝
"

print_color $BLUE "⚡ Este script faz TUDO em uma única execução:"
echo ""
print_color $GREEN "  1. 🔐 Login no AIVisual Dashboard"
print_color $GREEN "  2. 📹 Descoberta de TODAS as câmeras"
print_color $GREEN "  3. 📋 Extração de metadados (Lugar, Área, IPs, etc)"
print_color $GREEN "  4. 📸 Download de TODAS as imagens"
print_color $GREEN "  5. 💾 Salvamento de metadados em JSON"
echo ""

print_color $YELLOW "💡 Vantagens da versão integrada:"
echo "   • Faz tudo em UMA ÚNICA execução"
echo "   • NÃO impacta velocidade de download"
echo "   • Login apenas 1 vez (não 2)"
echo "   • Mais rápido e eficiente"
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

print_color $GREEN "✓ Python encontrado: $PYTHON_CMD"

# Executar
print_color $CYAN "\n════════════════════════════════════════════════════════════════"
print_color $BLUE "\n🚀 Iniciando execução completa..."
print_color $CYAN "════════════════════════════════════════════════════════════════"
echo ""

$PYTHON_CMD camera_downloader_com_metadados.py

# Verificar resultado
if [ $? -eq 0 ]; then
    print_color $CYAN "\n════════════════════════════════════════════════════════════════"
    print_color $GREEN "✅ EXECUÇÃO CONCLUÍDA COM SUCESSO!"
    print_color $CYAN "════════════════════════════════════════════════════════════════"

    echo ""
    print_color $YELLOW "📋 Arquivos gerados:"
    echo ""
    print_color $BLUE "  1. Imagens baixadas:"
    print_color $CYAN "     cameras/Nome_da_Loja/*.jpg"
    echo ""
    print_color $BLUE "  2. Metadados extraídos:"
    print_color $CYAN "     data/camera_metadata.json"
    echo ""

    # Contar arquivos
    if [ -d "cameras" ]; then
        img_count=$(find cameras -name "*.jpg" -type f | wc -l)
        print_color $GREEN "     ✓ $img_count imagens salvas"
    fi

    if [ -f "data/camera_metadata.json" ]; then
        meta_count=$(python3 -c "import json; print(len(json.load(open('data/camera_metadata.json'))))" 2>/dev/null || echo "?")
        print_color $GREEN "     ✓ $meta_count câmeras com metadados"
    fi

    echo ""
    print_color $YELLOW "📋 Próximos passos:"
    echo ""
    print_color $BLUE "  1. Visualizar metadados:"
    print_color $CYAN "     cat data/camera_metadata.json | python3 -m json.tool | less"
    echo ""
    print_color $BLUE "  2. Iniciar dashboard:"
    print_color $CYAN "     ./start_dashboard.sh"
    echo ""
    print_color $BLUE "  3. Ver no navegador:"
    print_color $CYAN "     http://localhost:5000"
    print_color $CYAN "     (Lembre-se: Ctrl+Shift+R para limpar cache)"
    echo ""
else
    print_color $RED "\n❌ Erro durante a execução"
    echo "   Verifique os logs acima"
    exit 1
fi

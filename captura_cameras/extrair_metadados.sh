#!/bin/bash

# Script para extrair metadados das câmeras do AIVisual

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Funções auxiliares
print_color() {
    echo -e "${1}${2}${NC}"
}

# Banner
clear
print_color $CYAN "
╔════════════════════════════════════════════════════════════════╗
║       EXTRATOR DE METADADOS - AIVISUAL DASHBOARD              ║
╚════════════════════════════════════════════════════════════════╝
"

print_color $BLUE "📋 O que este script faz:"
echo ""
print_color $GREEN "  1. 🔐 Faz login no dashboard AIVisual"
print_color $GREEN "  2. 📡 Extrai metadados de TODAS as câmeras P1:"
echo "     • Nome completo"
echo "     • Lugar (Drive_Thru, Salão, etc)"
echo "     • Área (Pedido, Caixa, etc)"
echo "     • IPs (local e internet)"
echo "     • UUID, MAC, Temperatura CPU"
echo "     • Versão do sistema"
echo ""
print_color $GREEN "  3. 📦 Copia dados compartilhados para P2 e P3:"
echo "     • Lugar, IP internet, Versão do sistema"
echo ""
print_color $GREEN "  4. 💾 Salva tudo em: data/camera_metadata.json"
echo ""

print_color $CYAN "════════════════════════════════════════════════════════════════"
echo ""

# Verificar se Python está disponível
if ! command -v python3 &> /dev/null; then
    print_color $RED "❌ Python3 não encontrado!"
    echo "   Instale Python 3: sudo apt install python3"
    exit 1
fi

print_color $GREEN "✓ Python3 encontrado"

# Verificar dependências
print_color $BLUE "\n🔍 Verificando dependências..."

python3 -c "import selenium" &> /dev/null || {
    print_color $YELLOW "⚙️  Instalando Selenium..."
    pip3 install selenium chromedriver-autoinstaller
}

print_color $GREEN "✓ Dependências OK"

# Executar extração
print_color $CYAN "\n════════════════════════════════════════════════════════════════"
print_color $BLUE "\n🚀 Iniciando extração de metadados..."
print_color $CYAN "════════════════════════════════════════════════════════════════"
echo ""

python3 extrair_metadados_aivisual.py

# Verificar resultado
if [ $? -eq 0 ]; then
    print_color $CYAN "\n════════════════════════════════════════════════════════════════"
    print_color $GREEN "✅ EXTRAÇÃO CONCLUÍDA COM SUCESSO!"
    print_color $CYAN "════════════════════════════════════════════════════════════════"

    echo ""
    print_color $YELLOW "📋 Próximos passos:"
    echo ""
    print_color $BLUE "  1. Visualizar metadados extraídos:"
    print_color $CYAN "     cat data/camera_metadata.json | python3 -m json.tool | less"
    echo ""
    print_color $BLUE "  2. Reiniciar o dashboard:"
    print_color $CYAN "     ./start_dashboard.sh"
    echo ""
    print_color $BLUE "  3. Abrir no navegador e limpar cache:"
    print_color $CYAN "     http://localhost:5000"
    print_color $CYAN "     Ctrl + Shift + R"
    echo ""
else
    print_color $RED "\n❌ Erro durante a extração"
    echo "   Verifique os logs acima para detalhes"
    exit 1
fi

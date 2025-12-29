#!/bin/bash

# Script de Instalação das Dependências de Visão Computacional
# Para análise de similaridade com IA

set -euo pipefail

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

# Banner
clear
print_color $CYAN "
╔════════════════════════════════════════════════════════════════╗
║        INSTALAÇÃO DE DEPENDÊNCIAS - ANÁLISE COM IA            ║
╚════════════════════════════════════════════════════════════════╝
"

# Detectar Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    print_color $RED "❌ Python não encontrado!"
    exit 1
fi

print_color $GREEN "✓ Python encontrado: $PYTHON_CMD"
echo ""

# Verificar se já está instalado
print_color $BLUE "🔍 Verificando dependências instaladas..."
echo ""

check_package() {
    if $PYTHON_CMD -c "import $1" &> /dev/null; then
        print_color $GREEN "  ✓ $1 já instalado"
        return 0
    else
        print_color $YELLOW "  ⚠ $1 não instalado"
        return 1
    fi
}

NEEDS_INSTALL=false

check_package "cv2" || NEEDS_INSTALL=true
check_package "skimage" || NEEDS_INSTALL=true
check_package "numpy" || NEEDS_INSTALL=true

echo ""

# Perguntar sobre Anthropic API
print_color $CYAN "════════════════════════════════════════════════════════════════"
print_color $YELLOW "🤖 Claude Vision API (Opcional)"
print_color $CYAN "════════════════════════════════════════════════════════════════"
echo ""
echo "Para análise avançada com IA, você pode configurar a API do Claude."
echo "Isso é OPCIONAL - o sistema funciona com apenas OpenCV."
echo ""
read -p "Deseja instalar o SDK do Claude? (s/N): " install_anthropic

if [[ $install_anthropic =~ ^[SsYy]$ ]]; then
    check_package "anthropic" || NEEDS_INSTALL=true
fi

echo ""

if [ "$NEEDS_INSTALL" = false ]; then
    print_color $GREEN "✅ Todas as dependências já estão instaladas!"
    exit 0
fi

# Instalar
print_color $CYAN "════════════════════════════════════════════════════════════════"
print_color $BLUE "📦 Instalando dependências..."
print_color $CYAN "════════════════════════════════════════════════════════════════"
echo ""

if [ -f "requirements_vision.txt" ]; then
    # Instalar apenas o necessário
    if [[ ! $install_anthropic =~ ^[SsYy]$ ]]; then
        # Instalar sem anthropic
        print_color $YELLOW "Instalando apenas OpenCV e dependências..."
        $PIP_CMD install opencv-python scikit-image numpy
    else
        # Instalar tudo
        print_color $YELLOW "Instalando todas as dependências..."
        $PIP_CMD install -r requirements_vision.txt
    fi
else
    print_color $RED "❌ Arquivo requirements_vision.txt não encontrado"
    print_color $YELLOW "Instalando manualmente..."

    $PIP_CMD install opencv-python scikit-image numpy

    if [[ $install_anthropic =~ ^[SsYy]$ ]]; then
        $PIP_CMD install anthropic
    fi
fi

echo ""
print_color $GREEN "✅ Instalação concluída!"
echo ""

# Configurar API Key se necessário
if [[ $install_anthropic =~ ^[SsYy]$ ]]; then
    echo ""
    print_color $CYAN "════════════════════════════════════════════════════════════════"
    print_color $YELLOW "🔑 Configuração da API Key (Opcional)"
    print_color $CYAN "════════════════════════════════════════════════════════════════"
    echo ""
    echo "Para usar a análise com Claude Vision, você precisa de uma API key."
    echo "Obtenha em: https://console.anthropic.com/settings/keys"
    echo ""
    read -p "Deseja configurar agora? (s/N): " config_key

    if [[ $config_key =~ ^[SsYy]$ ]]; then
        read -p "Cole sua API key: " api_key

        if [ -n "$api_key" ]; then
            echo "export ANTHROPIC_API_KEY='$api_key'" >> ~/.bashrc
            export ANTHROPIC_API_KEY="$api_key"
            print_color $GREEN "✓ API key configurada!"
            print_color $YELLOW "Execute: source ~/.bashrc"
        fi
    else
        echo ""
        print_color $YELLOW "Você pode configurar depois com:"
        print_color $BLUE "export ANTHROPIC_API_KEY='sua-key'"
    fi
fi

echo ""
print_color $CYAN "════════════════════════════════════════════════════════════════"
print_color $GREEN "🎉 Instalação completa!"
print_color $CYAN "════════════════════════════════════════════════════════════════"
echo ""
print_color $YELLOW "Próximos passos:"
echo "1. Inicie o dashboard: ./start_dashboard.sh"
echo "2. Clique no botão '🤖 Análise IA'"
echo "3. Clique em 'Aprender Referências'"
echo "4. Clique em 'Analisar Todas as Câmeras'"
echo ""
print_color $GREEN "Pronto! O sistema irá comparar automaticamente as imagens."
echo ""

#!/bin/bash

# Script de Inicialização do Dashboard de Câmeras
# Instala dependências e inicia o servidor Flask

set -euo pipefail

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
║        DASHBOARD DE CÂMERAS AIVISUAL - INICIALIZAÇÃO          ║
╚════════════════════════════════════════════════════════════════╝
"

# Garantir que estamos no diretório correto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_color $BLUE "📁 Diretório: $SCRIPT_DIR"
echo ""

# Detectar Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    print_color $RED "❌ Python não encontrado!"
    echo "   Por favor, instale Python 3.6 ou superior"
    exit 1
fi

print_color $GREEN "✓ Python encontrado: $PYTHON_CMD"

# Verificar se Flask está instalado
if ! $PYTHON_CMD -c "import flask" &> /dev/null; then
    print_color $YELLOW "⚙️  Flask não encontrado. Instalando..."

    if [ -f "requirements_dashboard.txt" ]; then
        $PIP_CMD install -r requirements_dashboard.txt
        print_color $GREEN "✓ Flask instalado com sucesso"
    else
        print_color $YELLOW "   Instalando Flask diretamente..."
        $PIP_CMD install Flask==3.0.0
    fi
else
    print_color $GREEN "✓ Flask já instalado"
fi

# Verificar estrutura de diretórios
print_color $BLUE "\n🔍 Verificando estrutura..."

for dir in templates static/css static/js data; do
    if [ ! -d "$dir" ]; then
        print_color $YELLOW "   Criando diretório: $dir"
        mkdir -p "$dir"
    fi
done

print_color $GREEN "✓ Estrutura verificada"

# Verificar se existem imagens
if [ ! -d "cameras" ] || [ -z "$(ls -A cameras 2>/dev/null)" ]; then
    print_color $YELLOW "\n⚠️  Atenção: Pasta 'cameras' vazia ou não existe"
    print_color $YELLOW "   Execute primeiro o download das câmeras:"
    print_color $CYAN "   ./executar_melhorado.sh"
    echo ""
    read -p "Deseja continuar mesmo assim? (s/N): " continuar

    if [[ ! $continuar =~ ^[SsYy]$ ]]; then
        print_color $BLUE "👋 Saindo..."
        exit 0
    fi
fi

# Informações
echo ""
print_color $CYAN "════════════════════════════════════════════════════════════════"
print_color $GREEN "🚀 Iniciando Dashboard..."
print_color $CYAN "════════════════════════════════════════════════════════════════"
echo ""
print_color $YELLOW "📌 Acesse o dashboard em:"
print_color $BLUE "   http://localhost:5000"
echo ""
print_color $YELLOW "📌 Para parar o servidor:"
print_color $BLUE "   Pressione Ctrl+C"
echo ""
print_color $CYAN "════════════════════════════════════════════════════════════════"
echo ""

# Iniciar Flask
$PYTHON_CMD app.py

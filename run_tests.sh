#!/bin/bash
# Script de Execução de Testes - captura_cameras
# ==============================================

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Testes - captura_cameras${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Função para exibir menu
show_menu() {
    echo -e "${YELLOW}Escolha uma opção:${NC}"
    echo "1. Executar todos os testes"
    echo "2. Testes unitários apenas"
    echo "3. Testes de integração apenas"
    echo "4. Testes com coverage (HTML)"
    echo "5. Testes de segurança apenas"
    echo "6. Testes rápidos (sem coverage)"
    echo "7. Teste específico"
    echo "8. Validar credentials"
    echo "9. Limpar cache de testes"
    echo "0. Sair"
    echo ""
}

# Função para executar comando
run_cmd() {
    echo -e "${BLUE}Executando: $1${NC}"
    eval $1
}

# Loop principal
while true; do
    show_menu
    read -p "Opção: " choice
    echo ""

    case $choice in
        1)
            echo -e "${GREEN}Executando todos os testes...${NC}"
            run_cmd "python -m pytest tests/ -v"
            ;;
        2)
            echo -e "${GREEN}Executando testes unitários...${NC}"
            run_cmd "python -m pytest tests/unit/ -v"
            ;;
        3)
            echo -e "${GREEN}Executando testes de integração...${NC}"
            run_cmd "python -m pytest tests/integration/ -v"
            ;;
        4)
            echo -e "${GREEN}Executando testes com coverage...${NC}"
            run_cmd "python -m pytest tests/ --cov=captura_cameras --cov=common --cov-report=html --cov-report=term"
            echo ""
            echo -e "${GREEN}Relatório HTML gerado em: htmlcov/index.html${NC}"
            echo -e "${YELLOW}Abrir relatório? (y/n)${NC}"
            read -p "" open_report
            if [ "$open_report" = "y" ] || [ "$open_report" = "Y" ]; then
                if command -v xdg-open &> /dev/null; then
                    xdg-open htmlcov/index.html
                elif command -v open &> /dev/null; then
                    open htmlcov/index.html
                else
                    echo -e "${YELLOW}Abra manualmente: htmlcov/index.html${NC}"
                fi
            fi
            ;;
        5)
            echo -e "${GREEN}Executando testes de segurança...${NC}"
            run_cmd "python -m pytest tests/ -m security -v"
            ;;
        6)
            echo -e "${GREEN}Executando testes rápidos (sem coverage)...${NC}"
            run_cmd "python -m pytest tests/ -v --no-cov"
            ;;
        7)
            echo -e "${YELLOW}Digite o caminho do teste (ex: tests/unit/test_config_manager.py):${NC}"
            read -p "" test_path
            echo -e "${GREEN}Executando $test_path...${NC}"
            run_cmd "python -m pytest $test_path -v"
            ;;
        8)
            echo -e "${GREEN}Validando credentials...${NC}"
            run_cmd "python3 common/credentials.py"
            ;;
        9)
            echo -e "${YELLOW}Limpando cache de testes...${NC}"
            run_cmd "rm -rf .pytest_cache __pycache__ .coverage htmlcov"
            run_cmd "find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true"
            run_cmd "find . -type f -name '*.pyc' -delete 2>/dev/null || true"
            echo -e "${GREEN}Cache limpo!${NC}"
            ;;
        0)
            echo -e "${GREEN}Saindo...${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Opção inválida!${NC}"
            ;;
    esac

    echo ""
    read -p "Pressione Enter para continuar..."
    clear
done

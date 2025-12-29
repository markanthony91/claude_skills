#!/bin/bash

# Script de Execução Melhorado - Sistema de Câmeras AIVisual
# Integra todas as melhorias: paralelo, retry, validação, limpeza

set -euo pipefail  # Exit em erro, undefined vars, pipe failures
IFS=$'\n\t'

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Trap para cleanup
trap 'echo -e "${RED}❌ Script interrompido${NC}"; exit 130' INT TERM

# Função para imprimir com cor
print_color() {
    echo -e "${1}${2}${NC}"
}

# Garantir execução no diretório correto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || { echo "❌ Falha ao mudar diretório"; exit 1; }

# Banner
clear
print_color $CYAN "
╔════════════════════════════════════════════════════════════════╗
║     SISTEMA DE CÂMERAS AIVISUAL - VERSÃO MELHORADA             ║
║                                                                ║
║  ✅ Download Paralelo (10x mais rápido)                        ║
║  ✅ Retry Automático (3 tentativas)                            ║
║  ✅ Validação de Imagem                                        ║
║  ✅ Logging em Arquivo                                         ║
║  ✅ Múltiplos Modos de Armazenamento                           ║
╚════════════════════════════════════════════════════════════════╝
"

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

# Verificar arquivo de configuração
if [ ! -f ".camera_config.json" ]; then
    print_color $YELLOW "⚙️  Primeira execução detectada"
    print_color $BLUE "   Executando configurador..."
    $PYTHON_CMD config_manager.py
fi

# Menu principal
while true; do
    echo ""
    print_color $CYAN "════════════════════════════════════════════════════════════════"
    print_color $CYAN "                      MENU PRINCIPAL"
    print_color $CYAN "════════════════════════════════════════════════════════════════"
    echo ""
    echo "  📸 EXECUÇÃO"
    echo "     1 - Download Paralelo (Recomendado - 2 min)"
    echo "     2 - Download Sequencial (Original - 16 min)"
    echo "     3 - Teste com 10 câmeras"
    echo ""
    echo "  ⚙️  CONFIGURAÇÃO"
    echo "     4 - Alterar configurações"
    echo "     5 - Comparar modos de armazenamento"
    echo "     6 - Ver recomendações"
    echo ""
    echo "  🧹 MANUTENÇÃO"
    echo "     7 - Estatísticas de armazenamento"
    echo "     8 - Limpar arquivos antigos"
    echo "     9 - Verificar integridade das imagens"
    echo ""
    echo "  📊 MONITORAMENTO"
    echo "     10 - Ver logs da última execução"
    echo "     11 - Relatório de falhas"
    echo ""
    echo "     0 - Sair"
    echo ""
    print_color $CYAN "════════════════════════════════════════════════════════════════"

    read -p "➡️  Escolha uma opção: " opcao

    case $opcao in
        1)
            print_color $BLUE "\n🚀 Iniciando Download Paralelo..."
            if [ -f "camera_downloader_main.py" ]; then
                LOGFILE="download_$(date +%Y%m%d_%H%M%S).log"
                print_color $YELLOW "📝 Log será salvo em: $LOGFILE"

                $PYTHON_CMD camera_downloader_main.py 2>&1 | tee "$LOGFILE"
                EXIT_CODE=${PIPESTATUS[0]}

                if [ $EXIT_CODE -eq 0 ]; then
                    print_color $GREEN "\n✅ Download concluído com sucesso!"
                else
                    print_color $RED "\n❌ Download falhou (código: $EXIT_CODE)"
                    print_color $YELLOW "   Verifique o log: $LOGFILE"
                fi
            else
                print_color $RED "❌ Arquivo camera_downloader_main.py não encontrado"
                print_color $YELLOW "   Execute: ./install_final.sh"
            fi
            read -p "Pressione Enter para continuar..."
            ;;

        2)
            print_color $BLUE "\n🐌 Iniciando Download Sequencial (Original)..."
            if [ -f "camera_downloader_complete.py" ]; then
                $PYTHON_CMD camera_downloader_complete.py
            else
                print_color $RED "❌ Arquivo não encontrado"
            fi
            read -p "Pressione Enter para continuar..."
            ;;

        3)
            print_color $BLUE "\n🧪 Teste com 10 câmeras..."
            if [ -f "test_estrutura.py" ]; then
                $PYTHON_CMD test_estrutura.py
            else
                print_color $RED "❌ Arquivo não encontrado"
            fi
            read -p "Pressione Enter para continuar..."
            ;;

        4)
            print_color $BLUE "\n⚙️  Abrindo configurador..."
            $PYTHON_CMD config_manager.py
            ;;

        5)
            print_color $BLUE "\n📊 Comparando modos de armazenamento..."
            $PYTHON_CMD config_manager.py --compare
            read -p "Pressione Enter para continuar..."
            ;;

        6)
            print_color $BLUE "\n💡 Recomendações de uso..."
            $PYTHON_CMD config_manager.py --recommend
            read -p "Pressione Enter para continuar..."
            ;;

        7)
            print_color $BLUE "\n📊 Estatísticas de armazenamento..."
            if [ -f "cleanup_manager.py" ]; then
                $PYTHON_CMD cleanup_manager.py --stats
            else
                print_color $RED "❌ Arquivo cleanup_manager.py não encontrado"
            fi
            read -p "Pressione Enter para continuar..."
            ;;

        8)
            print_color $BLUE "\n🧹 Limpeza de arquivos antigos..."
            if [ -f "cleanup_manager.py" ]; then
                read -p "Quantos dias manter? (padrão: 7): " dias
                dias=${dias:-7}

                read -p "Arquivar antes de deletar? (s/N): " arquivar

                if [[ $arquivar =~ ^[SsYy]$ ]]; then
                    $PYTHON_CMD cleanup_manager.py --dias $dias --arquivar
                else
                    $PYTHON_CMD cleanup_manager.py --dias $dias
                fi
            else
                print_color $RED "❌ Arquivo cleanup_manager.py não encontrado"
            fi
            read -p "Pressione Enter para continuar..."
            ;;

        9)
            print_color $BLUE "\n🔍 Verificando integridade das imagens..."

            total=$(find cameras/ -name "*.jpg" 2>/dev/null | wc -l)
            print_color $YELLOW "Analisando $total arquivos JPG..."

            invalidos=$(find cameras/ -name "*.jpg" -exec file {} \; 2>/dev/null | grep -v "JPEG image" | wc -l)

            if [ $invalidos -eq 0 ]; then
                print_color $GREEN "✅ Todos os $total arquivos são JPEGs válidos"
            else
                print_color $RED "❌ Encontrados $invalidos arquivos inválidos"
                print_color $YELLOW "   Lista:"
                find cameras/ -name "*.jpg" -exec file {} \; 2>/dev/null | grep -v "JPEG image"
            fi
            read -p "Pressione Enter para continuar..."
            ;;

        10)
            print_color $BLUE "\n📋 Logs da última execução..."

            ultimo_log=$(ls -t *.log 2>/dev/null | head -1)

            if [ -n "$ultimo_log" ]; then
                print_color $GREEN "Exibindo: $ultimo_log"
                echo ""
                tail -50 "$ultimo_log"
                echo ""
                read -p "Ver log completo? (s/N): " ver_completo
                if [[ $ver_completo =~ ^[SsYy]$ ]]; then
                    less "$ultimo_log"
                fi
            else
                print_color $YELLOW "Nenhum log encontrado"
            fi
            read -p "Pressione Enter para continuar..."
            ;;

        11)
            print_color $BLUE "\n❌ Relatório de falhas..."

            ultimo_log=$(ls -t *.log 2>/dev/null | head -1)

            if [ -n "$ultimo_log" ]; then
                print_color $GREEN "Analisando: $ultimo_log"
                echo ""
                grep -i "erro\|falha\|failed\|error" "$ultimo_log" || print_color $GREEN "✅ Nenhuma falha encontrada!"
            else
                print_color $YELLOW "Nenhum log encontrado"
            fi
            read -p "Pressione Enter para continuar..."
            ;;

        0)
            print_color $GREEN "\n👋 Até logo!"
            exit 0
            ;;

        *)
            print_color $RED "\n❌ Opção inválida"
            sleep 1
            ;;
    esac
done

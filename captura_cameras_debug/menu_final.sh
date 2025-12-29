#!/bin/bash
while true; do
    clear
    echo "🎯 MENU FINAL - EXTRATOR DE IMAGENS"
    echo "======================================"
    echo "🌐 API: http://35.209.243.66:11967"
    echo "🏷️  Rótulos: d0, d1, d2, d3"
    echo "✅ Porta correta descoberta!"
    echo "======================================"
    echo
    echo "1. 🧪 Testar API Descoberta"
    echo "2. 🚀 Extrair com API Correta"
    echo "3. 🎯 Execução Completa (Teste + Extração)"
    echo "4. 🕵️  Investigador Avançado"
    echo "5. ⚙️  Métodos Antigos (Experimentais)"
    echo "6. ❌ Sair"
    echo
    read -p "Escolha uma opção (1-6): " opcao
    
    case $opcao in
        1) ./testar_api_descoberta.sh; read -p "Pressione Enter...";;
        2) ./extrair_com_api.sh; read -p "Pressione Enter...";;
        3) ./executar_completo_api.sh; read -p "Pressione Enter...";;
        4) python3 investigador_avancado.py; read -p "Pressione Enter...";;
        5) 
            echo "Métodos antigos (experimentais):"
            echo "a) ./investigar.sh"
            echo "b) ./extrair_inteligente.sh"
            echo "c) ./extrair_com_login.sh"
            echo "d) ./extrair_simples_login.sh"
            read -p "Pressione Enter..."
            ;;
        6) echo "👋 Até logo!"; exit 0;;
        *) echo "❌ Opção inválida"; sleep 2;;
    esac
done

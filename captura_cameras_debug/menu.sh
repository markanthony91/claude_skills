#!/bin/bash
while true; do
    clear
    echo "🎯 MENU PRINCIPAL - EXTRATOR DE IMAGENS"
    echo "======================================"
    echo "🌐 Site: http://35.209.243.66"
    echo "🏷️  Rótulos: d0, d1, d2, d3"
    echo "======================================"
    echo
    echo "1. 🚀 Execução Completa (Recomendado)"
    echo "2. 🕵️  Investigar Site"
    echo "3. 🧠 Extrair Inteligente"
    echo "4. 📋 Interface Completa"
    echo "5. ⚡ Versão Rápida"
    echo "6. 🧪 Testar Sistema"
    echo "7. ❌ Sair"
    echo
    read -p "Escolha uma opção (1-7): " opcao
    
    case $opcao in
        1) ./executar_completo.sh; read -p "Pressione Enter...";;
        2) ./investigar.sh; read -p "Pressione Enter...";;
        3) ./extrair_inteligente.sh; read -p "Pressione Enter...";;
        4) ./extrair_com_login.sh; read -p "Pressione Enter...";;
        5) ./extrair_simples_login.sh; read -p "Pressione Enter...";;
        6) ./testar_sistema.sh; read -p "Pressione Enter...";;
        7) echo "👋 Até logo!"; exit 0;;
        *) echo "❌ Opção inválida"; sleep 2;;
    esac
done

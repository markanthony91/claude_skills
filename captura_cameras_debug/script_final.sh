# ==========================================
# SCRIPTS DE EXECUÇÃO - VERSÃO FINAL
# ==========================================

# 1. Script para testar a API descoberta
cat > testar_api_descoberta.sh << 'TESTEEOF'
#!/bin/bash
echo "🧪 TESTE DA API DESCOBERTA"
echo "=========================="
echo "🌐 URL: http://35.209.243.66:11967"
echo "📧 Login: bk@aiknow.ai"
echo "🔍 Testa todos os endpoints e estrutura"
echo "=========================="

python3 testar_api.py
TESTEEOF

# 2. Script para executar o extrator com API correta
cat > extrair_com_api.sh << 'APIEOF'
#!/bin/bash
echo "🚀 EXTRATOR COM API CORRETA"
echo "============================"
echo "🌐 URL: http://35.209.243.66:11967 (PORTA CORRETA!)"
echo "📧 Login: bk@aiknow.ai"
echo "🏷️  Rótulos: d0, d1, d2, d3"
echo "📅 Data: 29/05/2025"
echo "============================"

if [ ! -f "extrator_api_correto.py" ]; then
    echo "❌ Arquivo extrator_api_correto.py não encontrado!"
    exit 1
fi

python3 extrator_api_correto.py
APIEOF

# 3. Script completo (testa + extrai)
cat > executar_completo_api.sh << 'COMPLETOEOF'
#!/bin/bash
echo "🎯 EXECUÇÃO COMPLETA - API DESCOBERTA"
echo "====================================="
echo "1. Testa a API na porta 11967"
echo "2. Extrai as imagens automaticamente"
echo "====================================="

echo "🧪 PASSO 1: Testando API..."
python3 testar_api.py

if [ $? -eq 0 ]; then
    echo
    echo "🚀 PASSO 2: Executando extração..."
    python3 extrator_api_correto.py
else
    echo "❌ Teste da API falhou. Verifique a conectividade."
fi
COMPLETOEOF

# 4. Menu atualizado
cat > menu_final.sh << 'MENUEOF'
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
MENUEOF

# 5. Script de diagnóstico completo
cat > diagnosticar_completo.sh << 'DIAGEOF'
#!/bin/bash
echo "🔍 DIAGNÓSTICO COMPLETO DO SISTEMA"
echo "=================================="

echo "📋 1. Verificando arquivos principais..."
arquivos_principais=(
    "testar_api.py"
    "extrator_api_correto.py"
    "investigador_avancado.py"
)

for arquivo in "${arquivos_principais[@]}"; do
    if [ -f "$arquivo" ]; then
        echo "   ✅ $arquivo"
    else
        echo "   ❌ $arquivo (FALTANDO)"
    fi
done

echo
echo "📋 2. Verificando arquivos experimentais..."
arquivos_experimentais=(
    "investigar_site.py"
    "extrator_auto_corrigido.py"
    "extrator_simples.py"
)

for arquivo in "${arquivos_experimentais[@]}"; do
    if [ -f "$arquivo" ]; then
        echo "   ✅ $arquivo"
    else
        echo "   ⚠️  $arquivo (experimento)"
    fi
done

echo
echo "🌐 3. Testando conectividade..."
echo "   Porta 80 (antiga):"
if curl -s --connect-timeout 3 http://35.209.243.66 > /dev/null; then
    echo "      ✅ Acessível"
else
    echo "      ❌ Não acessível"
fi

echo "   Porta 11967 (correta):"
if curl -s --connect-timeout 3 http://35.209.243.66:11967 > /dev/null; then
    echo "      ✅ Acessível (API descoberta!)"
else
    echo "      ❌ Não acessível"
fi

echo
echo "🐍 4. Verificando Python e dependências..."
if command -v python3 &> /dev/null; then
    echo "   ✅ Python3 disponível"
    
    deps=("requests" "json")
    for dep in "${deps[@]}"; do
        if python3 -c "import $dep" 2>/dev/null; then
            echo "   ✅ $dep"
        else
            echo "   ❌ $dep (instale: pip install $dep)"
        fi
    done
else
    echo "   ❌ Python3 não encontrado"
fi

echo
echo "📁 5. Verificando estrutura de pastas..."
pastas=("imagens_api" "imagens_auto" "imagens_com_login")
for pasta in "${pastas[@]}"; do
    if [ -d "$pasta" ]; then
        count=$(find "$pasta" -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" 2>/dev/null | wc -l)
        echo "   ✅ $pasta/ ($count imagens)"
    else
        echo "   📁 $pasta/ (será criada automaticamente)"
    fi
done

echo
echo "🎯 RECOMENDAÇÃO:"
echo "   Use: ./executar_completo_api.sh"
echo "   Ou: ./menu_final.sh"
DIAGEOF

# Tornar todos executáveis
chmod +x *.sh

echo "✅ Scripts finais criados:"
echo "   • testar_api_descoberta.sh    (Testa API na porta 11967)"
echo "   • extrair_com_api.sh          (Extrator com API correta)"
echo "   • executar_completo_api.sh    (Tudo automático)"
echo "   • menu_final.sh               (Menu completo)"
echo "   • diagnosticar_completo.sh    (Diagnóstico detalhado)"
echo
echo "🚀 RECOMENDADO: ./executar_completo_api.sh"

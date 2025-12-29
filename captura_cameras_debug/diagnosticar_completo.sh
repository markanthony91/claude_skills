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

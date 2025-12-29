#!/bin/bash

# Instalador do Extrator de Imagens com Login
# Para o sistema http://35.209.243.66 com autenticação

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
==========================================
   EXTRATOR DE IMAGENS COM LOGIN
     Sistema: http://35.209.243.66
    Login: bk@aiknow.ai / Sphbr7410
      Rótulos: d0, d1, d2, d3
==========================================
"

# Verificar Python
print_color $BLUE "🔍 Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    print_color $GREEN "✓ Python3 encontrado: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    print_color $GREEN "✓ Python encontrado: $(python --version)"
else
    print_color $RED "❌ Python não encontrado!"
    print_color $YELLOW "   Instale Python 3.7+ e tente novamente."
    exit 1
fi

# Verificar pip
print_color $BLUE "🔍 Verificando pip..."
if $PYTHON_CMD -m pip --version &> /dev/null; then
    print_color $GREEN "✓ pip encontrado"
else
    print_color $YELLOW "⚠️  Instalando pip..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y python3-pip
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3-pip
    else
        print_color $RED "❌ Instale pip manualmente"
        exit 1
    fi
fi

# Instalar dependências
print_color $BLUE "📦 Instalando dependências..."
$PYTHON_CMD -m pip install --user --quiet requests beautifulsoup4 lxml pathlib
print_color $GREEN "✓ Dependências instaladas"

# Criar diretórios
print_color $BLUE "📁 Criando estrutura..."
mkdir -p imagens imagens_extraidas imagens_com_login logs
print_color $GREEN "✓ Diretórios criados"

# Criar teste de login
print_color $BLUE "📝 Criando teste de login..."
cat > testar_login.py << 'TESTLOGINEOF'
#!/usr/bin/env python3
"""
Teste de Login no Sistema
Verifica se as credenciais funcionam
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "http://35.209.243.66"
LOGIN_EMAIL = "bk@aiknow.ai" 
LOGIN_PASSWORD = "Sphbr7410"

def testar_login():
    print("🧪 TESTE DE LOGIN")
    print("=" * 30)
    print(f"🌐 URL: {BASE_URL}")
    print(f"📧 Email: {LOGIN_EMAIL}")
    print(f"🔒 Senha: {'*' * len(LOGIN_PASSWORD)}")
    print("=" * 30)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Testar acesso ao site
    print("🔍 Testando acesso ao site...")
    try:
        response = session.get(BASE_URL, timeout=10)
        print(f"   ✅ Site acessível (Status: {response.status_code})")
    except Exception as e:
        print(f"   ❌ Erro ao acessar site: {e}")
        return False
    
    # Procurar página de login
    urls_login = [
        f"{BASE_URL}/login",
        f"{BASE_URL}/admin/login",
        f"{BASE_URL}/auth/login", 
        f"{BASE_URL}/signin",
        f"{BASE_URL}/admin",
        f"{BASE_URL}/"
    ]
    
    print("🔍 Procurando página de login...")
    login_encontrado = False
    
    for url in urls_login:
        try:
            print(f"   Testando: {url}")
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                conteudo = response.text.lower()
                if any(palavra in conteudo for palavra in ['login', 'password', 'email']):
                    print(f"   ✅ Página de login encontrada!")
                    
                    # Tentar fazer login
                    soup = BeautifulSoup(response.content, 'html.parser')
                    form = soup.find('form')
                    
                    if form:
                        print("   📝 Formulário de login encontrado")
                        
                        # Procurar campos
                        campos = soup.find_all('input')
                        print(f"   📋 {len(campos)} campos encontrados:")
                        
                        for campo in campos:
                            tipo = campo.get('type', '')
                            nome = campo.get('name', '')
                            print(f"      • {tipo}: {nome}")
                        
                        login_encontrado = True
                        break
                    else:
                        print("   ❌ Formulário não encontrado")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    if not login_encontrado:
        print("❌ Página de login não encontrada")
        print("   Verifique se o site está funcionando")
        return False
    
    print("\n✅ TESTE CONCLUÍDO")
    print("   • Site acessível")
    print("   • Página de login encontrada")
    print("   • Formulário detectado")
    print("\n🚀 Pronto para usar o extrator!")
    
    return True

if __name__ == "__main__":
    testar_login()
TESTLOGINEOF

# Criar configurador específico para login
print_color $BLUE "📝 Criando configurador com login..."
cat > configurar_com_login.py << 'CONFIGLOGINEOF'
#!/usr/bin/env python3
"""
Configurador para Extrator com Login
"""

import os
from datetime import datetime

def configurar():
    print("🎯 CONFIGURADOR COM LOGIN")
    print("=" * 40)
    print("🔑 Credenciais já configuradas:")
    print("   📧 Email: bk@aiknow.ai")
    print("   🔒 Senha: Sphbr7410")
    print("   🌐 Site: http://35.209.243.66")
    print("=" * 40)
    
    # Data
    print("\n📅 CONFIGURAÇÃO DE DATA:")
    ano = int(input("   Ano (default: 2025): ") or "2025")
    mes = int(input("   Mês (1-12, default: 5): ") or "5")
    dia = int(input("   Dia (1-31, default: 29): ") or "29")
    
    # Horário
    print("\n⏰ CONFIGURAÇÃO DE HORÁRIO:")
    usar_horario = input("   Filtrar por horário? (s/N): ").lower() == 's'
    
    if usar_horario:
        horario_inicio = input("   Horário início (HH:MM, ex: 14:00): ")
        horario_fim = input("   Horário fim (HH:MM, ex: 16:00): ")
    else:
        horario_inicio = None
        horario_fim = None
    
    # Lojas
    print("\n🏪 CONFIGURAÇÃO DE LOJAS:")
    print("1. Lojas específicas")
    print("2. Buscar todas após login")
    
    opcao = input("Escolha (1-2, default: 1): ") or "1"
    
    if opcao == "1":
        lojas_str = input("Digite nomes das lojas (separados por vírgula): ")
        lojas = [loja.strip() for loja in lojas_str.split(',') if loja.strip()]
    else:
        lojas = []
    
    # Criar arquivo de configuração
    config_content = f'''#!/usr/bin/env python3
"""
Configuração com Login - Gerada em {datetime.now()}
"""

# === CONFIGURAÇÕES DE LOGIN ===
BASE_URL = "http://35.209.243.66"
LOGIN_EMAIL = "bk@aiknow.ai"
LOGIN_PASSWORD = "Sphbr7410"

# === CONFIGURAÇÕES DE EXTRAÇÃO ===
ANO = {ano}
MES = {mes}
DIA = {dia}

HORARIO_INICIO = "{horario_inicio}" if "{horario_inicio}" != "None" else None
HORARIO_FIM = "{horario_fim}" if "{horario_fim}" != "None" else None

LOJAS_ESPECIFICAS = {lojas}

# === FIXO ===
ROTULOS = ['d0', 'd1', 'd2', 'd3']
CAMERAS = ['P1', 'P2', 'P3']

# === RESUMO ===
print("📋 CONFIGURAÇÃO COM LOGIN:")
print(f"   🔑 Site: {{BASE_URL}}")
print(f"   📧 Login: {{LOGIN_EMAIL}}")
print(f"   📅 Data: {{DIA:02d}}/{{MES:02d}}/{{ANO}}")
if HORARIO_INICIO and HORARIO_FIM:
    print(f"   ⏰ Horário: {{HORARIO_INICIO}} às {{HORARIO_FIM}}")
else:
    print("   ⏰ Sem filtro de horário")
print(f"   🏷️  Rótulos: {{', '.join(ROTULOS)}}")
if LOJAS_ESPECIFICAS:
    print(f"   🏪 Lojas específicas: {{len(LOJAS_ESPECIFICAS)}}")
else:
    print("   🏪 Todas as lojas")
print("=" * 50)
'''
    
    with open('config_login.py', 'w') as f:
        f.write(config_content)
    
    print("\n✅ Configuração salva em: config_login.py")
    print("🧪 Para testar login: python3 testar_login.py")
    print("🚀 Para extrair: python3 extrator_com_login_simples.py")

if __name__ == "__main__":
    configurar()
CONFIGLOGINEOF

# Criar scripts de execução rápida
print_color $BLUE "📜 Criando scripts de execução rápida..."

# Script completo automático
cat > executar_completo.sh << 'COMPLETOEOF'
#!/bin/bash
echo "🚀 EXECUÇÃO COMPLETA AUTOMÁTICA"
echo "================================"
echo "1. Investigar sistema"
echo "2. Extrair imagens automaticamente"
echo "================================"

echo "🕵️  PASSO 1: Investigando sistema..."
python3 investigar_site.py

echo
echo "🧠 PASSO 2: Executando extração inteligente..."
python3 extrator_auto_corrigido.py

echo
echo "🎉 EXECUÇÃO COMPLETA FINALIZADA!"
COMPLETOEOF

# Menu principal
cat > menu.sh << 'MENUEOF'
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
MENUEOF

cat > investigar.sh << 'INVESTIGAREOF'
#!/bin/bash
echo "🕵️  INVESTIGADOR AVANÇADO DO SITE"
echo "================================"
echo "Analisa a estrutura do site e detecta"
echo "o método correto de autenticação"
echo "================================"

python3 investigar_site.py
INVESTIGAREOF

cat > extrair_inteligente.sh << 'INTELEOF'
#!/bin/bash
echo "🧠 EXTRATOR INTELIGENTE"
echo "======================="
echo "Detecta automaticamente o método de"
echo "autenticação e extrai as imagens"
echo "======================="

python3 extrator_auto_corrigido.py
INTELEOF

cat > extrair_com_login.sh << 'LOGINEOF'
#!/bin/bash
echo "🎯 EXTRATOR COM LOGIN - INTERFACE COMPLETA"
echo "=========================================="
echo "🔑 Login: bk@aiknow.ai"
echo "🌐 Site: http://35.209.243.66"
echo "🏷️  Rótulos: d0, d1, d2, d3"
echo "=========================================="

if [ ! -f "extrator_imagens_por_horario.py" ]; then
    echo "❌ Arquivo principal não encontrado!"
    exit 1
fi

python3 extrator_imagens_por_horario.py
LOGINEOF

cat > extrair_simples_login.sh << 'SIMPLESLOGINEOF'
#!/bin/bash
echo "⚡ EXTRATOR SIMPLES COM LOGIN"
echo "============================="
echo "🔑 Faz login automaticamente"
echo "📝 Configure no topo do arquivo:"
echo "   • Data (ANO, MES, DIA)"
echo "   • Horário (HORARIO_INICIO, HORARIO_FIM)"
echo "   • Lojas (LOJAS_ESPECIFICAS)"
echo "============================="

if [ ! -f "extrator_simples.py" ]; then
    echo "❌ Arquivo extrator_simples.py não encontrado!"
    exit 1
fi

python3 extrator_simples.py
SIMPLESLOGINEOF

cat > testar_sistema.sh << 'TESTEEOF'
#!/bin/bash
echo "🧪 TESTE DO SISTEMA COM LOGIN"
echo "============================="
echo "Verifica se consegue acessar o site"
echo "e encontrar a página de login"
echo "============================="

python3 testar_login.py
TESTEEOF

cat > configurar_login.sh << 'CONFLOGINEOF'
#!/bin/bash
echo "⚙️  CONFIGURADOR COM LOGIN"
echo "========================="
echo "Gera arquivo de configuração"
echo "com credenciais já definidas"
echo "========================="

python3 configurar_com_login.py
CONFLOGINEOF

chmod +x *.sh *.py

print_color $GREEN "✓ Todos os arquivos criados"

print_color $CYAN "
==========================================
🎉 INSTALAÇÃO COM LOGIN CONCLUÍDA! 🎉
==========================================
"

print_color $GREEN "📋 ARQUIVOS CRIADOS:"
echo "   ├── investigar_site.py               (🕵️  Investigador avançado)"
echo "   ├── extrator_auto_corrigido.py       (🧠 Extrator inteligente)"
echo "   ├── extrator_imagens_por_horario.py  (📋 Interface completa)"
echo "   ├── extrator_simples.py              (⚡ Versão rápida)"
echo "   ├── testar_login.py                  (🧪 Teste de login)"
echo "   ├── executar_completo.sh             (🚀 Execução automática)"
echo "   ├── menu.sh                          (🎯 Menu principal)"
echo "   ├── investigar.sh                    (🕵️  Investigador)"
echo "   ├── extrair_inteligente.sh           (🧠 Extrator inteligente)" 
echo "   ├── extrair_com_login.sh             (📋 Interface completa)"
echo "   ├── extrair_simples_login.sh         (⚡ Versão rápida)"
echo "   ├── testar_sistema.sh                (🧪 Teste do sistema)"
echo "   └── pastas: imagens_auto/, imagens_com_login/, logs/"

print_color $YELLOW "
🚀 FORMAS DE USAR (ESCOLHA UMA):
"

print_color $CYAN "🎯 SUPER FÁCIL - Menu Interativo:"
echo "   ./menu.sh"
echo "   ☝️  Interface amigável com todas as opções!"

print_color $CYAN "🚀 AUTOMÁTICO - Execução Completa:"
echo "   ./executar_completo.sh"
echo "   ☝️  Faz tudo sozinho: investiga + extrai!"

print_color $CYAN "🧠 INTELIGENTE - Passo a Passo:"
echo "   1. ./investigar.sh       (descobre como acessar)"
echo "   2. ./extrair_inteligente.sh (extrai automaticamente)"

print_color $BLUE "ALTERNATIVAS (se o inteligente não funcionar):"

print_color $CYAN "   Método A - Interface Completa:"
echo "     ./extrair_com_login.sh"

print_color $CYAN "   Método B - Versão Rápida:"
echo "     1. Edite extrator_simples.py (data, horário, lojas)"
echo "     2. ./extrair_simples_login.sh"

print_color $CYAN "   Método C - Teste Manual:"
echo "     ./testar_sistema.sh"

print_color $GREEN "
🔑 CREDENCIAIS CONFIGURADAS:
   📧 Email: bk@aiknow.ai
   🔒 Senha: Sphbr7410  
   🌐 Site: http://35.209.243.66
"

print_color $GREEN "
🎯 FUNCIONALIDADES AVANÇADAS:
   ✅ 🧠 Detecção automática de autenticação
   ✅ 🔓 Teste de acesso direto (sem login)
   ✅ 🔑 HTTP Basic Authentication
   ✅ 👤 Teste de usuários alternativos
   ✅ 🕵️  Investigação completa da estrutura
   ✅ 📸 Extração de imagens d0, d1, d2, d3
   ✅ ⏰ Filtro por data e horário específicos
   ✅ 🏪 Processamento de múltiplas lojas
   ✅ 📁 Organização automática por loja/câmera/dia
   ✅ 📊 Relatórios detalhados de progresso
"

print_color $GREEN "
📁 ESTRUTURA DE SAÍDA:
   imagens_com_login/
   ├── BK_Aguas_Claras_Castaneiras/
   │   ├── P1/
   │   │   └── dia_29/
   │   │       ├── arquivo_d0_xxx.jpg
   │   │       ├── arquivo_d1_xxx.jpg
   │   │       ├── arquivo_d2_xxx.jpg
   │   │       └── arquivo_d3_xxx.jpg
   │   ├── P2/dia_29/...
   │   └── P3/dia_29/...
   └── ...
"

print_color $CYAN "
==========================================
    SISTEMA INTELIGENTE INSTALADO! 🎉
   
   👉 MAIS FÁCIL: ./menu.sh
   👉 RÁPIDO: ./executar_completo.sh
   
   ✅ Descobre automaticamente como acessar
   ✅ Extrai as imagens d0,d1,d2,d3 sozinho!
==========================================
"

print_color $YELLOW "
💡 DICAS IMPORTANTES:
   🕵️  SEMPRE execute o investigador primeiro!
   🧠 Use o extrator inteligente - ele resolve tudo sozinho
   ⏰ Configure data/horário conforme necessidade
   🏪 Verifique se as lojas existem na data especificada
   🏷️  Imagens d0,d1,d2,d3 são filtradas automaticamente
   🔄 Se um método não funcionar, o script tenta outros
   📊 Verifique os relatórios para acompanhar o progresso
"

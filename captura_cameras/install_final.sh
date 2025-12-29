#!/bin/bash

# Script de instalação da versão FINAL COMPLETA - TOTALMENTE CORRIGIDO
# Processa TODAS as câmeras com estrutura organizada
# Inclui verificação e instalação automática do Chrome

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

# Função para detectar o sistema operacional
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            echo "debian"
        elif [ -f /etc/redhat-release ]; then
            echo "redhat"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Função para verificar se o Chrome está instalado
check_chrome() {
    local chrome_paths=(
        "google-chrome"
        "google-chrome-stable"
        "chromium"
        "chromium-browser"
        "/usr/bin/google-chrome"
        "/usr/bin/google-chrome-stable"
        "/usr/bin/chromium"
        "/usr/bin/chromium-browser"
        "/opt/google/chrome/chrome"
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    )
    
    for path in "${chrome_paths[@]}"; do
        if command -v "$path" &> /dev/null; then
            print_color $GREEN "✓ Chrome encontrado: $path"
            return 0
        fi
    done
    
    return 1
}

# Função para instalar Chrome
install_chrome() {
    local os=$(detect_os)
    
    print_color $YELLOW "🔧 Instalando Google Chrome para $os..."
    
    case $os in
        "debian")
            # Ubuntu/Debian
            print_color $BLUE "📦 Atualizando repositórios..."
            sudo apt update -qq
            
            print_color $BLUE "📦 Instalando dependências..."
            sudo apt install -y wget curl gnupg2 software-properties-common apt-transport-https ca-certificates
            
            print_color $BLUE "📦 Adicionando repositório do Google Chrome..."
            wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
            echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
            
            print_color $BLUE "📦 Instalando Google Chrome..."
            sudo apt update -qq
            sudo apt install -y google-chrome-stable
            ;;
        "redhat")
            # CentOS/RHEL/Fedora
            print_color $BLUE "📦 Instalando Google Chrome via dnf/yum..."
            sudo dnf install -y https://dl.google.com/linux/direct/google-chrome-stable-current_x86_64.rpm 2>/dev/null || \
            sudo yum install -y https://dl.google.com/linux/direct/google-chrome-stable-current_x86_64.rpm
            ;;
        "macos")
            # macOS
            if command -v brew &> /dev/null; then
                print_color $BLUE "📦 Instalando via Homebrew..."
                brew install --cask google-chrome
            else
                print_color $RED "❌ Homebrew não encontrado. Instale manualmente:"
                print_color $YELLOW "   https://www.google.com/chrome/"
                return 1
            fi
            ;;
        *)
            print_color $RED "❌ Sistema operacional não suportado para instalação automática"
            print_color $YELLOW "   Instale o Google Chrome manualmente:"
            print_color $YELLOW "   https://www.google.com/chrome/"
            return 1
            ;;
    esac
    
    # Verificar se a instalação foi bem-sucedida
    if check_chrome; then
        print_color $GREEN "✅ Chrome instalado com sucesso!"
        return 0
    else
        print_color $RED "❌ Falha na instalação do Chrome"
        return 1
    fi
}

clear
print_color $CYAN "
========================================
   INSTALADOR VERSÃO FINAL CORRIGIDA
     DOWNLOADER DE CÂMERAS AIVISUAL
          (Todas as 345 câmeras)
       COM VERIFICAÇÃO DE DEPENDÊNCIAS
========================================
"

# Verificar se está executando como root (não recomendado)
if [[ $EUID -eq 0 ]]; then
    print_color $YELLOW "⚠️  Executando como root. Isso pode causar problemas com algumas dependências."
    print_color $YELLOW "   Recomendamos executar como usuário normal."
fi

# Verificar Python
print_color $BLUE "🔍 Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1)
    print_color $GREEN "✓ Python3 encontrado: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version 2>&1)
    print_color $GREEN "✓ Python encontrado: $PYTHON_VERSION"
else
    print_color $RED "❌ Python não encontrado!"
    print_color $YELLOW "   Instale Python 3.7+ e tente novamente."
    exit 1
fi

# Verificar pip
print_color $BLUE "🔍 Verificando pip..."
if $PYTHON_CMD -m pip --version &> /dev/null; then
    print_color $GREEN "✓ pip encontrado"
elif command -v pip3 &> /dev/null; then
    print_color $GREEN "✓ pip3 encontrado"
elif command -v pip &> /dev/null; then
    print_color $GREEN "✓ pip encontrado"
else
    print_color $YELLOW "⚠️  pip não encontrado. Tentando instalar..."
    
    # Tentar instalar pip
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y python3-pip
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3-pip
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3-pip
    else
        print_color $RED "❌ Não foi possível instalar pip automaticamente"
        print_color $YELLOW "   Instale pip manualmente e tente novamente"
        exit 1
    fi
    
    if $PYTHON_CMD -m pip --version &> /dev/null; then
        print_color $GREEN "✓ pip instalado com sucesso"
    else
        print_color $RED "❌ Falha na instalação do pip"
        exit 1
    fi
fi

# Verificar Chrome
print_color $BLUE "🔍 Verificando Google Chrome..."
if check_chrome; then
    print_color $GREEN "✓ Chrome já está instalado"
else
    print_color $YELLOW "⚠️  Google Chrome não encontrado"
    print_color $YELLOW "   O script precisa do Chrome para funcionar"
    
    echo
    read -p "🤔 Deseja instalar o Google Chrome automaticamente? (s/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        if install_chrome; then
            print_color $GREEN "✅ Chrome instalado com sucesso!"
        else
            print_color $RED "❌ Falha na instalação do Chrome"
            print_color $YELLOW "   Instale manualmente: https://www.google.com/chrome/"
            exit 1
        fi
    else
        print_color $RED "❌ Chrome é necessário para o funcionamento"
        print_color $YELLOW "   Instale manualmente: https://www.google.com/chrome/"
        exit 1
    fi
fi

# Instalar dependências Python
print_color $BLUE "📦 Instalando dependências Python..."
print_color $YELLOW "   Isso pode levar alguns minutos..."

# Lista de dependências com versões específicas para compatibilidade
DEPENDENCIAS=(
    "requests>=2.25.0"
    "selenium>=4.0.0"
    "chromedriver-autoinstaller>=0.4.0"
    "pathlib"
)

for dep in "${DEPENDENCIAS[@]}"; do
    print_color $BLUE "   → Instalando $dep..."
    if $PYTHON_CMD -m pip install --user --quiet --upgrade "$dep"; then
        print_color $GREEN "     ✓ $dep instalado"
    else
        print_color $YELLOW "     ⚠️  Tentando sem --user..."
        if $PYTHON_CMD -m pip install --quiet --upgrade "$dep"; then
            print_color $GREEN "     ✓ $dep instalado"
        else
            print_color $RED "     ❌ Falha ao instalar $dep"
            exit 1
        fi
    fi
done

print_color $GREEN "✓ Todas as dependências foram instaladas"

# Criar diretórios
print_color $BLUE "📁 Criando estrutura de diretórios..."
mkdir -p cameras logs cameras_teste
print_color $GREEN "✓ Diretórios criados"

# Criar arquivo de teste melhorado
print_color $BLUE "📝 Criando arquivo de teste melhorado..."
cat > test_estrutura.py << 'TESTEOF'
#!/usr/bin/env python3
"""
TESTE da Nova Estrutura - 10 Câmeras
Versão com verificação completa de dependências
"""

import sys
import os
import subprocess

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    dependencias = {
        'requests': 'requests',
        'selenium': 'selenium',
        'chromedriver_autoinstaller': 'chromedriver-autoinstaller'
    }
    
    print("🔍 Verificando dependências Python...")
    
    for modulo, nome_pip in dependencias.items():
        try:
            __import__(modulo)
            print(f"   ✓ {nome_pip}")
        except ImportError:
            print(f"   ❌ {nome_pip} não encontrado")
            print(f"   📦 Instalando {nome_pip}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", nome_pip])
                print(f"   ✓ {nome_pip} instalado")
            except:
                print(f"   ❌ Falha ao instalar {nome_pip}")
                return False
    return True

def verificar_chrome():
    """Verifica se o Chrome está disponível"""
    import shutil
    
    chrome_executables = [
        'google-chrome',
        'google-chrome-stable',
        'chromium',
        'chromium-browser'
    ]
    
    for exe in chrome_executables:
        if shutil.which(exe):
            print(f"   ✓ Chrome encontrado: {exe}")
            return True
    
    print("   ❌ Chrome não encontrado no PATH")
    return False

def testar_chrome_selenium():
    """Testa se o Selenium consegue inicializar o Chrome"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        import chromedriver_autoinstaller
        
        print("🧪 Testando Selenium + Chrome...")
        
        # Instalar chromedriver
        chromedriver_autoinstaller.install()
        
        # Configurar Chrome em modo headless
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--remote-debugging-port=9222')
        
        # Tentar inicializar
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('about:blank')
        driver.quit()
        
        print("   ✓ Selenium + Chrome funcionando")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no teste: {e}")
        return False

# Resto do código do teste original...
import requests
import base64
from datetime import datetime
from pathlib import Path
import time
import re

BASE_URL = "https://dashboard.aivisual.ai"
USERNAME = "bk@aiknow.ai"
PASSWORD = "nR}CMryIT,8/5!3i9"

def extrair_nome_loja(nome_camera):
    try:
        nome_limpo = nome_camera.replace("BK - ", "")
        nome_limpo = re.sub(r'_P[123]$', '', nome_limpo)
        nome_pasta = nome_limpo.replace(" - ", "_").replace(" ", "_")
        nome_pasta = "".join(c for c in nome_pasta if c.isalnum() or c in "_-")
        return nome_pasta, nome_limpo
    except:
        return "Loja_Desconhecida", "Loja Desconhecida"

def download_base64_image(image_url):
    try:
        if image_url.startswith('data:image/'):
            header, data = image_url.split(',', 1)
            return base64.b64decode(data)
        else:
            response = requests.get(image_url, timeout=30)
            return response.content if response.status_code == 200 else None
    except:
        return None

def testar_nova_estrutura():
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        import chromedriver_autoinstaller
        
        print("🧪 TESTE DA NOVA ESTRUTURA - 10 CÂMERAS")
        print("=" * 50)
        print("📁 Estrutura: cameras_teste/Nome_da_Loja/P1_Nome_da_Loja_timestamp.jpg")
        print("=" * 50)
        
        chromedriver_autoinstaller.install()
        
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--remote-debugging-port=9222')
        
        driver = webdriver.Chrome(options=chrome_options)
        session = requests.Session()
        
        sucessos = []
        falhas = []
        
        try:
            print("🔑 Fazendo login...")
            driver.get(f"{BASE_URL}/login")
            time.sleep(3)
            
            wait = WebDriverWait(driver, 15)
            email_field = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, 'input[type="email"], input[name="email"]'
            )))
            email_field.clear()
            email_field.send_keys(USERNAME)
            
            password_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            password_field.clear()
            password_field.send_keys(PASSWORD)
            
            login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()
            time.sleep(5)
            
            driver.get(f"{BASE_URL}/admin/iots")
            time.sleep(3)
            
            selenium_cookies = driver.get_cookies()
            for cookie in selenium_cookies:
                session.cookies.set(cookie['name'], cookie['value'])
            
            elementos = driver.find_elements(By.CSS_SELECTOR, '[data-cam-id]')
            if not elementos:
                elementos = driver.find_elements(By.CSS_SELECTOR, '.cameraCard')
            if not elementos:
                elementos = driver.find_elements(By.XPATH, "//*[contains(text(), 'BK -')]")
            
            cameras_teste = []
            for i, elemento in enumerate(elementos[:10]):
                try:
                    cam_id = elemento.get_attribute('data-cam-id') or f"test_{i}"
                    texto = elemento.text
                    
                    nome = f"Camera_{i}"
                    if "BK -" in texto:
                        linhas = texto.split("\n")
                        for linha in linhas:
                            if "BK -" in linha:
                                nome = linha.strip()
                                break
                    
                    tipo_camera = "P1"
                    if "_P2" in nome or " P2" in nome:
                        tipo_camera = "P2"
                    elif "_P3" in nome or " P3" in nome:
                        tipo_camera = "P3"
                    
                    nome_pasta_loja, nome_loja_display = extrair_nome_loja(nome)
                    
                    cameras_teste.append({
                        'id': cam_id,
                        'nome': nome,
                        'tipo': tipo_camera,
                        'loja_pasta': nome_pasta_loja,
                        'loja_nome': nome_loja_display
                    })
                except:
                    continue
            
            print(f"🎯 Testando {len(cameras_teste)} câmeras com nova estrutura...")
            print()
            
            for i, camera in enumerate(cameras_teste, 1):
                try:
                    print(f"📸 [{i:2d}/10] {camera['loja_nome']} ({camera['tipo']})...", end=" ")
                    
                    response = session.get(
                        f"{BASE_URL}/admin/get/iots/getLastImage",
                        params={'iot': camera['id']},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        image_url = data.get('image')
                        
                        if image_url:
                            img_data = download_base64_image(image_url)
                            
                            if img_data:
                                pasta_loja = Path("cameras_teste") / camera['loja_pasta']
                                pasta_loja.mkdir(parents=True, exist_ok=True)
                                
                                agora = datetime.now().strftime("%Y%m%d_%H%M%S")
                                nome_arquivo = f"{camera['tipo']}_{camera['loja_pasta']}_{agora}.jpg"
                                
                                caminho = pasta_loja / nome_arquivo
                                with open(caminho, 'wb') as f:
                                    f.write(img_data)
                                
                                print(f"✅ {nome_arquivo}")
                                sucessos.append({
                                    'loja': camera['loja_nome'],
                                    'tipo': camera['tipo'],
                                    'arquivo': str(caminho),
                                    'tamanho': len(img_data)
                                })
                            else:
                                print("❌ Download falhou")
                                falhas.append(f"{camera['loja_nome']} ({camera['tipo']}): Falha no download")
                        else:
                            print("❌ Sem URL")
                            falhas.append(f"{camera['loja_nome']} ({camera['tipo']}): Sem URL da imagem")
                    else:
                        print(f"❌ HTTP {response.status_code}")
                        falhas.append(f"{camera['loja_nome']} ({camera['tipo']}): HTTP {response.status_code}")
                
                except Exception as e:
                    print("❌ Erro")
                    falhas.append(f"{camera['loja_nome']} ({camera['tipo']}): {str(e)}")
                
                time.sleep(1)
            
            print("\n" + "=" * 60)
            print("📊 RESULTADO DO TESTE")
            print("=" * 60)
            print(f"✅ Sucessos: {len(sucessos)}")
            print(f"❌ Falhas: {len(falhas)}")
            
            if sucessos:
                print(f"\n🎉 ESTRUTURA FUNCIONANDO! Arquivos criados:")
                
                lojas = {}
                for s in sucessos:
                    loja = s['loja']
                    if loja not in lojas:
                        lojas[loja] = []
                    lojas[loja].append(s)
                
                for loja, arquivos in lojas.items():
                    print(f"\n📁 cameras_teste/{arquivos[0]['arquivo'].split('/')[-2]}/")
                    for arquivo in arquivos:
                        nome_arquivo = arquivo['arquivo'].split('/')[-1]
                        tamanho_kb = arquivo['tamanho'] // 1024
                        print(f"   └── {nome_arquivo} ({tamanho_kb} KB)")
                
                print(f"\n🚀 TESTE APROVADO! Execute o completo:")
                print("   ./executar_todas_cameras.sh")
            
            if falhas:
                print(f"\n❌ Falhas encontradas:")
                for falha in falhas:
                    print(f"   • {falha}")
            
        finally:
            driver.quit()
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 TESTE DE ESTRUTURA COM VERIFICAÇÕES COMPLETAS")
    print("=" * 50)
    
    # Verificar tudo antes de começar
    if not verificar_dependencias():
        print("❌ Falha na verificação das dependências")
        sys.exit(1)
    
    if not verificar_chrome():
        print("❌ Chrome não encontrado")
        sys.exit(1)
    
    if not testar_chrome_selenium():
        print("❌ Falha no teste do Selenium + Chrome")
        sys.exit(1)
    
    print("✅ Todas as verificações passaram!")
    print()
    
    testar_nova_estrutura()
    input("\nPressione Enter para sair...")
TESTEOF

# Criar arquivo principal completo melhorado
print_color $BLUE "📝 Criando downloader completo melhorado..."
cat > camera_downloader_complete.py << 'MAINEOF'
#!/usr/bin/env python3
"""
Downloader Completo de Câmeras AIVisual
Processa TODAS as câmeras com estrutura organizada por loja
Versão com verificação completa de dependências
"""

import sys
import os
import subprocess
import requests
import base64
from datetime import datetime
from pathlib import Path
import time
import re

BASE_URL = "https://dashboard.aivisual.ai"
USERNAME = "bk@aiknow.ai"
PASSWORD = "nR}CMryIT,8/5!3i9"
DELAY_ENTRE_CAMERAS = 2

def verificar_e_instalar_dependencias():
    """Verifica e instala dependências necessárias"""
    dependencias = {
        'requests': 'requests>=2.25.0',
        'selenium': 'selenium>=4.0.0',
        'chromedriver_autoinstaller': 'chromedriver-autoinstaller>=0.4.0'
    }
    
    print("🔍 Verificando dependências Python...")
    
    for modulo, nome_pip in dependencias.items():
        try:
            __import__(modulo.replace('-', '_'))
            print(f"   ✓ {modulo}")
        except ImportError:
            print(f"   ❌ {modulo} não encontrado")
            print(f"   📦 Instalando {nome_pip}...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "--user", "--upgrade", nome_pip
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"   ✓ {modulo} instalado")
            except:
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", "--upgrade", nome_pip
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"   ✓ {modulo} instalado (global)")
                except:
                    print(f"   ❌ Falha ao instalar {modulo}")
                    return False
    return True

def verificar_chrome():
    """Verifica se o Chrome está disponível"""
    import shutil
    
    chrome_executables = [
        'google-chrome',
        'google-chrome-stable',
        'chromium',
        'chromium-browser'
    ]
    
    print("🔍 Verificando Google Chrome...")
    for exe in chrome_executables:
        if shutil.which(exe):
            print(f"   ✓ Chrome encontrado: {exe}")
            return True
    
    print("   ❌ Chrome não encontrado no PATH")
    print("   📋 Instale o Chrome:")
    print("      Ubuntu/Debian: sudo apt install google-chrome-stable")
    print("      CentOS/RHEL: sudo dnf install google-chrome-stable")
    print("      Ou baixe: https://www.google.com/chrome/")
    return False

def testar_selenium():
    """Testa se o Selenium consegue funcionar"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        import chromedriver_autoinstaller
        
        print("🧪 Testando Selenium + Chrome...")
        
        # Instalar chromedriver
        chromedriver_autoinstaller.install()
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('about:blank')
        driver.quit()
        
        print("   ✓ Selenium funcionando")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no Selenium: {e}")
        return False

def extrair_nome_loja(nome_camera):
    try:
        nome_limpo = nome_camera.replace("BK - ", "")
        nome_limpo = re.sub(r'_P[123]$', '', nome_limpo)
        nome_pasta = nome_limpo.replace(" - ", "_").replace(" ", "_")
        nome_pasta = "".join(c for c in nome_pasta if c.isalnum() or c in "_-")
        return nome_pasta, nome_limpo
    except:
        return "Loja_Desconhecida", "Loja Desconhecida"

def download_base64_image(image_url):
    try:
        if image_url.startswith('data:image/'):
            header, data = image_url.split(',', 1)
            return base64.b64decode(data)
        else:
            response = requests.get(image_url, timeout=30)
            return response.content if response.status_code == 200 else None
    except:
        return None

def fazer_login_e_baixar():
    try:
        print("🔧 VERIFICAÇÕES INICIAIS")
        print("=" * 40)
        
        # Verificar todas as dependências
        if not verificar_e_instalar_dependencias():
            print("❌ Falha na verificação das dependências")
            return False
        
        if not verificar_chrome():
            print("❌ Chrome não disponível")
            return False
        
        if not testar_selenium():
            print("❌ Selenium não funcionando")
            return False
        
        print("✅ Todas as verificações passaram!")
        print()
        
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        import chromedriver_autoinstaller
        
        print("🚀 DOWNLOADER COMPLETO - TODAS AS CÂMERAS AIVISUAL")
        print("=" * 60)
        print(f"⚙️  Delay entre câmeras: {DELAY_ENTRE_CAMERAS} segundos")
        print("📁 Estrutura: cameras/Nome_da_Loja/P1_Nome_da_Loja_timestamp.jpg")
        print("=" * 60)
        
        chromedriver_autoinstaller.install()
        
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')  # Acelerar carregamento
        
        driver = webdriver.Chrome(options=chrome_options)
        session = requests.Session()
        
        cameras_processadas = []
        cameras_com_sucesso = []
        cameras_com_falha = []
        lojas_processadas = set()
        
        try:
            print("🔑 Fazendo login...")
            
            driver.get(f"{BASE_URL}/login")
            time.sleep(3)
            
            wait = WebDriverWait(driver, 15)
            
            email_field = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, 'input[type="email"], input[name="email"]'
            )))
            email_field.clear()
            email_field.send_keys(USERNAME)
            
            password_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            password_field.clear()
            password_field.send_keys(PASSWORD)
            
            login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()
            
            print("⏳ Aguardando login...")
            time.sleep(5)
            
            driver.get(f"{BASE_URL}/admin/iots")
            time.sleep(3)
            
            print("📹 Buscando todas as câmeras...")
            
            print("📜 Carregando todas as câmeras (scroll automático)...")
            last_height = driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 20  # Evitar loop infinito
            
            while scroll_attempts < max_scrolls:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1
                print(f"   → Scroll {scroll_attempts}/20...")
            
            selenium_cookies = driver.get_cookies()
            for cookie in selenium_cookies:
                session.cookies.set(cookie['name'], cookie['value'])
            
            cameras_encontradas = []
            
            # Múltiplas estratégias de busca
            seletores = [
                '[data-cam-id]',
                '.cameraCard',
                '[data-id*="cam"]',
                '.camera-item',
                '[class*="camera"]'
            ]
            
            elementos = []
            for seletor in seletores:
                elementos_encontrados = driver.find_elements(By.CSS_SELECTOR, seletor)
                if elementos_encontrados:
                    elementos = elementos_encontrados
                    print(f"   ✓ Usando seletor: {seletor}")
                    break
            
            # Fallback com XPath
            if not elementos:
                elementos = driver.find_elements(By.XPATH, "//*[contains(text(), 'BK -')]")
                if elementos:
                    print("   ✓ Usando busca por texto 'BK -'")
            
            print(f"🔍 Analisando {len(elementos)} elementos...")
            
            for i, elemento in enumerate(elementos):
                try:
                    # Múltiplas tentativas de obter ID
                    cam_id = (
                        elemento.get_attribute('data-cam-id') or
                        elemento.get_attribute('data-id') or
                        elemento.get_attribute('id') or
                        elemento.get_attribute('data-camera-id') or
                        f"camera_{i}"
                    )
                    
                    texto = elemento.text
                    
                    nome = f"Camera_{i}"
                    if "Nome:" in texto:
                        nome = texto.split("Nome:")[1].split("\n")[0].strip()
                    elif "BK -" in texto:
                        linhas = texto.split("\n")
                        for linha in linhas:
                            if "BK -" in linha:
                                nome = linha.strip()
                                break
                    
                    # Detectar tipo de câmera
                    tipo_camera = "P1"
                    if "_P2" in nome or " P2" in nome:
                        tipo_camera = "P2"
                    elif "_P3" in nome or " P3" in nome:
                        tipo_camera = "P3"
                    
                    nome_pasta_loja, nome_loja_display = extrair_nome_loja(nome)
                    
                    cameras_encontradas.append({
                        'id': cam_id,
                        'nome': nome,
                        'tipo': tipo_camera,
                        'loja_pasta': nome_pasta_loja,
                        'loja_nome': nome_loja_display
                    })
                    
                    if len(cameras_encontradas) % 50 == 0:
                        print(f"  → Processadas {len(cameras_encontradas)} câmeras...")
                    
                except Exception as e:
                    continue
            
            print(f"✅ Total de câmeras encontradas: {len(cameras_encontradas)}")
            
            if len(cameras_encontradas) == 0:
                print("❌ Nenhuma câmera encontrada!")
                print("   Verifique se o login foi bem-sucedido")
                print("   e se a página carregou corretamente")
                return False
            
            lojas_unicas = set()
            for cam in cameras_encontradas:
                lojas_unicas.add(cam['loja_nome'])
            
            print(f"🏪 Total de lojas identificadas: {len(lojas_unicas)}")
            print("=" * 60)
            
            inicio_processamento = time.time()
            
            for i, camera in enumerate(cameras_encontradas, 1):
                try:
                    print(f"📸 [{i:3d}/{len(cameras_encontradas)}] {camera['loja_nome']} ({camera['tipo']})...", end=" ")
                    
                    cameras_processadas.append(camera)
                    
                    response = session.get(
                        f"{BASE_URL}/admin/get/iots/getLastImage",
                        params={'iot': camera['id']},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            image_url = data.get('image')
                            
                            if image_url:
                                img_data = download_base64_image(image_url)
                                
                                if img_data:
                                    pasta_loja = Path("cameras") / camera['loja_pasta']
                                    pasta_loja.mkdir(parents=True, exist_ok=True)
                                    
                                    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    nome_arquivo = f"{camera['tipo']}_{camera['loja_pasta']}_{agora}.jpg"
                                    
                                    caminho_completo = pasta_loja / nome_arquivo
                                    with open(caminho_completo, 'wb') as f:
                                        f.write(img_data)
                                    
                                    print(f"✅ ({len(img_data):,} bytes)")
                                    cameras_com_sucesso.append({
                                        'camera': camera,
                                        'arquivo': str(caminho_completo),
                                        'tamanho': len(img_data)
                                    })
                                    
                                    lojas_processadas.add(camera['loja_nome'])
                                else:
                                    print("❌ Falha download")
                                    cameras_com_falha.append({
                                        'camera': camera,
                                        'erro': 'Falha no download da imagem'
                                    })
                            else:
                                print("❌ Sem URL")
                                cameras_com_falha.append({
                                    'camera': camera,
                                    'erro': 'URL da imagem não encontrada'
                                })
                        except Exception as json_error:
                            print(f"❌ Erro JSON")
                            cameras_com_falha.append({
                                'camera': camera,
                                'erro': f'Erro JSON: {str(json_error)}'
                            })
                    else:
                        print(f"❌ HTTP {response.status_code}")
                        cameras_com_falha.append({
                            'camera': camera,
                            'erro': f'Erro HTTP: {response.status_code}'
                        })
                
                except Exception as e:
                    print(f"❌ Erro geral")
                    cameras_com_falha.append({
                        'camera': camera,
                        'erro': f'Erro geral: {str(e)}'
                    })
                
                if i < len(cameras_encontradas):
                    time.sleep(DELAY_ENTRE_CAMERAS)
                
                # Progress report
                if i % 25 == 0:
                    tempo_decorrido = time.time() - inicio_processamento
                    tempo_estimado = (tempo_decorrido / i) * len(cameras_encontradas)
                    tempo_restante = tempo_estimado - tempo_decorrido
                    print(f"⏱️  Progresso: {i}/{len(cameras_encontradas)} | Tempo restante: {tempo_restante/60:.1f}min")
            
            tempo_total = time.time() - inicio_processamento
            
            # Relatório final
            print("\n" + "=" * 80)
            print("📊 RELATÓRIO FINAL COMPLETO")
            print("=" * 80)
            print(f"🎯 Total de câmeras encontradas: {len(cameras_encontradas)}")
            print(f"✅ Downloads bem-sucedidos: {len(cameras_com_sucesso)}")
            print(f"❌ Falhas: {len(cameras_com_falha)}")
            print(f"🏪 Lojas com imagens: {len(lojas_processadas)}")
            print(f"⏱️  Tempo total: {tempo_total/60:.1f} minutos")
            
            if len(cameras_encontradas) > 0:
                taxa_sucesso = len(cameras_com_sucesso) / len(cameras_encontradas) * 100
                print(f"📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
            
            print(f"💾 Imagens salvas em: ./cameras/")
            
            # Estatísticas por tipo
            print(f"\n📊 Por tipo de câmera:")
            tipos = {}
            for sucesso in cameras_com_sucesso:
                tipo = sucesso['camera']['tipo']
                tipos[tipo] = tipos.get(tipo, 0) + 1
            
            for tipo, count in sorted(tipos.items()):
                print(f"   {tipo}: {count} imagens")
            
            # Lista de lojas
            if lojas_processadas:
                print(f"\n🏪 Lojas com imagens capturadas ({len(lojas_processadas)}):")
                for loja in sorted(lojas_processadas):
                    cameras_loja = sum(1 for s in cameras_com_sucesso if s['camera']['loja_nome'] == loja)
                    print(f"   • {loja} ({cameras_loja} câmeras)")
            
            # Relatório de falhas
            if cameras_com_falha:
                print(f"\n❌ CÂMERAS COM FALHA ({len(cameras_com_falha)}):")
                
                falhas_por_loja = {}
                for falha in cameras_com_falha:
                    loja = falha['camera']['loja_nome']
                    if loja not in falhas_por_loja:
                        falhas_por_loja[loja] = []
                    falhas_por_loja[loja].append(falha)
                
                for loja, falhas in sorted(falhas_por_loja.items()):
                    print(f"\n   🏪 {loja}:")
                    for falha in falhas:
                        print(f"      • {falha['camera']['tipo']}: {falha['erro']}")
            
            print("\n" + "=" * 80)
            if len(cameras_com_sucesso) > 0:
                print("🎉 PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
            else:
                print("⚠️  PROCESSAMENTO CONCLUÍDO - VERIFICAR FALHAS")
            print("=" * 80)
            
            return True
            
        finally:
            driver.quit()
    
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚨 ATENÇÃO: Este script baixará TODAS as câmeras!")
    print("   Isso pode levar bastante tempo...")
    print("   Certifique-se de ter conexão estável com a internet")
    print()
    
    resposta = input("🤔 Deseja continuar? (s/N): ")
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        sucesso = fazer_login_e_baixar()
        if not sucesso:
            print("\n❌ Execução não foi bem-sucedida")
            print("   Verifique os erros acima e tente novamente")
    else:
        print("❌ Cancelado pelo usuário.")
    
    input("\nPressione Enter para sair...")
MAINEOF

# Scripts de execução melhorados
print_color $BLUE "📜 Criando scripts de execução melhorados..."

cat > executar_todas_cameras.sh << 'EXECEOF'
#!/bin/bash

# Script de execução com verificações de segurança

echo "🚀 EXECUTANDO DOWNLOADER COMPLETO"
echo "=================================="
echo "⚠️  PROCESSARÁ TODAS AS 345 CÂMERAS"
echo "⏱️  TEMPO ESTIMADO: ~12-15 minutos"
echo "🔧 VERSÃO COM VERIFICAÇÕES COMPLETAS"
echo "=================================="

# Verificar se os arquivos existem
if [ ! -f "camera_downloader_complete.py" ]; then
    echo "❌ Arquivo camera_downloader_complete.py não encontrado!"
    echo "   Execute primeiro: ./install_final.sh"
    exit 1
fi

# Verificar Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python não encontrado!"
    exit 1
fi

# Executar
$PYTHON_CMD camera_downloader_complete.py
EXECEOF

cat > executar_rapido.sh << 'RAPIDEOF'
#!/bin/bash
echo "⚡ EXECUÇÃO RÁPIDA (SEM CONFIRMAÇÃO)"
echo "=================================="
echo "🔧 VERSÃO COM VERIFICAÇÕES COMPLETAS"
echo "=================================="

# Verificar se os arquivos existem
if [ ! -f "camera_downloader_complete.py" ]; then
    echo "❌ Arquivo camera_downloader_complete.py não encontrado!"
    exit 1
fi

# Verificar Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python não encontrado!"
    exit 1
fi

echo "s" | $PYTHON_CMD camera_downloader_complete.py
RAPIDEOF

cat > testar_estrutura.sh << 'TESTEEOF'
#!/bin/bash
echo "🧪 TESTANDO NOVA ESTRUTURA (10 CÂMERAS)"
echo "======================================"
echo "🔧 VERSÃO COM VERIFICAÇÕES COMPLETAS"
echo "======================================"

# Verificar se os arquivos existem
if [ ! -f "test_estrutura.py" ]; then
    echo "❌ Arquivo test_estrutura.py não encontrado!"
    exit 1
fi

# Verificar Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python não encontrado!"
    exit 1
fi

$PYTHON_CMD test_estrutura.py
TESTEEOF

# Tornar executáveis
chmod +x *.sh *.py

print_color $GREEN "✓ Todos os arquivos criados e configurados"

print_color $CYAN "
========================================
🎉 INSTALAÇÃO CORRIGIDA CONCLUÍDA! 🎉
     VERSÃO COM TODAS AS VERIFICAÇÕES
========================================
"

print_color $GREEN "📋 ARQUIVOS CRIADOS:"
echo "   ├── camera_downloader_complete.py  (versão final com verificações)"
echo "   ├── test_estrutura.py              (teste com verificações completas)"
echo "   ├── executar_todas_cameras.sh      (executa com confirmação)"
echo "   ├── executar_rapido.sh             (executa sem confirmação)"
echo "   ├── testar_estrutura.sh            (testa nova estrutura)"
echo "   ├── cameras/                       (pasta para imagens)"
echo "   ├── cameras_teste/                 (pasta para testes)"
echo "   └── logs/                          (pasta para logs)"

print_color $YELLOW "
🚀 COMO EXECUTAR:
"
echo "1. PRIMEIRO - Teste a estrutura:"
print_color $CYAN "   ./testar_estrutura.sh"

echo
echo "2. Se o teste OK - Execute completo:"
print_color $CYAN "   ./executar_todas_cameras.sh"

echo
echo "3. RÁPIDO - Sem confirmação:"
print_color $CYAN "   ./executar_rapido.sh"

print_color $GREEN "
🔧 MELHORIAS DESTA VERSÃO:
   ✅ Verificação automática do Chrome
   ✅ Instalação automática do Chrome (se necessário)
   ✅ Verificação completa de dependências Python
   ✅ Instalação automática de pip (se necessário)
   ✅ Múltiplas estratégias de busca de câmeras
   ✅ Melhor tratamento de erros
   ✅ Relatórios mais detalhados
   ✅ Teste completo antes da execução
"

print_color $GREEN "
📁 ESTRUTURA DE SAÍDA:
   cameras/
   ├── Aguas_Claras_Castaneiras/
   │   ├── P1_Aguas_Claras_Castaneiras_20250529_143022.jpg
   │   ├── P2_Aguas_Claras_Castaneiras_20250529_143025.jpg
   │   └── P3_Aguas_Claras_Castaneiras_20250529_143028.jpg
   ├── Aracaju_Av_Augusto_Franco/
   │   ├── P1_Aracaju_Av_Augusto_Franco_20250529_143031.jpg
   │   └── P2_Aracaju_Av_Augusto_Franco_20250529_143034.jpg
   └── ...
"

print_color $CYAN "
========================================
     ERRO CORRIGIDO - PRONTO PARA USO!
       Chrome será instalado automaticamente
       se necessário, ou instruções serão dadas
========================================
"

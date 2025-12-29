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

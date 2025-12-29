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

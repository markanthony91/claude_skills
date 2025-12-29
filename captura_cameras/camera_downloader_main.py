#!/usr/bin/env python3
"""
Downloader COMPLETO de Câmeras AIVisual - Versão Integrada
Combina login/scraping do Selenium com download paralelo otimizado
"""

import sys
import os
import json
import subprocess
import requests
import time
from pathlib import Path
from datetime import datetime

# Importar funções do módulo paralelo
try:
    from camera_downloader_parallel import processar_cameras_paralelo
except ImportError:
    print("❌ Erro: camera_downloader_parallel.py não encontrado")
    print("   Certifique-se de que está no diretório correto")
    sys.exit(1)

BASE_URL = "https://dashboard.aivisual.ai"
USERNAME = os.getenv('AIVISUAL_USER', 'bk@aiknow.ai')
PASSWORD = os.getenv('AIVISUAL_PASS', 'nR}CMryIT,8/5!3i9')

def carregar_config():
    """Carrega configuração do arquivo JSON"""
    config_file = Path(".camera_config.json")
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            pass

    # Configuração padrão
    return {
        "storage_mode": "timestamped",  # Formato compatível com dashboard
        "max_workers": 10,
        "retry_attempts": 3,
        "delay_between_cameras": 0.5
    }

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
    return False

def fazer_login_e_obter_cameras():
    """
    Faz login no AIVisual e obtém lista de todas as câmeras
    Retorna: (session, lista_de_cameras)
    """
    try:
        print("\n🔧 VERIFICAÇÕES INICIAIS")
        print("=" * 80)

        if not verificar_e_instalar_dependencias():
            print("❌ Falha na verificação das dependências")
            return None, []

        if not verificar_chrome():
            print("❌ Chrome não disponível")
            return None, []

        print("✅ Todas as verificações passaram!\n")

        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        import chromedriver_autoinstaller

        print("🚀 DOWNLOADER PARALELO - TODAS AS CÂMERAS AIVISUAL")
        print("=" * 80)

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
        chrome_options.add_argument('--disable-images')

        driver = webdriver.Chrome(options=chrome_options)
        session = requests.Session()

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
            max_scrolls = 20

            while scroll_attempts < max_scrolls:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1
                print(f"   → Scroll {scroll_attempts}/20...")

            # Transferir cookies do Selenium para requests.Session
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

            # Importar função de extração de nome
            import re

            def extrair_nome_loja(nome_camera):
                try:
                    nome_limpo = nome_camera.replace("BK - ", "")
                    nome_limpo = re.sub(r'_P[123]$', '', nome_limpo)
                    nome_pasta = nome_limpo.replace(" - ", "_").replace(" ", "_")
                    nome_pasta = "".join(c for c in nome_pasta if c.isalnum() or c in "_-")
                    return nome_pasta, nome_limpo
                except:
                    return "Loja_Desconhecida", "Loja Desconhecida"

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
                return None, []

            lojas_unicas = set()
            for cam in cameras_encontradas:
                lojas_unicas.add(cam['loja_nome'])

            print(f"🏪 Total de lojas identificadas: {len(lojas_unicas)}")
            print("=" * 80)

            return session, cameras_encontradas

        finally:
            driver.quit()

    except Exception as e:
        print(f"❌ Erro crítico durante login/scraping: {e}")
        import traceback
        traceback.print_exc()
        return None, []

def main():
    """Função principal - integra login/scraping com download paralelo"""

    print("\n" + "="*80)
    print("🚀 SISTEMA DE DOWNLOAD PARALELO DE CÂMERAS AIVISUAL")
    print("="*80)

    # Carregar configuração
    config = carregar_config()

    print(f"\n⚙️  Configuração:")
    print(f"   • Modo de armazenamento: {config['storage_mode']}")
    print(f"   • Workers paralelos: {config['max_workers']}")
    print(f"   • Tentativas de retry: {config['retry_attempts']}")
    print(f"   • Delay entre câmeras: {config['delay_between_cameras']}s")

    # Fase 1: Login e Scraping (Selenium)
    print("\n" + "="*80)
    print("FASE 1: LOGIN E DESCOBERTA DE CÂMERAS")
    print("="*80)

    session, cameras_encontradas = fazer_login_e_obter_cameras()

    if not session or not cameras_encontradas:
        print("\n❌ Falha ao obter câmeras. Abortando.")
        return False

    # Fase 2: Download Paralelo
    print("\n" + "="*80)
    print("FASE 2: DOWNLOAD PARALELO DE IMAGENS")
    print("="*80)

    resultados = processar_cameras_paralelo(
        cameras_encontradas,
        session,
        storage_mode=config['storage_mode']
    )

    return len(resultados) > 0

if __name__ == "__main__":
    print("🚨 ATENÇÃO: Este script baixará TODAS as câmeras em modo PARALELO!")
    print("   Isso será MUITO mais rápido (~2 minutos vs 16 minutos)")
    print("   Certifique-se de ter conexão estável com a internet")
    print()

    resposta = input("🤔 Deseja continuar? (s/N): ")
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        sucesso = main()
        if not sucesso:
            print("\n❌ Execução não foi bem-sucedida")
            print("   Verifique os erros acima e tente novamente")
            sys.exit(1)
        else:
            print("\n🎉 Execução concluída com sucesso!")
            sys.exit(0)
    else:
        print("❌ Cancelado pelo usuário.")
        sys.exit(0)

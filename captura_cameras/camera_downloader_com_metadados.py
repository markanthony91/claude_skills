#!/usr/bin/env python3
"""
Downloader Completo de Câmeras AIVisual COM Extração de Metadados
Versão integrada que baixa imagens E extrai metadados em uma única execução
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
import json

# Importar o downloader original
sys.path.insert(0, os.path.dirname(__file__))
from camera_downloader_complete import (
    verificar_e_instalar_dependencias,
    verificar_chrome,
    testar_selenium,
    extrair_nome_loja,
    download_base64_image,
    BASE_URL,
    USERNAME,
    PASSWORD,
    DELAY_ENTRE_CAMERAS
)

METADATA_FILE = Path(__file__).parent / "data" / "camera_metadata.json"


def extract_camera_metadata(elemento):
    """
    Extrai metadados de um elemento de câmera
    Retorna dict com metadados encontrados
    """
    metadata = {}

    try:
        texto_completo = elemento.text

        # Nome completo
        if "Nome:" in texto_completo:
            nome_line = [l for l in texto_completo.split("\n") if "Nome:" in l]
            if nome_line:
                metadata['nome_completo'] = nome_line[0].replace("Nome:", "").strip()
        elif "BK -" in texto_completo:
            linhas = texto_completo.split("\n")
            for linha in linhas:
                if "BK -" in linha:
                    metadata['nome_completo'] = linha.strip()
                    break

        # Lugar
        if "Lugar:" in texto_completo:
            lugar_line = [l for l in texto_completo.split("\n") if "Lugar:" in l]
            if lugar_line:
                metadata['lugar'] = lugar_line[0].replace("Lugar:", "").strip()

        # Área
        if "Área:" in texto_completo or "Area:" in texto_completo:
            area_line = [l for l in texto_completo.split("\n") if "Área:" in l or "Area:" in l]
            if area_line:
                metadata['area'] = area_line[0].replace("Área:", "").replace("Area:", "").strip()

        # Buscar elementos internos mais específicos
        try:
            from selenium.webdriver.common.by import By

            # Última resposta
            try:
                response_elem = elemento.find_element(By.CSS_SELECTOR, "b.response")
                metadata['ultima_resposta'] = response_elem.text.strip()
            except:
                pass

            # IP local (ethernet)
            try:
                ethernet_elem = elemento.find_element(By.CSS_SELECTOR, "b.ethernet")
                metadata['ip_local'] = ethernet_elem.text.strip()
            except:
                pass

            # IP internet
            try:
                internet_elem = elemento.find_element(By.CSS_SELECTOR, "b.internet")
                metadata['ip_internet'] = internet_elem.text.strip()
            except:
                pass

            # MAC address
            try:
                mac_elem = elemento.find_element(By.CSS_SELECTOR, "b.mac")
                metadata['mac_address'] = mac_elem.text.strip()
            except:
                pass

            # Temperatura CPU
            try:
                cpu_elem = elemento.find_element(By.CSS_SELECTOR, "b.cpu")
                metadata['temperatura_cpu'] = cpu_elem.text.strip()
            except:
                pass

            # Versão do sistema
            try:
                version_elem = elemento.find_element(By.CSS_SELECTOR, "b.version")
                metadata['versao_sistema'] = version_elem.text.strip()
            except:
                pass

            # UUID (do ID do elemento <small>)
            try:
                small_elem = elemento.find_element(By.TAG_NAME, "small")
                uuid = small_elem.get_attribute("id")
                if uuid:
                    metadata['uuid'] = uuid.strip()
            except:
                pass

        except Exception as e:
            # Se não conseguir buscar elementos internos, tenta pelo texto
            pass

        # Fallback: buscar no texto completo usando regex
        if not metadata.get('ip_local') and "IP da rede local:" in texto_completo:
            match = re.search(r'IP da rede local:\s*(\d+\.\d+\.\d+\.\d+)', texto_completo)
            if match:
                metadata['ip_local'] = match.group(1)

        if not metadata.get('ip_internet') and "IP de internet:" in texto_completo:
            match = re.search(r'IP de internet:\s*(\d+\.\d+\.\d+\.\d+)', texto_completo)
            if match:
                metadata['ip_internet'] = match.group(1)

        if not metadata.get('versao_sistema') and "Versão do Sistema:" in texto_completo:
            match = re.search(r'Versão do Sistema:\s*([^\n]+)', texto_completo)
            if match:
                metadata['versao_sistema'] = match.group(1).strip()

    except Exception as e:
        pass

    return metadata


def copy_p1_to_p2_p3(all_metadata):
    """Copia dados compartilhados de P1 para P2 e P3"""

    SHARED_FIELDS = ['lugar', 'ip_internet', 'versao_sistema']

    p1_cameras = {k: v for k, v in all_metadata.items() if k.endswith('_P1')}

    added_count = 0

    for p1_id, p1_data in p1_cameras.items():
        if not p1_data:  # Skip se não tem dados
            continue

        store_name = p1_id[:-3]  # Remove _P1

        for position in ['P2', 'P3']:
            camera_id = f"{store_name}_{position}"

            # Se já existe metadados completos para P2/P3, não sobrescrever
            if camera_id in all_metadata and all_metadata[camera_id]:
                continue

            # Preparar dados compartilhados
            shared_data = {}

            for field in SHARED_FIELDS:
                if field in p1_data:
                    shared_data[field] = p1_data[field]

            # Adicionar nome completo ajustado
            if 'nome_completo' in p1_data:
                nome_completo = p1_data['nome_completo'].replace('_P1', f'_{position}')
                shared_data['nome_completo'] = nome_completo

            if shared_data:
                all_metadata[camera_id] = shared_data
                added_count += 1

    return added_count


def save_metadata(metadata):
    """Salva metadados no arquivo JSON"""
    METADATA_FILE.parent.mkdir(exist_ok=True)

    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return len(metadata)


def fazer_login_e_baixar_com_metadados():
    """Versão integrada: baixa imagens E extrai metadados"""

    try:
        print("🔧 VERIFICAÇÕES INICIAIS")
        print("=" * 40)

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

        print("🚀 DOWNLOADER COM EXTRAÇÃO DE METADADOS")
        print("=" * 60)
        print(f"⚙️  Delay entre câmeras: {DELAY_ENTRE_CAMERAS} segundos")
        print("📁 Imagens: cameras/Nome_da_Loja/P1_Nome_da_Loja_timestamp.jpg")
        print("📋 Metadados: data/camera_metadata.json")
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

        driver = webdriver.Chrome(options=chrome_options)
        session = requests.Session()

        cameras_processadas = []
        cameras_com_sucesso = []
        cameras_com_falha = []
        all_metadata = {}

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

            selenium_cookies = driver.get_cookies()
            for cookie in selenium_cookies:
                session.cookies.set(cookie['name'], cookie['value'])

            cameras_encontradas = []

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

            if not elementos:
                elementos = driver.find_elements(By.XPATH, "//*[contains(text(), 'BK -')]")
                if elementos:
                    print("   ✓ Usando busca por texto 'BK -'")

            print(f"🔍 Analisando {len(elementos)} elementos...")
            print("📋 Extraindo metadados simultaneamente...")

            metadados_extraidos = 0

            for i, elemento in enumerate(elementos):
                try:
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

                    # ===== EXTRAÇÃO DE METADADOS =====
                    # Extrair metadados deste elemento
                    metadata = extract_camera_metadata(elemento)

                    if metadata:
                        # ID da câmera para o arquivo de metadados
                        camera_metadata_id = f"{nome_pasta_loja}_{tipo_camera}"
                        all_metadata[camera_metadata_id] = metadata
                        metadados_extraidos += 1
                    # =================================

                    if len(cameras_encontradas) % 50 == 0:
                        print(f"  → {len(cameras_encontradas)} câmeras | {metadados_extraidos} com metadados")

                except Exception as e:
                    continue

            print(f"\n✅ Câmeras encontradas: {len(cameras_encontradas)}")
            print(f"📋 Metadados extraídos: {metadados_extraidos} câmeras")

            # Copiar metadados de P1 para P2/P3
            print("\n📦 Copiando dados compartilhados P1 → P2/P3...")
            added = copy_p1_to_p2_p3(all_metadata)
            print(f"   ✓ {added} câmeras P2/P3 adicionadas")

            # Salvar metadados
            print("\n💾 Salvando metadados...")
            total_saved = save_metadata(all_metadata)
            print(f"   ✓ {total_saved} câmeras salvas em {METADATA_FILE}")

            if len(cameras_encontradas) == 0:
                print("\n❌ Nenhuma câmera encontrada!")
                return False

            lojas_unicas = set()
            for cam in cameras_encontradas:
                lojas_unicas.add(cam['loja_nome'])

            print(f"\n🏪 Total de lojas: {len(lojas_unicas)}")
            print("=" * 60)
            print("\n🖼️  INICIANDO DOWNLOAD DAS IMAGENS...")
            print("=" * 60)

            inicio_processamento = time.time()

            # Download das imagens (código original)
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

                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    filename = f"{camera['tipo']}_{camera['loja_pasta']}_{timestamp}.jpg"
                                    filepath = pasta_loja / filename

                                    with open(filepath, 'wb') as f:
                                        f.write(img_data)

                                    cameras_com_sucesso.append(camera)
                                    print("✅")
                                else:
                                    cameras_com_falha.append(camera)
                                    print("❌ Download falhou")
                            else:
                                cameras_com_falha.append(camera)
                                print("⚠️  Sem imagem")
                        except:
                            cameras_com_falha.append(camera)
                            print("❌ Erro no JSON")
                    else:
                        cameras_com_falha.append(camera)
                        print(f"❌ HTTP {response.status_code}")

                    if i % 25 == 0:
                        tempo_decorrido = time.time() - inicio_processamento
                        print(f"  ⏱️  {i} câmeras em {tempo_decorrido:.0f}s | {len(cameras_com_sucesso)} OK, {len(cameras_com_falha)} falhas")

                    time.sleep(DELAY_ENTRE_CAMERAS)

                except Exception as e:
                    cameras_com_falha.append(camera)
                    print(f"❌ Erro: {str(e)[:50]}")
                    continue

            tempo_total = time.time() - inicio_processamento

            print("\n" + "=" * 60)
            print("📊 RELATÓRIO FINAL")
            print("=" * 60)
            print(f"✅ Imagens baixadas: {len(cameras_com_sucesso)}")
            print(f"❌ Falhas: {len(cameras_com_falha)}")
            print(f"📋 Metadados salvos: {total_saved} câmeras")
            print(f"⏱️  Tempo total: {tempo_total:.0f}s ({tempo_total/60:.1f} minutos)")
            print("=" * 60)

            return True

        except Exception as e:
            print(f"\n❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            driver.quit()

    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    fazer_login_e_baixar_com_metadados()

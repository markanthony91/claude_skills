#!/usr/bin/env python3
"""
Download PARALELO com Extração de Metadados
Versão otimizada: 2-3 minutos para download + metadados
"""

import os
import re
import base64
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import requests

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    import chromedriver_autoinstaller
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium não disponível")

# Configuração
BASE_URL = "https://dashboard.aivisual.ai"
USERNAME = os.getenv('AIVISUAL_USER', 'bk@aiknow.ai')
PASSWORD = os.getenv('AIVISUAL_PASS', 'nR}CMryIT,8/5!3i9')
MAX_WORKERS = 10  # Downloads simultâneos
DELAY_ENTRE_CAMERAS = 0.5  # Delay reduzido (paralelo aguenta)
RETRY_ATTEMPTS = 3
METADATA_FILE = Path(__file__).parent / "data" / "camera_metadata.json"


class ParallelDownloaderComMetadados:
    """Gerenciador de downloads paralelos + extração de metadados"""

    def __init__(self, output_dir='cameras'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.stats_lock = Lock()
        self.stats = {
            'total': 0,
            'sucesso': 0,
            'falha': 0,
            'atual': '',
            'progresso': 0,
            'running': False,
            'cameras_ok': [],
            'cameras_falha': []
        }

        self.metadata = {}  # Armazena metadados extraídos
        self.metadata_lock = Lock()

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def get_stats(self):
        """Retorna estatísticas thread-safe"""
        with self.stats_lock:
            return self.stats.copy()

    def update_stats(self, **kwargs):
        """Atualiza estatísticas thread-safe"""
        with self.stats_lock:
            self.stats.update(kwargs)
            if self.stats['total'] > 0:
                self.stats['progresso'] = round(
                    (self.stats['sucesso'] + self.stats['falha']) / self.stats['total'] * 100
                )

    def extrair_nome_loja(self, nome_camera):
        """Extrai e limpa nome da loja"""
        try:
            nome_limpo = nome_camera.replace("BK - ", "")
            nome_limpo = re.sub(r'_P[123]$', '', nome_limpo)
            nome_pasta = nome_limpo.replace(" - ", "_").replace(" ", "_")
            nome_pasta = "".join(c for c in nome_pasta if c.isalnum() or c in "_-")
            return nome_pasta, nome_limpo
        except:
            return "Loja_Desconhecida", "Loja Desconhecida"

    def extract_camera_metadata(self, elemento):
        """Extrai metadados de um elemento de câmera"""
        metadata = {}

        try:
            texto_completo = elemento.text

            # Nome completo
            if "Nome:" in texto_completo:
                nome_line = [l for l in texto_completo.split("\n") if "Nome:" in l]
                if nome_line:
                    metadata['nome_completo'] = nome_line[0].replace("Nome:", "").strip()
            elif "BK -" in texto_completo:
                for linha in texto_completo.split("\n"):
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

            # Tentar buscar elementos específicos
            try:
                # Última resposta
                try:
                    response_elem = elemento.find_element(By.CSS_SELECTOR, "b.response")
                    metadata['ultima_resposta'] = response_elem.text.strip()
                except:
                    pass

                # IP local
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

                # Versão
                try:
                    version_elem = elemento.find_element(By.CSS_SELECTOR, "b.version")
                    metadata['versao_sistema'] = version_elem.text.strip()
                except:
                    pass

                # UUID
                try:
                    small_elem = elemento.find_element(By.TAG_NAME, "small")
                    uuid = small_elem.get_attribute("id")
                    if uuid:
                        metadata['uuid'] = uuid.strip()
                except:
                    pass

            except:
                pass

            # Fallback: regex no texto
            if not metadata.get('ip_local') and "IP da rede local:" in texto_completo:
                match = re.search(r'IP da rede local:\s*(\d+\.\d+\.\d+\.\d+)', texto_completo)
                if match:
                    metadata['ip_local'] = match.group(1)

            if not metadata.get('ip_internet') and "IP de internet:" in texto_completo:
                match = re.search(r'IP de internet:\s*(\d+\.\d+\.\d+\.\d+)', texto_completo)
                if match:
                    metadata['ip_internet'] = match.group(1)

        except Exception as e:
            logging.debug(f"Erro ao extrair metadados: {e}")

        return metadata

    def login_aivisual(self):
        """Faz login no AIVisual"""
        if not SELENIUM_AVAILABLE:
            logging.error("Selenium não disponível")
            return None

        try:
            chromedriver_autoinstaller.install()

            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')

            driver = webdriver.Chrome(options=chrome_options)
            driver.get(f"{BASE_URL}/login")
            time.sleep(2)

            wait = WebDriverWait(driver, 10)
            email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]')))
            email_input.send_keys(USERNAME)

            password_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            password_input.send_keys(PASSWORD)

            login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()

            time.sleep(3)

            # Extrair cookies para requests
            session = requests.Session()
            for cookie in driver.get_cookies():
                session.cookies.set(cookie['name'], cookie['value'])

            driver.quit()

            logging.info(f"✅ Login realizado: {USERNAME}")
            return session

        except Exception as e:
            logging.error(f"❌ Erro no login: {e}")
            if 'driver' in locals():
                driver.quit()
            return None

    def buscar_cameras_com_metadados(self, session):
        """Busca câmeras E extrai metadados simultaneamente"""
        if not SELENIUM_AVAILABLE:
            logging.error("Selenium não disponível")
            return []

        try:
            chromedriver_autoinstaller.install()

            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')

            driver = webdriver.Chrome(options=chrome_options)

            # Transferir cookies
            driver.get(BASE_URL)
            for cookie_name, cookie_value in session.cookies.items():
                driver.add_cookie({'name': cookie_name, 'value': cookie_value})

            # Acessar página de câmeras
            driver.get(f"{BASE_URL}/admin/iots")
            time.sleep(3)

            logging.info("📹 Carregando câmeras...")

            # Scroll para carregar tudo
            last_height = driver.execute_script("return document.body.scrollHeight")
            scroll_count = 0
            max_scrolls = 20

            while scroll_count < max_scrolls:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_count += 1
                logging.info(f"   Scroll {scroll_count}/{max_scrolls}...")

            # Buscar elementos das câmeras
            logging.info("🔍 Extraindo câmeras e metadados...")

            seletores = [
                '[data-cam-id]',
                '[data-iot-id]',
                '.cameraCard',
                '.camera-item',
                '[class*="camera"]'
            ]

            elementos = []
            for seletor in seletores:
                elementos = driver.find_elements(By.CSS_SELECTOR, seletor)
                if elementos:
                    logging.info(f"   ✓ Usando seletor: {seletor}")
                    break

            if not elementos:
                elementos = driver.find_elements(By.XPATH, "//*[contains(text(), 'BK -')]")
                if elementos:
                    logging.info("   ✓ Usando busca por texto 'BK -'")

            logging.info(f"📋 Processando {len(elementos)} elementos...")

            cameras = []
            metadados_extraidos = 0

            for i, elemento in enumerate(elementos):
                try:
                    # ID da câmera
                    cam_id = (
                        elemento.get_attribute('data-cam-id') or
                        elemento.get_attribute('data-iot-id') or
                        elemento.get_attribute('data-id') or
                        elemento.get_attribute('id') or
                        f"camera_{i}"
                    )

                    # Nome
                    texto = elemento.text
                    nome = f"Camera_{i}"

                    if "Nome:" in texto:
                        nome = texto.split("Nome:")[1].split("\n")[0].strip()
                    elif "BK -" in texto:
                        for linha in texto.split("\n"):
                            if "BK -" in linha:
                                nome = linha.strip()
                                break

                    # Tipo de câmera
                    tipo = "P1"
                    if "_P2" in nome or " P2" in nome:
                        tipo = "P2"
                    elif "_P3" in nome or " P3" in nome:
                        tipo = "P3"

                    loja_pasta, loja_nome = self.extrair_nome_loja(nome)

                    cameras.append({
                        'id': cam_id,
                        'nome': nome,
                        'loja_pasta': loja_pasta,
                        'loja_nome': loja_nome,
                        'tipo': tipo
                    })

                    # ===== EXTRAÇÃO DE METADADOS =====
                    metadata = self.extract_camera_metadata(elemento)

                    if metadata:
                        camera_id = f"{loja_pasta}_{tipo}"
                        with self.metadata_lock:
                            self.metadata[camera_id] = metadata
                        metadados_extraidos += 1
                    # =================================

                    if (i + 1) % 50 == 0:
                        logging.info(f"   → {i + 1} câmeras | {metadados_extraidos} com metadados")

                except Exception as e:
                    logging.debug(f"Erro ao processar elemento {i}: {e}")
                    continue

            driver.quit()

            logging.info(f"✅ {len(cameras)} câmeras encontradas")
            logging.info(f"📋 {metadados_extraidos} metadados extraídos")

            return cameras

        except Exception as e:
            logging.error(f"Erro ao buscar câmeras: {e}")
            if 'driver' in locals():
                driver.quit()
            return []

    def download_base64_image(self, image_url):
        """Download e decodifica imagem base64"""
        try:
            if image_url.startswith('data:image/'):
                header, data = image_url.split(',', 1)
                return base64.b64decode(data)
            else:
                response = requests.get(image_url, timeout=30)
                return response.content if response.status_code == 200 else None
        except Exception as e:
            return None

    def validar_imagem_jpg(self, img_data):
        """Valida se é JPG válido"""
        if not img_data or len(img_data) < 100:
            return False
        return img_data[:3] == b'\xff\xd8\xff'

    def salvar_imagem(self, camera, img_data):
        """Salva imagem"""
        try:
            agora = datetime.now()
            pasta = self.output_dir / camera['loja_pasta']
            pasta.mkdir(parents=True, exist_ok=True)

            caminho = pasta / f"{camera['tipo']}_{camera['loja_pasta']}_{agora:%Y%m%d_%H%M%S}.jpg"

            with open(caminho, 'wb') as f:
                f.write(img_data)

            return caminho

        except Exception as e:
            logging.error(f"Erro ao salvar {camera['loja_nome']} {camera['tipo']}: {e}")
            return None

    def download_camera_com_retry(self, camera, session):
        """Download de uma câmera com retry"""
        for tentativa in range(1, RETRY_ATTEMPTS + 1):
            try:
                self.update_stats(atual=f"{camera['loja_nome']} - {camera['tipo']}")

                response = session.get(
                    f"{BASE_URL}/admin/get/iots/getLastImage",
                    params={'iot': camera['id']},
                    timeout=30
                )

                if response.status_code != 200:
                    if tentativa < RETRY_ATTEMPTS:
                        time.sleep(2 ** tentativa)
                        continue
                    return None

                data = response.json()
                image_url = data.get('image')

                if not image_url:
                    return None

                img_data = self.download_base64_image(image_url)

                if not img_data or not self.validar_imagem_jpg(img_data):
                    if tentativa < RETRY_ATTEMPTS:
                        time.sleep(2 ** tentativa)
                        continue
                    return None

                caminho_arquivo = self.salvar_imagem(camera, img_data)

                if caminho_arquivo:
                    with self.stats_lock:
                        self.stats['sucesso'] += 1
                        self.stats['cameras_ok'].append({
                            'loja': camera['loja_nome'],
                            'tipo': camera['tipo']
                        })

                    logging.info(f"✅ {camera['loja_nome']} ({camera['tipo']})")

                    return {
                        'camera': camera,
                        'arquivo': str(caminho_arquivo)
                    }

            except Exception as e:
                if tentativa < RETRY_ATTEMPTS:
                    time.sleep(2 ** tentativa)
                    continue

        # Falha
        with self.stats_lock:
            self.stats['falha'] += 1
            self.stats['cameras_falha'].append({
                'loja': camera['loja_nome'],
                'tipo': camera['tipo']
            })

        logging.error(f"❌ {camera['loja_nome']} ({camera['tipo']})")
        return None

    def processar_cameras_paralelo(self, cameras, session):
        """Processa câmeras em PARALELO"""
        self.update_stats(
            total=len(cameras),
            sucesso=0,
            falha=0,
            running=True,
            cameras_ok=[],
            cameras_falha=[]
        )

        logging.info(f"🚀 Download paralelo: {len(cameras)} câmeras ({MAX_WORKERS} workers)")

        inicio = time.time()

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(self.download_camera_com_retry, camera, session): camera
                for camera in cameras
            }

            for future in as_completed(futures):
                try:
                    future.result()
                    time.sleep(DELAY_ENTRE_CAMERAS)
                except Exception as e:
                    logging.error(f"Erro no future: {e}")

        duracao = time.time() - inicio

        self.update_stats(running=False, atual='Concluído', progresso=100)

        logging.info(f"✅ Download concluído em {duracao:.1f}s ({duracao/60:.1f} min)")
        logging.info(f"📊 Sucesso: {self.stats['sucesso']} | Falha: {self.stats['falha']}")

        return duracao

    def copy_p1_to_p2_p3(self):
        """Copia metadados de P1 para P2/P3"""
        SHARED_FIELDS = ['lugar', 'ip_internet', 'versao_sistema']

        p1_cameras = {k: v for k, v in self.metadata.items() if k.endswith('_P1')}
        added = 0

        for p1_id, p1_data in p1_cameras.items():
            if not p1_data:
                continue

            store_name = p1_id[:-3]

            for position in ['P2', 'P3']:
                camera_id = f"{store_name}_{position}"

                if camera_id in self.metadata and self.metadata[camera_id]:
                    continue

                shared_data = {}

                for field in SHARED_FIELDS:
                    if field in p1_data:
                        shared_data[field] = p1_data[field]

                if 'nome_completo' in p1_data:
                    shared_data['nome_completo'] = p1_data['nome_completo'].replace('_P1', f'_{position}')

                if shared_data:
                    self.metadata[camera_id] = shared_data
                    added += 1

        return added

    def save_metadata(self):
        """Salva metadados em JSON"""
        METADATA_FILE.parent.mkdir(exist_ok=True)

        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

        logging.info(f"💾 Metadados salvos: {len(self.metadata)} câmeras")

    def executar_download_completo(self):
        """Execução completa: Login + Extração de Metadados + Download Paralelo"""
        try:
            logging.info("=" * 70)
            logging.info("🚀 DOWNLOAD PARALELO COM METADADOS")
            logging.info("=" * 70)

            # 1. Login
            logging.info("\n🔐 FASE 1: Login...")
            session = self.login_aivisual()

            if not session:
                logging.error("Falha no login")
                return False

            # 2. Buscar câmeras + Extrair metadados
            logging.info("\n📋 FASE 2: Descoberta e Extração de Metadados...")
            cameras = self.buscar_cameras_com_metadados(session)

            if not cameras:
                logging.error("Nenhuma câmera encontrada")
                return False

            # 3. Copiar metadados P1 → P2/P3
            logging.info("\n📦 Copiando metadados P1 → P2/P3...")
            added = self.copy_p1_to_p2_p3()
            logging.info(f"   ✓ {added} câmeras P2/P3 adicionadas")

            # 4. Salvar metadados
            self.save_metadata()

            # 5. Download paralelo
            logging.info(f"\n🖼️  FASE 3: Download Paralelo ({MAX_WORKERS} workers)...")
            duracao = self.processar_cameras_paralelo(cameras, session)

            # Relatório final
            logging.info("\n" + "=" * 70)
            logging.info("📊 RELATÓRIO FINAL")
            logging.info("=" * 70)
            logging.info(f"✅ Imagens: {self.stats['sucesso']} OK | {self.stats['falha']} Falhas")
            logging.info(f"📋 Metadados: {len(self.metadata)} câmeras salvas")
            logging.info(f"⏱️  Tempo total: {duracao:.1f}s ({duracao/60:.1f} minutos)")
            logging.info("=" * 70)

            return True

        except Exception as e:
            logging.error(f"Erro fatal: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    downloader = ParallelDownloaderComMetadados()
    downloader.executar_download_completo()

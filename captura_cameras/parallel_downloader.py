#!/usr/bin/env python3
"""
Módulo de Download Paralelo Integrado ao Dashboard
Versão otimizada com callbacks de progresso em tempo real
"""

import os
import re
import base64
import time
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
    print("⚠️ Selenium não disponível. Instale com: pip3 install selenium")

# Configuração
BASE_URL = "https://dashboard.aivisual.ai"
USERNAME = os.getenv('AIVISUAL_USER', 'bk@aiknow.ai')
PASSWORD = os.getenv('AIVISUAL_PASS', 'nR}CMryIT,8/5!3i9')
MAX_WORKERS = 10
DELAY_ENTRE_CAMERAS = 0.5
RETRY_ATTEMPTS = 3

class DownloadManager:
    """Gerenciador de downloads com callbacks de progresso"""

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

        # Configurar logging
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

    def login_aivisual(self):
        """Faz login no AIVisual usando Selenium e extrai cookies para requests"""
        if not SELENIUM_AVAILABLE:
            logging.error("Selenium não disponível")
            return None

        try:
            # Configurar Chrome headless
            chromedriver_autoinstaller.install()

            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')

            driver = webdriver.Chrome(options=chrome_options)
            driver.get(f"{BASE_URL}/login")
            time.sleep(2)

            # Preencher formulário
            wait = WebDriverWait(driver, 10)
            email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]')))
            email_input.send_keys(USERNAME)

            password_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            password_input.send_keys(PASSWORD)

            # Fazer login
            login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()

            time.sleep(3)

            # Extrair cookies para usar com requests
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

    def buscar_cameras(self, session):
        """Busca lista de todas as câmeras via Selenium"""
        if not SELENIUM_AVAILABLE:
            logging.error("Selenium não disponível")
            return []

        try:
            # Configurar Chrome headless
            chromedriver_autoinstaller.install()

            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')

            driver = webdriver.Chrome(options=chrome_options)

            # Transferir cookies da sessão
            driver.get(BASE_URL)
            for cookie_name, cookie_value in session.cookies.items():
                driver.add_cookie({'name': cookie_name, 'value': cookie_value})

            # Acessar página de câmeras
            driver.get(f"{BASE_URL}/admin/iots")
            time.sleep(3)

            # Executar JavaScript para obter lista de câmeras
            cameras_data = driver.execute_script("""
                const iots = [];
                const elements = document.querySelectorAll('[data-iot-id]');
                elements.forEach(el => {
                    iots.push({
                        id: el.getAttribute('data-iot-id'),
                        name: el.getAttribute('data-iot-name') || el.textContent.trim()
                    });
                });
                return iots;
            """)

            driver.quit()

            cameras = []
            for iot in cameras_data:
                nome_camera = iot.get('name', 'Desconhecido')
                loja_pasta, loja_nome = self.extrair_nome_loja(nome_camera)

                # Identificar tipo de câmera (P1, P2, P3)
                tipo = "P?"
                if "_P1" in nome_camera or " P1" in nome_camera:
                    tipo = "P1"
                elif "_P2" in nome_camera or " P2" in nome_camera:
                    tipo = "P2"
                elif "_P3" in nome_camera or " P3" in nome_camera:
                    tipo = "P3"

                cameras.append({
                    'id': iot.get('id'),
                    'nome': nome_camera,
                    'loja_pasta': loja_pasta,
                    'loja_nome': loja_nome,
                    'tipo': tipo
                })

            logging.info(f"📷 {len(cameras)} câmeras encontradas")
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
            logging.error(f"Erro ao baixar imagem: {e}")
            return None

    def validar_imagem_jpg(self, img_data):
        """Valida se os bytes são realmente um JPG válido"""
        if not img_data or len(img_data) < 100:
            return False
        return img_data[:3] == b'\xff\xd8\xff'

    def salvar_imagem(self, camera, img_data):
        """Salva imagem no formato timestamped"""
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
        """Download de uma câmera com retry automático"""
        for tentativa in range(1, RETRY_ATTEMPTS + 1):
            try:
                # Atualizar status atual
                self.update_stats(atual=f"{camera['loja_nome']} - {camera['tipo']}")

                # Request para obter imagem
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

                # Download da imagem
                img_data = self.download_base64_image(image_url)

                if not img_data or not self.validar_imagem_jpg(img_data):
                    if tentativa < RETRY_ATTEMPTS:
                        time.sleep(2 ** tentativa)
                        continue
                    return None

                # Salvar arquivo
                caminho_arquivo = self.salvar_imagem(camera, img_data)

                if caminho_arquivo:
                    # Atualizar estatísticas
                    with self.stats_lock:
                        self.stats['sucesso'] += 1
                        self.stats['cameras_ok'].append({
                            'loja': camera['loja_nome'],
                            'tipo': camera['tipo'],
                            'arquivo': str(caminho_arquivo)
                        })

                    logging.info(f"✅ {camera['loja_nome']} ({camera['tipo']})")

                    return {
                        'camera': camera,
                        'arquivo': str(caminho_arquivo),
                        'tamanho': len(img_data)
                    }

            except Exception as e:
                logging.error(f"Erro em {camera['loja_nome']} {camera['tipo']}: {e}")
                if tentativa < RETRY_ATTEMPTS:
                    time.sleep(2 ** tentativa)
                    continue

        # Todas as tentativas falharam
        with self.stats_lock:
            self.stats['falha'] += 1
            self.stats['cameras_falha'].append({
                'loja': camera['loja_nome'],
                'tipo': camera['tipo']
            })

        logging.error(f"❌ {camera['loja_nome']} ({camera['tipo']}) - FALHA")
        return None

    def processar_cameras_paralelo(self, cameras, session):
        """Processa lista de câmeras em paralelo"""
        self.update_stats(
            total=len(cameras),
            sucesso=0,
            falha=0,
            running=True,
            cameras_ok=[],
            cameras_falha=[]
        )

        logging.info(f"🚀 Iniciando download de {len(cameras)} câmeras ({MAX_WORKERS} workers)")

        inicio = time.time()
        resultados = []

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(self.download_camera_com_retry, camera, session): camera
                for camera in cameras
            }

            for future in as_completed(futures):
                try:
                    resultado = future.result()
                    if resultado:
                        resultados.append(resultado)

                    time.sleep(DELAY_ENTRE_CAMERAS)

                except Exception as e:
                    logging.error(f"Erro no future: {e}")

        duracao = time.time() - inicio

        self.update_stats(
            running=False,
            atual='Concluído',
            progresso=100
        )

        logging.info(f"✅ Download concluído em {duracao:.1f}s")
        logging.info(f"📊 Sucesso: {self.stats['sucesso']} | Falha: {self.stats['falha']}")

        return resultados

    def executar_download_completo(self):
        """Executa download usando o script paralelo original"""
        try:
            import subprocess
            from pathlib import Path

            self.update_stats(running=True, atual='Iniciando download paralelo...')

            # Usar o script paralelo existente que já funciona
            script_path = Path(__file__).parent / "camera_downloader_main.py"

            if not script_path.exists():
                logging.error("Script camera_downloader_main.py não encontrado")
                self.update_stats(running=False, atual='Script não encontrado')
                return False

            logging.info(f"🚀 Executando script: {script_path}")

            # Executar script e aguardar conclusão (modo simples)
            # Usaremos um arquivo JSON para compartilhar progresso entre processos
            result = subprocess.run(
                ["python3", str(script_path)],
                cwd=str(Path(__file__).parent),
                capture_output=False,
                text=True
            )

            if result.returncode == 0:
                self.update_stats(running=False, atual='Download concluído', progresso=100)
                logging.info("✅ Download concluído com sucesso")
                return True
            else:
                self.update_stats(running=False, atual='Erro no download')
                logging.error(f"❌ Script falhou com código: {result.returncode}")
                return False

        except Exception as e:
            logging.error(f"Erro no download: {e}")
            self.update_stats(running=False, atual=f'Erro: {str(e)}')
            return False

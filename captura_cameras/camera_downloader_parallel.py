#!/usr/bin/env python3
"""
Downloader PARALELO de Câmeras AIVisual
Versão otimizada com ThreadPoolExecutor
Ganho: ~10x mais rápido que a versão sequencial
"""

import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import base64
from datetime import datetime
from pathlib import Path
import time
import re
import logging
from threading import Lock

# Configuração
BASE_URL = "https://dashboard.aivisual.ai"
USERNAME = os.getenv('AIVISUAL_USER', 'bk@aiknow.ai')
PASSWORD = os.getenv('AIVISUAL_PASS', 'nR}CMryIT,8/5!3i9')
MAX_WORKERS = 10  # Número de downloads simultâneos
DELAY_ENTRE_CAMERAS = 0.5  # Reduzido (paralelo aguenta mais)
RETRY_ATTEMPTS = 3  # Tentar 3 vezes antes de desistir

# Lock para operações thread-safe
stats_lock = Lock()
stats = {
    'sucesso': 0,
    'falha': 0,
    'total': 0
}

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)-10s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'download_{datetime.now():%Y%m%d_%H%M%S}.log'),
        logging.StreamHandler()
    ]
)

def extrair_nome_loja(nome_camera):
    """Extrai e limpa nome da loja"""
    try:
        nome_limpo = nome_camera.replace("BK - ", "")
        nome_limpo = re.sub(r'_P[123]$', '', nome_limpo)
        nome_pasta = nome_limpo.replace(" - ", "_").replace(" ", "_")
        nome_pasta = "".join(c for c in nome_pasta if c.isalnum() or c in "_-")
        return nome_pasta, nome_limpo
    except:
        return "Loja_Desconhecida", "Loja Desconhecida"

def download_base64_image(image_url):
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

def validar_imagem_jpg(img_data):
    """Valida se os bytes são realmente um JPG válido"""
    if not img_data or len(img_data) < 100:
        return False
    # JPG começa com FF D8 FF
    return img_data[:3] == b'\xff\xd8\xff'

def download_camera_com_retry(camera, session, storage_mode='organized'):
    """
    Download de uma câmera com retry automático

    storage_mode:
        - 'organized': Organiza por data (2025-12/22/P1_143022.jpg)
        - 'snapshot': Sobrescreve sempre (P1.jpg)
        - 'timestamped': Modelo atual (P1_Loja_20251222_143022.jpg)
    """
    for tentativa in range(1, RETRY_ATTEMPTS + 1):
        try:
            # Request para obter imagem
            response = session.get(
                f"{BASE_URL}/admin/get/iots/getLastImage",
                params={'iot': camera['id']},
                timeout=30
            )

            if response.status_code != 200:
                logging.warning(
                    f"[{camera['loja_nome']} {camera['tipo']}] "
                    f"HTTP {response.status_code} (tentativa {tentativa}/{RETRY_ATTEMPTS})"
                )
                if tentativa < RETRY_ATTEMPTS:
                    time.sleep(2 ** tentativa)  # Backoff exponencial: 2s, 4s, 8s
                    continue
                return None

            data = response.json()
            image_url = data.get('image')

            if not image_url:
                logging.error(f"[{camera['loja_nome']} {camera['tipo']}] Sem URL de imagem")
                return None

            # Download da imagem
            img_data = download_base64_image(image_url)

            if not img_data:
                logging.error(f"[{camera['loja_nome']} {camera['tipo']}] Falha no download")
                if tentativa < RETRY_ATTEMPTS:
                    time.sleep(2 ** tentativa)
                    continue
                return None

            # Validar integridade
            if not validar_imagem_jpg(img_data):
                logging.error(f"[{camera['loja_nome']} {camera['tipo']}] JPG inválido")
                if tentativa < RETRY_ATTEMPTS:
                    time.sleep(2 ** tentativa)
                    continue
                return None

            # Salvar arquivo conforme modo de armazenamento
            caminho_arquivo = salvar_imagem(camera, img_data, storage_mode)

            if caminho_arquivo:
                # Atualizar estatísticas (thread-safe)
                with stats_lock:
                    stats['sucesso'] += 1

                logging.info(
                    f"✅ [{stats['sucesso']:3d}/{stats['total']}] "
                    f"{camera['loja_nome']} ({camera['tipo']}) - "
                    f"{len(img_data):,} bytes → {caminho_arquivo.name}"
                )

                return {
                    'camera': camera,
                    'arquivo': str(caminho_arquivo),
                    'tamanho': len(img_data),
                    'tentativas': tentativa
                }

        except Exception as e:
            logging.error(
                f"[{camera['loja_nome']} {camera['tipo']}] "
                f"Erro: {e} (tentativa {tentativa}/{RETRY_ATTEMPTS})"
            )
            if tentativa < RETRY_ATTEMPTS:
                time.sleep(2 ** tentativa)
                continue

    # Todas as tentativas falharam
    with stats_lock:
        stats['falha'] += 1

    logging.error(f"❌ [{camera['loja_nome']} {camera['tipo']}] FALHA após {RETRY_ATTEMPTS} tentativas")
    return None

def salvar_imagem(camera, img_data, storage_mode='organized'):
    """
    Salva imagem conforme modo de armazenamento escolhido
    """
    try:
        agora = datetime.now()

        if storage_mode == 'snapshot':
            # Modo 1: Sobrescreve sempre
            pasta = Path("cameras") / camera['loja_pasta']
            pasta.mkdir(parents=True, exist_ok=True)
            caminho = pasta / f"{camera['tipo']}.jpg"

        elif storage_mode == 'organized':
            # Modo 2: Organizado por data (RECOMENDADO)
            pasta = Path("cameras") / camera['loja_pasta'] / f"{agora:%Y-%m}" / f"{agora:%d}"
            pasta.mkdir(parents=True, exist_ok=True)
            caminho = pasta / f"{camera['tipo']}_{agora:%H%M%S}.jpg"

            # Criar symlink para último arquivo
            pasta_latest = Path("cameras") / camera['loja_pasta'] / "latest"
            pasta_latest.mkdir(parents=True, exist_ok=True)
            symlink = pasta_latest / f"{camera['tipo']}.jpg"

            # Remover symlink antigo e criar novo
            if symlink.exists() or symlink.is_symlink():
                symlink.unlink()

            # Criar symlink relativo
            caminho_relativo = os.path.relpath(caminho, pasta_latest)
            symlink.symlink_to(caminho_relativo)

        else:  # 'timestamped' (modo atual)
            # Modo 4: Timestamp no nome
            pasta = Path("cameras") / camera['loja_pasta']
            pasta.mkdir(parents=True, exist_ok=True)
            caminho = pasta / f"{camera['tipo']}_{camera['loja_pasta']}_{agora:%Y%m%d_%H%M%S}.jpg"

        # Escrever arquivo
        with open(caminho, 'wb') as f:
            f.write(img_data)

        return caminho

    except Exception as e:
        logging.error(f"Erro ao salvar {camera['loja_nome']} {camera['tipo']}: {e}")
        return None

def processar_cameras_paralelo(cameras_encontradas, session, storage_mode='organized'):
    """
    Processa lista de câmeras em paralelo usando ThreadPoolExecutor
    """
    global stats
    stats['total'] = len(cameras_encontradas)

    print(f"\n🚀 Iniciando download PARALELO de {len(cameras_encontradas)} câmeras")
    print(f"⚙️  Workers: {MAX_WORKERS} threads simultâneas")
    print(f"📁 Modo de armazenamento: {storage_mode}")
    print(f"🔄 Retry: {RETRY_ATTEMPTS} tentativas por câmera")
    print("=" * 80)

    inicio = time.time()
    resultados = []

    # ThreadPoolExecutor para downloads paralelos
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit todas as tarefas
        futures = {
            executor.submit(download_camera_com_retry, camera, session, storage_mode): camera
            for camera in cameras_encontradas
        }

        # Processar conforme completam
        for future in as_completed(futures):
            camera = futures[future]
            try:
                resultado = future.result()
                if resultado:
                    resultados.append(resultado)

                # Pequeno delay para evitar rate limiting
                time.sleep(DELAY_ENTRE_CAMERAS)

            except Exception as e:
                logging.error(f"Exceção ao processar {camera['loja_nome']}: {e}")

    tempo_total = time.time() - inicio

    # Relatório final
    print("\n" + "=" * 80)
    print("📊 RELATÓRIO FINAL - DOWNLOAD PARALELO")
    print("=" * 80)
    print(f"🎯 Total de câmeras: {stats['total']}")
    print(f"✅ Sucessos: {stats['sucesso']} ({stats['sucesso']/stats['total']*100:.1f}%)")
    print(f"❌ Falhas: {stats['falha']} ({stats['falha']/stats['total']*100:.1f}%)")
    print(f"⏱️  Tempo total: {tempo_total/60:.2f} minutos")
    print(f"⚡ Velocidade média: {stats['total']/tempo_total:.1f} câmeras/segundo")
    print(f"📈 Ganho vs sequencial: ~{16*60/tempo_total:.1f}x mais rápido")
    print("=" * 80)

    return resultados

# Exemplo de uso
if __name__ == "__main__":
    print("🔧 Este é o módulo de download paralelo")
    print("   Use camera_downloader_complete.py como ponto de entrada")
    print("   Ou integre estas funções no script principal")

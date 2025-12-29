#!/usr/bin/env python3
"""
Dashboard Web para Sistema de Câmeras AIVisual
Backend Flask com APIs para visualização e marcação de câmeras
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import json
from datetime import datetime
from pathlib import Path
import subprocess
import threading
import glob
import asyncio

# Importar módulos
try:
    from image_comparison import ImageComparator
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    print("⚠️ Módulo de comparação não disponível")

try:
    from parallel_downloader import DownloadManager
    DOWNLOADER_AVAILABLE = True
except ImportError:
    DOWNLOADER_AVAILABLE = False
    print("⚠️ Módulo de download paralelo não disponível")

app = Flask(__name__)

# Configurações
BASE_DIR = Path(__file__).parent
CAMERAS_DIR = BASE_DIR / "cameras"
DATA_DIR = BASE_DIR / "data"
REFERENCES_DIR = DATA_DIR / "referencias"
MARCACOES_FILE = DATA_DIR / "marcacoes.json"
ANALYSIS_CACHE_FILE = DATA_DIR / "analysis_cache.json"
METADATA_FILE = DATA_DIR / "camera_metadata.json"

# Garantir que diretórios existem
DATA_DIR.mkdir(exist_ok=True)
REFERENCES_DIR.mkdir(exist_ok=True)

# Inicializar comparador de imagens
if VISION_AVAILABLE:
    image_comparator = ImageComparator(REFERENCES_DIR)
else:
    image_comparator = None

# Inicializar gerenciador de downloads
if DOWNLOADER_AVAILABLE:
    download_manager = DownloadManager(output_dir=str(CAMERAS_DIR))
else:
    download_manager = None

# Estado do download (legado - mantido para compatibilidade)
download_status = {
    "running": False,
    "progress": 0,
    "total": 0,
    "current_camera": "",
    "start_time": None
}


def load_marcacoes():
    """Carrega marcações de câmeras ruins"""
    if MARCACOES_FILE.exists():
        with open(MARCACOES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_camera_metadata():
    """Carrega metadados adicionais das câmeras (Lugar, Área, UUID, etc.)"""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erro ao carregar metadados: {e}")
            return {}
    return {}


def is_camera_online(metadata):
    """Verifica se câmera está online baseado em 'última_resposta'

    Considera online se última_resposta foi nos últimos 15 minutos
    """
    if not metadata or 'ultima_resposta' not in metadata:
        return None  # Sem informação

    try:
        from datetime import datetime, timedelta

        # Parse do timestamp: "2025-12-22 07:09:54"
        ultima_resposta_str = metadata['ultima_resposta']
        ultima_resposta = datetime.strptime(ultima_resposta_str, '%Y-%m-%d %H:%M:%S')

        # Calcular diferença
        agora = datetime.now()
        diferenca = agora - ultima_resposta

        # Online se última resposta foi nos últimos 15 minutos
        TIMEOUT_MINUTOS = 15
        online = diferenca <= timedelta(minutes=TIMEOUT_MINUTOS)

        return online
    except Exception as e:
        print(f"⚠️ Erro ao calcular status online: {e}")
        return None


def save_marcacoes(marcacoes):
    """Salva marcações de câmeras ruins"""
    with open(MARCACOES_FILE, 'w', encoding='utf-8') as f:
        json.dump(marcacoes, f, indent=2, ensure_ascii=False)


def get_camera_images():
    """Lista todas as imagens de câmeras organizadas por loja"""
    cameras = []

    if not CAMERAS_DIR.exists():
        return cameras

    # Dicionário para rastrear a imagem mais recente de cada câmera
    latest_images = {}

    # Percorrer todas as pastas de lojas
    for loja_dir in sorted(CAMERAS_DIR.iterdir()):
        if not loja_dir.is_dir():
            continue

        loja_name = loja_dir.name

        # Buscar imagens (P1, P2, P3)
        for img_file in sorted(loja_dir.glob("*.jpg")):
            # Extrair posição da câmera (P1, P2, P3)
            filename = img_file.name
            position = "P?"

            if filename.startswith("P1_"):
                position = "P1"
            elif filename.startswith("P2_"):
                position = "P2"
            elif filename.startswith("P3_"):
                position = "P3"

            # Informações do arquivo
            stat = img_file.stat()
            file_size = stat.st_size
            modified_time = datetime.fromtimestamp(stat.st_mtime)

            # Caminho relativo para servir a imagem
            relative_path = f"cameras/{loja_name}/{filename}"

            # ID único da câmera base (loja_posição)
            camera_base_id = f"{loja_name}_{position}"

            # ID único incluindo timestamp para diferenciar versões
            camera_id = f"{loja_name}_{position}_{int(modified_time.timestamp())}"

            # Rastrear a mais recente
            key = camera_base_id
            if key not in latest_images or modified_time.timestamp() > latest_images[key]:
                latest_images[key] = modified_time.timestamp()

            cameras.append({
                "id": camera_id,
                "base_id": camera_base_id,  # ID sem timestamp para marcação
                "loja": loja_name,
                "position": position,
                "filename": filename,
                "path": relative_path,
                "size": file_size,
                "modified": modified_time.isoformat(),
                "modified_readable": modified_time.strftime("%d/%m/%Y %H:%M:%S"),
                "timestamp": modified_time.timestamp()
            })

    # Marcar quais são as mais recentes
    for camera in cameras:
        key = camera['base_id']
        camera['is_latest'] = (camera['timestamp'] == latest_images.get(key, 0))

    return cameras


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/api/cameras')
def api_cameras():
    """API: Lista todas as câmeras"""
    cameras = get_camera_images()
    marcacoes = load_marcacoes()
    metadata = load_camera_metadata()

    # Adicionar status de marcação e metadados extras a cada câmera (usa base_id)
    for camera in cameras:
        base_id = camera['base_id']

        # Marcações
        if base_id in marcacoes:
            camera['marked'] = True
            camera['mark_info'] = marcacoes[base_id]
        else:
            camera['marked'] = False

        # Metadados adicionais (Lugar, Área, UUID, IPs, etc.)
        if base_id in metadata:
            camera['metadata'] = metadata[base_id]
            # Calcular status online/offline
            camera['online'] = is_camera_online(metadata[base_id])
        else:
            camera['metadata'] = None
            camera['online'] = None

    return jsonify({
        "success": True,
        "total": len(cameras),
        "cameras": cameras
    })


@app.route('/api/stores')
def api_stores():
    """API: Lista todas as lojas únicas"""
    cameras = get_camera_images()

    # Extrair lojas únicas e ordenar
    stores = sorted(set(c['loja'] for c in cameras))

    return jsonify({
        "success": True,
        "total": len(stores),
        "stores": stores
    })


@app.route('/api/cameras/<camera_id>/mark', methods=['POST'])
def api_mark_camera(camera_id):
    """API: Marcar câmera como ruim"""
    marcacoes = load_marcacoes()

    data = request.get_json() or {}
    note = data.get('note', '')

    marcacoes[camera_id] = {
        "marked_at": datetime.now().isoformat(),
        "note": note
    }

    save_marcacoes(marcacoes)

    return jsonify({
        "success": True,
        "message": "Câmera marcada como ruim",
        "camera_id": camera_id
    })


@app.route('/api/cameras/<camera_id>/unmark', methods=['POST'])
def api_unmark_camera(camera_id):
    """API: Desmarcar câmera"""
    marcacoes = load_marcacoes()

    if camera_id in marcacoes:
        del marcacoes[camera_id]
        save_marcacoes(marcacoes)

    return jsonify({
        "success": True,
        "message": "Marcação removida",
        "camera_id": camera_id
    })


@app.route('/api/stats')
def api_stats():
    """API: Estatísticas gerais"""
    cameras = get_camera_images()
    marcacoes = load_marcacoes()

    # Contar lojas únicas
    lojas = set(c['loja'] for c in cameras)

    # Última atualização
    last_update = None
    if cameras:
        last_update = max(c['modified'] for c in cameras)

    # Espaço usado
    total_size = sum(c['size'] for c in cameras)

    return jsonify({
        "success": True,
        "stats": {
            "total_cameras": len(cameras),
            "total_stores": len(lojas),
            "marked_bad": len(marcacoes),
            "marked_ok": len(cameras) - len(marcacoes),
            "last_update": last_update,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
    })


@app.route('/api/download/start', methods=['POST'])
def api_download_start():
    """API: Iniciar download paralelo de câmeras"""
    if not DOWNLOADER_AVAILABLE:
        return jsonify({
            "success": False,
            "message": "Módulo de download não disponível"
        }), 503

    if download_manager.get_stats()['running']:
        return jsonify({
            "success": False,
            "message": "Download já em execução"
        }), 400

    def run_download():
        download_manager.executar_download_completo()

    # Executar em thread separada
    thread = threading.Thread(target=run_download, daemon=True)
    thread.start()

    return jsonify({
        "success": True,
        "message": "Download paralelo iniciado"
    })


@app.route('/api/download/status')
def api_download_status():
    """API: Status do download (polling)"""
    if not DOWNLOADER_AVAILABLE:
        return jsonify({
            "success": False,
            "message": "Módulo de download não disponível"
        }), 503

    stats = download_manager.get_stats()

    return jsonify({
        "success": True,
        "status": {
            "running": stats['running'],
            "progress": stats['progresso'],
            "total": stats['total'],
            "current_camera": stats['atual'],
            "sucesso": stats['sucesso'],
            "falha": stats['falha']
        }
    })


@app.route('/api/download/status-stream')
def api_download_status_stream():
    """API: Status do download via Server-Sent Events (SSE)"""
    if not DOWNLOADER_AVAILABLE:
        return jsonify({
            "success": False,
            "message": "Módulo de download não disponível"
        }), 503

    def generate():
        """Gera eventos SSE com status do download"""
        import time

        max_iterations = 7200  # 1 hora máximo (7200 * 0.5s)
        iterations = 0

        while iterations < max_iterations:
            iterations += 1
            stats = download_manager.get_stats()

            # Enviar dados no formato SSE
            data = json.dumps({
                "running": stats['running'],
                "progresso": stats['progresso'],
                "total": stats['total'],
                "atual": stats['atual'],
                "sucesso": stats['sucesso'],
                "falha": stats['falha']
            })

            yield f"data: {data}\n\n"

            # Se terminou (não está rodando), enviar evento final e parar
            if not stats['running']:
                yield f"data: {json.dumps({'done': True, 'sucesso': stats['sucesso'], 'falha': stats['falha']})}\n\n"
                break

            time.sleep(0.5)  # Atualizar a cada 500ms

    return app.response_class(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@app.route('/api/export/marked')
def api_export_marked():
    """API: Exportar lista de câmeras marcadas como ruins"""
    marcacoes = load_marcacoes()
    cameras = get_camera_images()

    # Criar dicionário de câmeras por ID
    cameras_dict = {c['id']: c for c in cameras}

    # Montar lista de câmeras marcadas com detalhes
    marked_list = []
    for camera_id, mark_info in marcacoes.items():
        if camera_id in cameras_dict:
            camera = cameras_dict[camera_id]
            marked_list.append({
                "loja": camera['loja'],
                "position": camera['position'],
                "filename": camera['filename'],
                "marked_at": mark_info['marked_at'],
                "note": mark_info.get('note', '')
            })

    return jsonify({
        "success": True,
        "total": len(marked_list),
        "cameras": marked_list
    })


@app.route('/cameras/<path:filename>')
def serve_camera_image(filename):
    """Servir imagens de câmeras"""
    return send_from_directory(CAMERAS_DIR, filename)


@app.route('/data/referencias/<path:filename>')
def serve_reference_image(filename):
    """Servir imagens de referências"""
    return send_from_directory(REFERENCES_DIR, filename)


# ==================== APIs de Análise de Imagens ====================

def load_analysis_cache():
    """Carrega cache de análises"""
    if ANALYSIS_CACHE_FILE.exists():
        with open(ANALYSIS_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_analysis_cache(cache):
    """Salva cache de análises"""
    with open(ANALYSIS_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


@app.route('/api/vision/status')
def api_vision_status():
    """API: Verifica se análise de imagens está disponível"""
    return jsonify({
        "success": True,
        "vision_available": VISION_AVAILABLE,
        "opencv_available": VISION_AVAILABLE,
        "references_count": len(list(REFERENCES_DIR.glob("*.jpg"))) if REFERENCES_DIR.exists() else 0
    })


@app.route('/api/vision/references')
def api_list_references():
    """API: Lista todas as referências salvas"""
    if not image_comparator:
        return jsonify({"success": False, "error": "Módulo de visão não disponível"}), 503

    references = image_comparator.list_references()

    return jsonify({
        "success": True,
        "references": references,
        "total": len(references)
    })


@app.route('/api/vision/reference/<loja>/<position>', methods=['POST'])
def api_set_reference(loja, position):
    """API: Define uma imagem como referência"""
    if not image_comparator:
        return jsonify({"success": False, "error": "Módulo de visão não disponível"}), 503

    data = request.get_json() or {}
    image_path = data.get('image_path')

    if not image_path:
        return jsonify({"success": False, "error": "image_path não fornecido"}), 400

    # Caminho completo
    full_path = BASE_DIR / image_path

    if not full_path.exists():
        return jsonify({"success": False, "error": "Imagem não encontrada"}), 404

    # Salvar como referência
    success = image_comparator.save_reference(loja, position, str(full_path))

    if success:
        return jsonify({
            "success": True,
            "message": f"Referência salva para {loja} - {position}",
            "reference_path": str(REFERENCES_DIR / f"{loja}_{position}.jpg")
        })
    else:
        return jsonify({"success": False, "error": "Erro ao salvar referência"}), 500


@app.route('/api/vision/auto-learn', methods=['POST'])
def api_auto_learn_references():
    """API: Auto-aprendizado - usa as imagens mais recentes como referência"""
    if not image_comparator:
        return jsonify({"success": False, "error": "Módulo de visão não disponível"}), 503

    cameras = get_camera_images()
    learned = []

    # Agrupar por loja/posição e pegar apenas as mais recentes
    latest_cameras = {}
    for camera in cameras:
        if camera['is_latest']:
            key = f"{camera['loja']}_{camera['position']}"
            latest_cameras[key] = camera

    # Salvar cada uma como referência
    for key, camera in latest_cameras.items():
        full_path = BASE_DIR / camera['path']
        success = image_comparator.save_reference(
            camera['loja'],
            camera['position'],
            str(full_path)
        )

        if success:
            learned.append({
                "loja": camera['loja'],
                "position": camera['position'],
                "reference": camera['filename']
            })

    return jsonify({
        "success": True,
        "message": f"{len(learned)} referências aprendidas",
        "learned": learned
    })


@app.route('/api/vision/references/clear', methods=['DELETE'])
def api_clear_all_references():
    """API: Remove TODAS as referências salvas"""
    if not image_comparator:
        return jsonify({"success": False, "error": "Módulo de visão não disponível"}), 503

    try:
        # Deletar todos os arquivos .jpg do diretório de referências
        deleted_count = 0
        for ref_file in REFERENCES_DIR.glob("*.jpg"):
            ref_file.unlink()
            deleted_count += 1

        # Limpar cache de análises também
        if ANALYSIS_CACHE_FILE.exists():
            ANALYSIS_CACHE_FILE.unlink()

        return jsonify({
            "success": True,
            "message": f"{deleted_count} referências removidas",
            "deleted_count": deleted_count
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/vision/reference/<loja>/<position>', methods=['DELETE'])
def api_delete_reference(loja, position):
    """API: Remove uma referência específica"""
    if not image_comparator:
        return jsonify({"success": False, "error": "Módulo de visão não disponível"}), 503

    try:
        ref_file = REFERENCES_DIR / f"{loja}_{position}.jpg"

        if not ref_file.exists():
            return jsonify({"success": False, "error": "Referência não encontrada"}), 404

        ref_file.unlink()

        return jsonify({
            "success": True,
            "message": f"Referência removida: {loja} - {position}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/vision/compare', methods=['POST'])
def api_compare_image():
    """API: Compara uma imagem com sua referência"""
    if not image_comparator:
        return jsonify({"success": False, "error": "Módulo de visão não disponível"}), 503

    data = request.get_json() or {}
    loja = data.get('loja')
    position = data.get('position')
    image_path = data.get('image_path')
    analysis_mode = data.get('analysis_mode', 'complete')  # 'complete' ou 'structural'

    if not all([loja, position, image_path]):
        return jsonify({"success": False, "error": "Parâmetros incompletos"}), 400

    # Buscar referência
    ref_path = image_comparator.get_reference_path(loja, position)

    if not ref_path:
        return jsonify({
            "success": False,
            "error": "Referência não encontrada",
            "has_reference": False
        }), 404

    # Caminho completo da imagem atual
    current_path = BASE_DIR / image_path

    if not current_path.exists():
        return jsonify({"success": False, "error": "Imagem atual não encontrada"}), 404

    # Comparar com modo selecionado
    structural_only = (analysis_mode == 'structural')
    result = image_comparator.compare_images(str(ref_path), str(current_path), use_claude=False, structural_only=structural_only)

    # Salvar no cache
    cache = load_analysis_cache()
    cache_key = f"{loja}_{position}_{Path(image_path).stem}"
    cache[cache_key] = {
        **result,
        "analyzed_at": datetime.now().isoformat(),
        "reference": str(ref_path),
        "current": image_path
    }
    save_analysis_cache(cache)

    return jsonify({
        "success": True,
        "has_reference": True,
        "result": result
    })


@app.route('/api/vision/analyze-all', methods=['POST'])
def api_analyze_all():
    """API: Analisa todas as câmeras mais recentes"""
    if not image_comparator:
        return jsonify({"success": False, "error": "Módulo de visão não disponível"}), 503

    data = request.get_json() or {}
    analysis_mode = data.get('analysis_mode', 'complete')  # 'complete' ou 'structural'
    structural_only = (analysis_mode == 'structural')

    cameras = get_camera_images()
    analyzed = []
    skipped = []

    # Analisar apenas as mais recentes
    for camera in cameras:
        if not camera['is_latest']:
            continue

        # Buscar referência
        ref_path = image_comparator.get_reference_path(camera['loja'], camera['position'])

        if not ref_path:
            skipped.append({
                "loja": camera['loja'],
                "position": camera['position'],
                "reason": "Sem referência"
            })
            continue

        # Comparar com modo selecionado
        current_path = BASE_DIR / camera['path']
        result = image_comparator.compare_images(str(ref_path), str(current_path), use_claude=False, structural_only=structural_only)

        analyzed.append({
            "loja": camera['loja'],
            "position": camera['position'],
            "filename": camera['filename'],
            "score": result['final_score'],
            "status": result['status']
        })

        # Salvar no cache
        cache = load_analysis_cache()
        cache_key = camera['base_id']
        cache[cache_key] = {
            **result,
            "analyzed_at": datetime.now().isoformat()
        }
        save_analysis_cache(cache)

    return jsonify({
        "success": True,
        "analyzed": len(analyzed),
        "skipped": len(skipped),
        "results": analyzed,
        "skipped_details": skipped
    })


@app.route('/api/vision/cache')
def api_get_analysis_cache():
    """API: Retorna cache de análises"""
    cache = load_analysis_cache()

    return jsonify({
        "success": True,
        "cache": cache,
        "total": len(cache)
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🎥 Dashboard de Câmeras AIVisual")
    print("=" * 60)
    print(f"📁 Diretório de câmeras: {CAMERAS_DIR}")
    print(f"💾 Arquivo de marcações: {MARCACOES_FILE}")
    print("=" * 60)
    print("🌐 Acesse: http://localhost:5000")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=True)

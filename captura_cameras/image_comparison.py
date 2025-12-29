#!/usr/bin/env python3
"""
Módulo de Comparação de Imagens
Sistema híbrido: OpenCV (rápido) + Claude Vision (inteligente)
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
import base64

try:
    import cv2
    import numpy as np
    from skimage.metrics import structural_similarity as ssim
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("⚠️ OpenCV não instalado. Instale com: pip3 install opencv-python scikit-image")

# Configurações - Thresholds ajustados para detectar mais problemas
SIMILARITY_THRESHOLD = 85  # Score mínimo para considerar OK (0-100)
CLAUDE_THRESHOLD = 60      # Abaixo disso, usa Claude para análise detalhada
PROBLEM_THRESHOLD = 70     # Abaixo disso é considerado problema
CRITICAL_THRESHOLD = 50    # Abaixo disso é crítico


class ImageComparator:
    """Classe para comparação de imagens com sistema híbrido"""

    def __init__(self, references_dir: Path, api_key: Optional[str] = None):
        self.references_dir = Path(references_dir)
        self.references_dir.mkdir(exist_ok=True)
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

    def calculate_ssim(self, image1_path: str, image2_path: str) -> float:
        """
        Calcula SSIM (Structural Similarity Index) entre duas imagens
        Retorna valor entre 0-100 (100 = idênticas)
        """
        if not OPENCV_AVAILABLE:
            return -1

        try:
            # Carregar imagens
            img1 = cv2.imread(str(image1_path))
            img2 = cv2.imread(str(image2_path))

            if img1 is None or img2 is None:
                return -1

            # Redimensionar para mesmo tamanho (necessário para SSIM)
            height, width = img1.shape[:2]
            img2_resized = cv2.resize(img2, (width, height))

            # Converter para escala de cinza
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)

            # Calcular SSIM
            score, _ = ssim(gray1, gray2, full=True)

            # Converter para porcentagem
            return round(score * 100, 2)

        except Exception as e:
            print(f"Erro ao calcular SSIM: {e}")
            return -1

    def calculate_histogram_similarity(self, image1_path: str, image2_path: str) -> float:
        """
        Calcula similaridade de histograma entre duas imagens
        Retorna valor entre 0-100
        """
        if not OPENCV_AVAILABLE:
            return -1

        try:
            img1 = cv2.imread(str(image1_path))
            img2 = cv2.imread(str(image2_path))

            if img1 is None or img2 is None:
                return -1

            # Redimensionar
            height, width = img1.shape[:2]
            img2_resized = cv2.resize(img2, (width, height))

            # Calcular histogramas para cada canal
            hist1_b = cv2.calcHist([img1], [0], None, [256], [0, 256])
            hist1_g = cv2.calcHist([img1], [1], None, [256], [0, 256])
            hist1_r = cv2.calcHist([img1], [2], None, [256], [0, 256])

            hist2_b = cv2.calcHist([img2_resized], [0], None, [256], [0, 256])
            hist2_g = cv2.calcHist([img2_resized], [1], None, [256], [0, 256])
            hist2_r = cv2.calcHist([img2_resized], [2], None, [256], [0, 256])

            # Comparar usando correlação
            corr_b = cv2.compareHist(hist1_b, hist2_b, cv2.HISTCMP_CORREL)
            corr_g = cv2.compareHist(hist1_g, hist2_g, cv2.HISTCMP_CORREL)
            corr_r = cv2.compareHist(hist1_r, hist2_r, cv2.HISTCMP_CORREL)

            # Média das correlações
            avg_corr = (corr_b + corr_g + corr_r) / 3

            # Converter para porcentagem
            return round(avg_corr * 100, 2)

        except Exception as e:
            print(f"Erro ao calcular similaridade de histograma: {e}")
            return -1

    async def analyze_with_claude(self, reference_path: str, current_path: str) -> Dict:
        """
        Usa Claude Vision API para análise detalhada
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "API key não configurada",
                "score": 0,
                "analysis": "Configure ANTHROPIC_API_KEY para usar análise com IA"
            }

        try:
            # Importar Anthropic (só quando necessário)
            from anthropic import Anthropic

            client = Anthropic(api_key=self.api_key)

            # Carregar e encodar imagens
            with open(reference_path, 'rb') as f:
                ref_b64 = base64.b64encode(f.read()).decode('utf-8')

            with open(current_path, 'rb') as f:
                cur_b64 = base64.b64encode(f.read()).decode('utf-8')

            # Criar prompt
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": ref_b64
                            }
                        },
                        {
                            "type": "text",
                            "text": "Esta é a imagem de REFERÊNCIA de uma câmera de segurança em posição ideal."
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": cur_b64
                            }
                        },
                        {
                            "type": "text",
                            "text": """Esta é a imagem ATUAL da mesma câmera.

Compare as duas imagens e responda em formato JSON:

{
  "score": <número 0-100 indicando similaridade>,
  "status": "<OK|RUIM|ATENÇÃO>",
  "issues": ["lista de problemas encontrados"],
  "summary": "resumo da análise"
}

Considere:
- Posição e ângulo da câmera
- Obstruções (objetos, pessoas bloqueando)
- Iluminação (muito escura/clara)
- Qualidade da imagem
- Elementos visíveis no enquadramento"""
                        }
                    ]
                }]
            )

            # Extrair resposta
            response_text = message.content[0].text

            # Tentar parsear JSON
            try:
                # Remover markdown se presente
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()

                result = json.loads(response_text)

                return {
                    "success": True,
                    "score": result.get("score", 0),
                    "status": result.get("status", "UNKNOWN"),
                    "issues": result.get("issues", []),
                    "summary": result.get("summary", ""),
                    "analysis": response_text
                }

            except json.JSONDecodeError:
                return {
                    "success": True,
                    "score": 50,
                    "status": "UNKNOWN",
                    "issues": [],
                    "summary": response_text,
                    "analysis": response_text
                }

        except ImportError:
            return {
                "success": False,
                "error": "Anthropic SDK não instalado. Instale com: pip3 install anthropic",
                "score": 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "score": 0
            }

    def compare_images(self, reference_path: str, current_path: str, use_claude: bool = True, structural_only: bool = False) -> Dict:
        """
        Sistema híbrido de comparação
        1. Tenta SSIM (rápido)
        2. Se score < threshold e use_claude=True, usa Claude para análise detalhada

        Args:
            structural_only: Se True, usa apenas SSIM (detecta mudanças de posição da câmera),
                           ignorando mudanças de conteúdo (pessoas, objetos)
        """
        result = {
            "method": "opencv",
            "mode": "structural" if structural_only else "complete",
            "ssim_score": -1,
            "histogram_score": -1,
            "final_score": 0,
            "status": "UNKNOWN",
            "issues": [],
            "summary": "",
            "used_claude": False
        }

        # Fase 1: Análise com OpenCV
        if OPENCV_AVAILABLE:
            ssim_score = self.calculate_ssim(reference_path, current_path)
            result["ssim_score"] = ssim_score

            if structural_only:
                # Modo estrutural: Usa APENAS SSIM (detecta mudança de posição)
                # SSIM detecta mudanças na estrutura da imagem
                result["final_score"] = ssim_score if ssim_score >= 0 else 0
                result["histogram_score"] = -1  # Não usado neste modo

                # Classificação estrutural com 5 níveis
                if result["final_score"] >= 90:
                    result["status"] = "EXCELENTE"
                    result["summary"] = "Câmera perfeitamente posicionada"
                elif result["final_score"] >= 80:
                    result["status"] = "BOM"
                    result["summary"] = "Câmera bem posicionada"
                elif result["final_score"] >= 65:
                    result["status"] = "ATENÇÃO"
                    result["summary"] = "Pequeno desalinhamento detectado"
                elif result["final_score"] >= 45:
                    result["status"] = "PROBLEMA"
                    result["summary"] = "Câmera desalinhada ou movida"
                    result["issues"] = ["Possível movimento da câmera"]
                else:
                    result["status"] = "CRÍTICO"
                    result["summary"] = "Câmera severamente desalinhada ou obstruída"
                    result["issues"] = ["Mudança estrutural significativa"]
            else:
                # Modo completo: Usa SSIM + Histograma
                hist_score = self.calculate_histogram_similarity(reference_path, current_path)
                result["histogram_score"] = hist_score

                # Média ponderada (SSIM tem mais peso)
                if ssim_score >= 0 and hist_score >= 0:
                    result["final_score"] = round((ssim_score * 0.7) + (hist_score * 0.3), 2)
                elif ssim_score >= 0:
                    result["final_score"] = ssim_score
                elif hist_score >= 0:
                    result["final_score"] = hist_score

                # Classificação completa com 5 níveis
                if result["final_score"] >= 90:
                    result["status"] = "EXCELENTE"
                    result["summary"] = "Imagem praticamente idêntica à referência"
                elif result["final_score"] >= SIMILARITY_THRESHOLD:  # >= 85
                    result["status"] = "BOM"
                    result["summary"] = "Imagem muito similar à referência"
                elif result["final_score"] >= PROBLEM_THRESHOLD:  # >= 70
                    result["status"] = "ATENÇÃO"
                    result["summary"] = "Diferenças detectadas (pessoas, objetos ou iluminação)"
                    result["issues"] = ["Mudanças no conteúdo da cena"]
                elif result["final_score"] >= CRITICAL_THRESHOLD:  # >= 50
                    result["status"] = "PROBLEMA"
                    result["summary"] = f"Diferenças significativas detectadas ({result['final_score']:.1f}%)"
                    result["issues"] = ["Mudanças importantes na cena", "Verificar obstruções ou iluminação"]
                else:
                    result["status"] = "CRÍTICO"
                    result["summary"] = f"Imagem muito diferente da referência ({result['final_score']:.1f}%)"
                    result["issues"] = ["Câmera possivelmente movida", "Obstrução grave", "Verificar urgentemente"]

        # Fase 2: Análise com Claude (se necessário)
        if use_claude and result["final_score"] < CLAUDE_THRESHOLD and result["final_score"] >= 0:
            print(f"Score baixo ({result['final_score']}%), usando Claude para análise detalhada...")
            # Nota: Esta parte precisa ser async, então retorna info para chamar depois
            result["needs_claude_analysis"] = True

        return result

    def get_reference_path(self, loja: str, position: str) -> Optional[Path]:
        """Retorna caminho da imagem de referência para loja/posição"""
        ref_file = self.references_dir / f"{loja}_{position}.jpg"
        return ref_file if ref_file.exists() else None

    def save_reference(self, loja: str, position: str, image_path: str) -> bool:
        """Salva uma imagem como referência"""
        try:
            if not OPENCV_AVAILABLE:
                # Cópia simples sem OpenCV
                import shutil
                ref_path = self.references_dir / f"{loja}_{position}.jpg"
                shutil.copy(image_path, ref_path)
                return True

            # Com OpenCV, pode redimensionar/otimizar
            img = cv2.imread(str(image_path))
            if img is None:
                return False

            ref_path = self.references_dir / f"{loja}_{position}.jpg"
            cv2.imwrite(str(ref_path), img, [cv2.IMWRITE_JPEG_QUALITY, 95])
            return True

        except Exception as e:
            print(f"Erro ao salvar referência: {e}")
            return False

    def list_references(self) -> Dict[str, Dict]:
        """Lista todas as referências salvas"""
        references = {}

        for ref_file in self.references_dir.glob("*.jpg"):
            # Parse do nome do arquivo: loja_position.jpg
            name = ref_file.stem
            parts = name.rsplit('_', 1)

            if len(parts) == 2:
                loja, position = parts
                if loja not in references:
                    references[loja] = {}

                references[loja][position] = {
                    "path": str(ref_file),
                    "exists": True,
                    "size": ref_file.stat().st_size
                }

        return references


if __name__ == "__main__":
    # Teste básico
    print("🔍 Testando módulo de comparação de imagens")
    print(f"OpenCV disponível: {OPENCV_AVAILABLE}")

    comparator = ImageComparator(Path("data/referencias"))
    print(f"Diretório de referências: {comparator.references_dir}")

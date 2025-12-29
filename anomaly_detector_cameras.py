#!/usr/bin/env python3
"""
Camera-Specific Anomaly Detection with Business Logic
Detects cameras that are obstructed, misaligned, or malfunctioning

Business Rules:
- P1 = Menu area (order placement)
- P2 = Payment area (cashier)
- P3 = Pickup area (order delivery)
- All cameras should capture similar scenes (people, counters, movement)
- If one camera has significantly different file sizes, it may be obstructed/misaligned

Author: AI/ML Task Executor
Date: 2025-12-29
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class CameraAnomalyDetector:
    """Enhanced anomaly detector with camera position awareness"""

    def __init__(self, contamination=0.1):
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
            max_samples='auto',
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.metadata = []
        self.stores_data = defaultdict(lambda: {'P1': [], 'P2': [], 'P3': []})

    def collect_metadata(self, base_path):
        """Collect file metadata grouped by store and camera position"""
        print(f"[INFO] Scanning directory: {base_path}")

        base_path = Path(base_path)
        if not base_path.exists():
            print(f"[ERROR] Path does not exist: {base_path}")
            return []

        metadata_list = []

        for root, dirs, files in os.walk(base_path):
            root_path = Path(root)

            for filename in files:
                if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue

                filepath = root_path / filename

                try:
                    stats = filepath.stat()

                    # Extract camera position and store name
                    parts = filename.split('_')
                    camera_position = None
                    store_name = str(root_path.relative_to(base_path))

                    if len(parts) >= 1 and parts[0] in ['P1', 'P2', 'P3']:
                        camera_position = parts[0]

                    metadata = {
                        'filepath': str(filepath),
                        'filename': filename,
                        'store': store_name,
                        'camera_position': camera_position,
                        'size_bytes': stats.st_size,
                        'size_kb': stats.st_size / 1024,
                        'size_mb': stats.st_size / (1024 * 1024),
                        'modified_timestamp': stats.st_mtime,
                        'depth': len(root_path.relative_to(base_path).parts)
                    }

                    metadata_list.append(metadata)

                    # Group by store and camera position
                    if camera_position and store_name != '.':
                        self.stores_data[store_name][camera_position].append(metadata)

                except (OSError, PermissionError) as e:
                    print(f"[WARNING] Cannot access {filepath}: {e}")

        print(f"[INFO] Collected metadata for {len(metadata_list)} files")
        print(f"[INFO] Found {len(self.stores_data)} stores")

        self.metadata = metadata_list
        return metadata_list

    def analyze_camera_positions(self):
        """Analyze if cameras at same store have consistent sizes"""
        print("\n[INFO] Analyzing camera position consistency...")

        issues = []

        for store, cameras in self.stores_data.items():
            if store == '.':
                continue

            # Calculate average sizes for each camera position
            p1_sizes = [f['size_kb'] for f in cameras['P1']]
            p2_sizes = [f['size_kb'] for f in cameras['P2']]
            p3_sizes = [f['size_kb'] for f in cameras['P3']]

            if not (p1_sizes and p2_sizes and p3_sizes):
                continue  # Skip if any camera position is missing

            p1_avg = np.mean(p1_sizes)
            p2_avg = np.mean(p2_sizes)
            p3_avg = np.mean(p3_sizes)

            store_avg = np.mean([p1_avg, p2_avg, p3_avg])

            # Check if any camera deviates significantly (>40% from store average)
            threshold = 0.40

            p1_deviation = abs(p1_avg - store_avg) / store_avg
            p2_deviation = abs(p2_avg - store_avg) / store_avg
            p3_deviation = abs(p3_avg - store_avg) / store_avg

            issue_detected = False
            problem_cameras = []

            if p1_deviation > threshold:
                issue_detected = True
                problem_cameras.append({
                    'camera': 'P1',
                    'area': 'Menu (Pedidos)',
                    'avg_size': p1_avg,
                    'expected': store_avg,
                    'deviation_pct': p1_deviation * 100
                })

            if p2_deviation > threshold:
                issue_detected = True
                problem_cameras.append({
                    'camera': 'P2',
                    'area': 'Pagamento (Caixa)',
                    'avg_size': p2_avg,
                    'expected': store_avg,
                    'deviation_pct': p2_deviation * 100
                })

            if p3_deviation > threshold:
                issue_detected = True
                problem_cameras.append({
                    'camera': 'P3',
                    'area': 'Retirada (Entrega)',
                    'avg_size': p3_avg,
                    'expected': store_avg,
                    'deviation_pct': p3_deviation * 100
                })

            if issue_detected:
                issues.append({
                    'store': store,
                    'p1_avg': p1_avg,
                    'p2_avg': p2_avg,
                    'p3_avg': p3_avg,
                    'store_avg': store_avg,
                    'problem_cameras': problem_cameras
                })

        return issues

    def generate_camera_report(self, output_path='camera_analysis_report.json'):
        """Generate report focusing on camera-specific issues"""
        print(f"[INFO] Generating camera analysis report...")

        # Analyze camera position consistency
        camera_issues = self.analyze_camera_positions()

        # Calculate global statistics by camera position
        all_p1 = []
        all_p2 = []
        all_p3 = []

        for store, cameras in self.stores_data.items():
            if store == '.':
                continue
            all_p1.extend([f['size_kb'] for f in cameras['P1']])
            all_p2.extend([f['size_kb'] for f in cameras['P2']])
            all_p3.extend([f['size_kb'] for f in cameras['P3']])

        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_stores': len([s for s in self.stores_data.keys() if s != '.']),
                'total_files': len(self.metadata),
                'analysis_type': 'Camera Position Consistency Check'
            },
            'camera_positions': {
                'P1_Menu_Pedidos': {
                    'description': 'Câmera do menu de pedidos',
                    'total_files': len(all_p1),
                    'avg_size_kb': float(np.mean(all_p1)) if all_p1 else 0,
                    'median_size_kb': float(np.median(all_p1)) if all_p1 else 0,
                    'std_dev_kb': float(np.std(all_p1)) if all_p1 else 0
                },
                'P2_Pagamento_Caixa': {
                    'description': 'Câmera do pagamento/caixa',
                    'total_files': len(all_p2),
                    'avg_size_kb': float(np.mean(all_p2)) if all_p2 else 0,
                    'median_size_kb': float(np.median(all_p2)) if all_p2 else 0,
                    'std_dev_kb': float(np.std(all_p2)) if all_p2 else 0
                },
                'P3_Retirada_Entrega': {
                    'description': 'Câmera da retirada/entrega',
                    'total_files': len(all_p3),
                    'avg_size_kb': float(np.mean(all_p3)) if all_p3 else 0,
                    'median_size_kb': float(np.median(all_p3)) if all_p3 else 0,
                    'std_dev_kb': float(np.std(all_p3)) if all_p3 else 0
                }
            },
            'camera_issues': {
                'total_stores_with_issues': len(camera_issues),
                'details': camera_issues
            },
            'recommendations': self._generate_camera_recommendations(camera_issues)
        }

        # Save report
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"[SUCCESS] Camera report saved to: {output_path}")

        return report

    def _generate_camera_recommendations(self, issues):
        """Generate recommendations based on camera issues"""
        recommendations = []

        for issue in issues:
            store = issue['store']

            for cam in issue['problem_cameras']:
                severity = 'CRITICAL' if cam['deviation_pct'] > 60 else 'HIGH'

                # Determine likely problem
                if cam['avg_size'] < cam['expected']:
                    problem = 'Câmera possivelmente OBSTRUÍDA, VIRADA PARA BAIXO ou DESALINHADA'
                    action = f"Inspecionar fisicamente câmera {cam['camera']} ({cam['area']}). Arquivo {cam['deviation_pct']:.1f}% menor que esperado."
                else:
                    problem = 'Câmera com tamanho de arquivo anormalmente GRANDE'
                    action = f"Verificar configuração de resolução/compressão da câmera {cam['camera']} ({cam['area']})."

                recommendations.append({
                    'priority': severity,
                    'store': store,
                    'camera': cam['camera'],
                    'area': cam['area'],
                    'problem': problem,
                    'action': action,
                    'avg_size_kb': cam['avg_size'],
                    'expected_kb': cam['expected'],
                    'deviation_pct': cam['deviation_pct']
                })

        # Sort by deviation (worst first)
        recommendations.sort(key=lambda x: x['deviation_pct'], reverse=True)

        return recommendations

    def print_camera_summary(self, report):
        """Print human-readable camera analysis summary"""
        print("\n" + "="*80)
        print("ANÁLISE DE CÂMERAS - DETECÇÃO DE OBSTRUÇÕES E DESALINHAMENTOS")
        print("="*80)

        print(f"\nGerado: {report['metadata']['generated_at']}")
        print(f"Total de Lojas: {report['metadata']['total_stores']}")
        print(f"Total de Arquivos: {report['metadata']['total_files']}")

        print("\n" + "-"*80)
        print("ESTATÍSTICAS POR POSIÇÃO DE CÂMERA")
        print("-"*80)

        for pos, data in report['camera_positions'].items():
            print(f"\n{pos}:")
            print(f"  Descrição: {data['description']}")
            print(f"  Arquivos: {data['total_files']}")
            print(f"  Tamanho Médio: {data['avg_size_kb']:.2f} KB")
            print(f"  Mediana: {data['median_size_kb']:.2f} KB")
            print(f"  Desvio Padrão: {data['std_dev_kb']:.2f} KB")

        print("\n" + "-"*80)
        print("CÂMERAS COM PROBLEMAS DETECTADOS")
        print("-"*80)

        issues_count = report['camera_issues']['total_stores_with_issues']
        print(f"\n🚨 Total de lojas com problemas: {issues_count}")

        if issues_count == 0:
            print("\n✅ Nenhum problema crítico detectado!")
            print("Todas as câmeras parecem estar funcionando corretamente.")
        else:
            print(f"\n⚠️  {issues_count} lojas requerem atenção:\n")

            for issue in report['camera_issues']['details'][:10]:  # Top 10
                print(f"\n📍 {issue['store']}:")
                print(f"   P1 (Menu): {issue['p1_avg']:.2f} KB")
                print(f"   P2 (Pagamento): {issue['p2_avg']:.2f} KB")
                print(f"   P3 (Retirada): {issue['p3_avg']:.2f} KB")
                print(f"   Média esperada: {issue['store_avg']:.2f} KB")

                for cam in issue['problem_cameras']:
                    print(f"   🔴 {cam['camera']} ({cam['area']}): {cam['deviation_pct']:.1f}% de desvio")

        print("\n" + "-"*80)
        print("RECOMENDAÇÕES PRIORITÁRIAS")
        print("-"*80)

        for i, rec in enumerate(report['recommendations'][:15], 1):
            print(f"\n{i}. [{rec['priority']}] {rec['store']}")
            print(f"   Câmera: {rec['camera']} - {rec['area']}")
            print(f"   Problema: {rec['problem']}")
            print(f"   Ação: {rec['action']}")
            print(f"   Tamanho: {rec['avg_size_kb']:.2f} KB (esperado: {rec['expected_kb']:.2f} KB)")

        print("\n" + "="*80)
        print("FIM DO RELATÓRIO")
        print("="*80 + "\n")


def main():
    """Main execution"""
    print("="*80)
    print("DETECTOR DE CÂMERAS OBSTRUÍDAS/DESALINHADAS")
    print("Análise baseada em posição de câmera (P1=Menu, P2=Pagamento, P3=Retirada)")
    print("="*80 + "\n")

    BASE_PATH = '/home/marcelo/sistemas/captura_cameras/cameras'
    OUTPUT_REPORT = '/home/marcelo/sistemas/camera_analysis_report.json'

    detector = CameraAnomalyDetector(contamination=0.1)

    # Collect metadata
    detector.collect_metadata(BASE_PATH)

    # Generate camera-specific report
    report = detector.generate_camera_report(OUTPUT_REPORT)

    # Print summary
    detector.print_camera_summary(report)

    print(f"\n[SUCCESS] Relatório completo salvo em: {OUTPUT_REPORT}")
    print("[INFO] Análise completa!\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())

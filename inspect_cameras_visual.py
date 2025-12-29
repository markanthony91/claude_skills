#!/usr/bin/env python3
"""
Visual Camera Inspector
Compares P1/P2/P3 cameras at each store and generates visual reports

Usage:
    python3 inspect_cameras_visual.py                    # Full report
    python3 inspect_cameras_visual.py --problems-only    # Only show problem stores
    python3 inspect_cameras_visual.py --store "StoreName" # Specific store
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict
import numpy as np

class VisualCameraInspector:
    """Visual inspector for camera positions"""

    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.stores_data = defaultdict(lambda: {'P1': [], 'P2': [], 'P3': []})
        self.global_stats = {'P1': [], 'P2': [], 'P3': []}

    def collect_data(self):
        """Collect camera data grouped by store and position"""
        print("📂 Coletando dados das câmeras...")

        for root, dirs, files in os.walk(self.base_path):
            root_path = Path(root)
            store_name = str(root_path.relative_to(self.base_path))

            if store_name == '.':
                continue

            for filename in files:
                if not filename.lower().endswith(('.jpg', '.jpeg')):
                    continue

                filepath = root_path / filename

                try:
                    size_kb = filepath.stat().st_size / 1024

                    # Extract camera position
                    parts = filename.split('_')
                    if len(parts) >= 1 and parts[0] in ['P1', 'P2', 'P3']:
                        camera_pos = parts[0]
                        self.stores_data[store_name][camera_pos].append(size_kb)
                        self.global_stats[camera_pos].append(size_kb)

                except (OSError, PermissionError):
                    continue

        print(f"✓ {len(self.stores_data)} lojas encontradas\n")

    def generate_bar_chart(self, value, max_value, width=40):
        """Generate ASCII bar chart"""
        if max_value == 0:
            return '░' * width

        filled = int((value / max_value) * width)
        filled = min(filled, width)

        return '█' * filled + '░' * (width - filled)

    def get_status_icon(self, deviation_pct):
        """Get status icon based on deviation"""
        if deviation_pct > 60:
            return '🔴'  # Critical
        elif deviation_pct > 40:
            return '🟠'  # High
        elif deviation_pct > 20:
            return '🟡'  # Medium
        else:
            return '🟢'  # OK

    def analyze_store(self, store_name, cameras):
        """Analyze a single store's cameras"""
        p1_sizes = cameras['P1']
        p2_sizes = cameras['P2']
        p3_sizes = cameras['P3']

        if not (p1_sizes and p2_sizes and p3_sizes):
            return None

        p1_avg = np.mean(p1_sizes)
        p2_avg = np.mean(p2_sizes)
        p3_avg = np.mean(p3_sizes)

        store_avg = np.mean([p1_avg, p2_avg, p3_avg])

        # Calculate deviations
        p1_dev = abs(p1_avg - store_avg) / store_avg * 100
        p2_dev = abs(p2_avg - store_avg) / store_avg * 100
        p3_dev = abs(p3_avg - store_avg) / store_avg * 100

        max_deviation = max(p1_dev, p2_dev, p3_dev)

        # Determine problem cameras
        problems = []
        if p1_dev > 40:
            direction = "menor" if p1_avg < store_avg else "maior"
            problems.append({
                'camera': 'P1',
                'area': 'Menu (Pedidos)',
                'deviation': p1_dev,
                'size': p1_avg,
                'direction': direction,
                'severity': 'CRÍTICO' if p1_dev > 60 else 'ALTO'
            })

        if p2_dev > 40:
            direction = "menor" if p2_avg < store_avg else "maior"
            problems.append({
                'camera': 'P2',
                'area': 'Pagamento (Caixa)',
                'deviation': p2_dev,
                'size': p2_avg,
                'direction': direction,
                'severity': 'CRÍTICO' if p2_dev > 60 else 'ALTO'
            })

        if p3_dev > 40:
            direction = "menor" if p3_avg < store_avg else "maior"
            problems.append({
                'camera': 'P3',
                'area': 'Retirada (Entrega)',
                'deviation': p3_dev,
                'size': p3_avg,
                'direction': direction,
                'severity': 'CRÍTICO' if p3_dev > 60 else 'ALTO'
            })

        return {
            'store': store_name,
            'p1_avg': p1_avg,
            'p2_avg': p2_avg,
            'p3_avg': p3_avg,
            'store_avg': store_avg,
            'p1_dev': p1_dev,
            'p2_dev': p2_dev,
            'p3_dev': p3_dev,
            'max_deviation': max_deviation,
            'has_problems': len(problems) > 0,
            'problems': problems,
            'p1_count': len(p1_sizes),
            'p2_count': len(p2_sizes),
            'p3_count': len(p3_sizes)
        }

    def print_store_visual(self, analysis):
        """Print visual representation of a store's cameras"""
        store = analysis['store']
        max_size = max(analysis['p1_avg'], analysis['p2_avg'], analysis['p3_avg'])

        # Status icons
        p1_icon = self.get_status_icon(analysis['p1_dev'])
        p2_icon = self.get_status_icon(analysis['p2_dev'])
        p3_icon = self.get_status_icon(analysis['p3_dev'])

        print(f"\n{'='*80}")
        print(f"🏪 {store}")
        print(f"{'='*80}\n")

        # P1 - Menu
        print(f"{p1_icon} P1 - Menu (Pedidos)")
        print(f"   {self.generate_bar_chart(analysis['p1_avg'], max_size)}")
        print(f"   {analysis['p1_avg']:.2f} KB ({analysis['p1_count']} arquivos) - Desvio: {analysis['p1_dev']:.1f}%")

        # P2 - Pagamento
        print(f"\n{p2_icon} P2 - Pagamento (Caixa)")
        print(f"   {self.generate_bar_chart(analysis['p2_avg'], max_size)}")
        print(f"   {analysis['p2_avg']:.2f} KB ({analysis['p2_count']} arquivos) - Desvio: {analysis['p2_dev']:.1f}%")

        # P3 - Retirada
        print(f"\n{p3_icon} P3 - Retirada (Entrega)")
        print(f"   {self.generate_bar_chart(analysis['p3_avg'], max_size)}")
        print(f"   {analysis['p3_avg']:.2f} KB ({analysis['p3_count']} arquivos) - Desvio: {analysis['p3_dev']:.1f}%")

        print(f"\n📊 Média da Loja: {analysis['store_avg']:.2f} KB")

        # Show problems if any
        if analysis['has_problems']:
            print(f"\n⚠️  PROBLEMAS DETECTADOS:")
            for prob in analysis['problems']:
                print(f"\n   [{prob['severity']}] Câmera {prob['camera']} - {prob['area']}")
                print(f"   • Tamanho: {prob['size']:.2f} KB ({prob['deviation']:.1f}% {prob['direction']})")

                if prob['direction'] == "menor":
                    print(f"   • Possível causa: Câmera OBSTRUÍDA, VIRADA PARA BAIXO ou DESALINHADA")
                    print(f"   • Ação: Inspecionar fisicamente e realinhar")
                else:
                    print(f"   • Possível causa: Resolução/compressão diferente")
                    print(f"   • Ação: Verificar configuração da câmera")
        else:
            print(f"\n✅ Todas as câmeras funcionando normalmente")

    def generate_summary_report(self, analyses, problems_only=False):
        """Generate summary report"""
        print("\n" + "="*80)
        print("RELATÓRIO VISUAL DE INSPEÇÃO DE CÂMERAS")
        print("="*80)

        # Global statistics
        p1_global_avg = np.mean(self.global_stats['P1']) if self.global_stats['P1'] else 0
        p2_global_avg = np.mean(self.global_stats['P2']) if self.global_stats['P2'] else 0
        p3_global_avg = np.mean(self.global_stats['P3']) if self.global_stats['P3'] else 0

        print("\n📊 ESTATÍSTICAS GLOBAIS:")
        print(f"   P1 (Menu): {p1_global_avg:.2f} KB médio")
        print(f"   P2 (Pagamento): {p2_global_avg:.2f} KB médio")
        print(f"   P3 (Retirada): {p3_global_avg:.2f} KB médio")

        # Count problems
        problem_stores = [a for a in analyses if a['has_problems']]
        ok_stores = [a for a in analyses if not a['has_problems']]

        print(f"\n📈 RESUMO:")
        print(f"   ✅ Lojas OK: {len(ok_stores)} ({len(ok_stores)/len(analyses)*100:.1f}%)")
        print(f"   ⚠️  Lojas com problemas: {len(problem_stores)} ({len(problem_stores)/len(analyses)*100:.1f}%)")

        if problems_only:
            print("\n🔍 EXIBINDO APENAS LOJAS COM PROBLEMAS:\n")
            stores_to_show = problem_stores
        else:
            stores_to_show = analyses

        # Sort by max deviation (worst first)
        stores_to_show.sort(key=lambda x: x['max_deviation'], reverse=True)

        # Print stores
        for analysis in stores_to_show[:20]:  # Limit to top 20
            self.print_store_visual(analysis)

        if len(stores_to_show) > 20:
            print(f"\n... e mais {len(stores_to_show) - 20} lojas")

        # Final recommendations
        print("\n" + "="*80)
        print("RECOMENDAÇÕES FINAIS")
        print("="*80)

        if problem_stores:
            print(f"\n🚨 {len(problem_stores)} lojas requerem inspeção física:")

            for analysis in problem_stores[:10]:
                print(f"\n• {analysis['store']}")
                for prob in analysis['problems']:
                    print(f"  → {prob['camera']} ({prob['area']}): {prob['deviation']:.1f}% {prob['direction']}")
        else:
            print("\n✅ Sistema de câmeras funcionando perfeitamente!")
            print("   Continue com monitoramento regular.")

        print("\n" + "="*80)

    def run(self, problems_only=False, specific_store=None):
        """Main execution"""
        self.collect_data()

        if specific_store:
            # Inspect specific store
            if specific_store in self.stores_data:
                analysis = self.analyze_store(specific_store, self.stores_data[specific_store])
                if analysis:
                    self.print_store_visual(analysis)
                else:
                    print(f"❌ Dados insuficientes para loja: {specific_store}")
            else:
                print(f"❌ Loja não encontrada: {specific_store}")
                print(f"\nLojas disponíveis:")
                for store in sorted(self.stores_data.keys())[:20]:
                    print(f"  - {store}")
            return

        # Analyze all stores
        analyses = []
        for store, cameras in self.stores_data.items():
            analysis = self.analyze_store(store, cameras)
            if analysis:
                analyses.append(analysis)

        # Generate report
        self.generate_summary_report(analyses, problems_only)

        # Export JSON for automation
        output = {
            'generated_at': str(np.datetime64('now')),
            'total_stores': len(analyses),
            'problem_stores': len([a for a in analyses if a['has_problems']]),
            'stores': analyses
        }

        output_path = '/home/marcelo/sistemas/visual_camera_report.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)

        print(f"\n💾 Relatório JSON salvo em: {output_path}\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Visual Camera Inspector')
    parser.add_argument('--problems-only', action='store_true',
                        help='Show only stores with problems')
    parser.add_argument('--store', type=str,
                        help='Inspect specific store')

    args = parser.parse_args()

    base_path = '/home/marcelo/sistemas/captura_cameras/cameras'

    inspector = VisualCameraInspector(base_path)
    inspector.run(problems_only=args.problems_only, specific_store=args.store)


if __name__ == '__main__':
    main()

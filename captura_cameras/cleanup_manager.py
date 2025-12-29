#!/usr/bin/env python3
"""
Gerenciador de Limpeza Automática de Imagens Antigas
Mantém apenas os últimos N dias de histórico
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import shutil
import argparse

def calcular_tamanho_diretorio(path):
    """Calcula tamanho total de um diretório em bytes"""
    total = 0
    for entry in Path(path).rglob('*'):
        if entry.is_file():
            total += entry.stat().st_size
    return total

def formatar_bytes(bytes_size):
    """Formata bytes em formato legível"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def limpar_arquivos_antigos(dias_retencao=7, dry_run=False, arquivar=False):
    """
    Remove ou arquiva imagens mais antigas que N dias

    Args:
        dias_retencao: Manter apenas os últimos N dias
        dry_run: Se True, apenas simula sem deletar
        arquivar: Se True, compacta antes de deletar
    """
    cameras_dir = Path("cameras")

    if not cameras_dir.exists():
        print("❌ Pasta 'cameras' não encontrada")
        return

    data_limite = datetime.now() - timedelta(days=dias_retencao)

    arquivos_para_deletar = []
    arquivos_para_manter = []
    tamanho_total_deletar = 0
    tamanho_total_manter = 0

    print(f"🔍 Analisando arquivos em: {cameras_dir.absolute()}")
    print(f"📅 Data limite: {data_limite:%Y-%m-%d %H:%M:%S}")
    print(f"⏳ Mantendo apenas arquivos dos últimos {dias_retencao} dias")
    print("=" * 80)

    # Percorrer todos os JPGs
    for jpg_file in cameras_dir.rglob("*.jpg"):
        # Pular symlinks
        if jpg_file.is_symlink():
            continue

        # Obter data de modificação
        mtime = datetime.fromtimestamp(jpg_file.stat().st_mtime)
        tamanho = jpg_file.stat().st_size

        if mtime < data_limite:
            arquivos_para_deletar.append({
                'caminho': jpg_file,
                'data': mtime,
                'tamanho': tamanho
            })
            tamanho_total_deletar += tamanho
        else:
            arquivos_para_manter.append({
                'caminho': jpg_file,
                'data': mtime,
                'tamanho': tamanho
            })
            tamanho_total_manter += tamanho

    # Relatório
    print(f"📊 Análise Completa:")
    print(f"   ✅ Arquivos a manter: {len(arquivos_para_manter)} ({formatar_bytes(tamanho_total_manter)})")
    print(f"   🗑️  Arquivos a deletar: {len(arquivos_para_deletar)} ({formatar_bytes(tamanho_total_deletar)})")
    print()

    if len(arquivos_para_deletar) == 0:
        print("✨ Nenhum arquivo antigo encontrado. Tudo limpo!")
        return

    # Arquivar antes de deletar (opcional)
    if arquivar and not dry_run:
        print("📦 Arquivando arquivos antigos...")
        arquivo_tar = Path("archive") / f"backup_{data_limite:%Y%m%d}.tar.gz"
        arquivo_tar.parent.mkdir(exist_ok=True)

        import tarfile
        with tarfile.open(arquivo_tar, "w:gz") as tar:
            for item in arquivos_para_deletar:
                tar.add(item['caminho'], arcname=item['caminho'].relative_to(cameras_dir))

        print(f"   ✅ Arquivo criado: {arquivo_tar} ({formatar_bytes(arquivo_tar.stat().st_size)})")
        print()

    # Listar alguns exemplos
    print("📋 Exemplos de arquivos a deletar:")
    for item in arquivos_para_deletar[:10]:
        print(f"   • {item['caminho'].relative_to(cameras_dir)} - {item['data']:%Y-%m-%d %H:%M}")

    if len(arquivos_para_deletar) > 10:
        print(f"   ... e mais {len(arquivos_para_deletar) - 10} arquivos")

    print()

    # Confirmar ação
    if dry_run:
        print("🧪 MODO DRY-RUN: Nenhum arquivo foi deletado")
        print(f"💾 Espaço que seria liberado: {formatar_bytes(tamanho_total_deletar)}")
        return

    resposta = input(f"⚠️  Confirma deleção de {len(arquivos_para_deletar)} arquivos? (s/N): ")
    if resposta.lower() not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada")
        return

    # Deletar arquivos
    print("🗑️  Deletando arquivos...")
    deletados = 0
    for item in arquivos_para_deletar:
        try:
            item['caminho'].unlink()
            deletados += 1
        except Exception as e:
            print(f"   ❌ Erro ao deletar {item['caminho']}: {e}")

    print(f"✅ {deletados} arquivos deletados")
    print(f"💾 Espaço liberado: {formatar_bytes(tamanho_total_deletar)}")

    # Limpar pastas vazias
    print("\n🧹 Limpando pastas vazias...")
    pastas_removidas = 0
    for pasta in sorted(cameras_dir.rglob('*'), reverse=True):
        if pasta.is_dir() and not any(pasta.iterdir()):
            try:
                pasta.rmdir()
                pastas_removidas += 1
            except:
                pass

    if pastas_removidas > 0:
        print(f"   ✅ {pastas_removidas} pastas vazias removidas")

    print("\n✨ Limpeza concluída!")

def estatisticas_armazenamento():
    """Mostra estatísticas de uso de armazenamento"""
    cameras_dir = Path("cameras")

    if not cameras_dir.exists():
        print("❌ Pasta 'cameras' não encontrada")
        return

    print("📊 ESTATÍSTICAS DE ARMAZENAMENTO")
    print("=" * 80)

    # Tamanho total
    tamanho_total = calcular_tamanho_diretorio(cameras_dir)
    print(f"💾 Tamanho total: {formatar_bytes(tamanho_total)}")

    # Contar arquivos
    total_arquivos = len(list(cameras_dir.rglob("*.jpg")))
    total_lojas = len([d for d in cameras_dir.iterdir() if d.is_dir()])

    print(f"📸 Total de imagens: {total_arquivos:,}")
    print(f"🏪 Total de lojas: {total_lojas}")
    print(f"📈 Média por loja: {total_arquivos/total_lojas:.1f} imagens")
    print(f"💽 Tamanho médio: {formatar_bytes(tamanho_total/total_arquivos)}/imagem")

    # Análise por idade
    agora = datetime.now()
    contadores = {
        'hoje': 0,
        'ultimos_7_dias': 0,
        'ultimos_30_dias': 0,
        'mais_antigos': 0
    }

    for jpg_file in cameras_dir.rglob("*.jpg"):
        if jpg_file.is_symlink():
            continue

        mtime = datetime.fromtimestamp(jpg_file.stat().st_mtime)
        idade_dias = (agora - mtime).days

        if idade_dias == 0:
            contadores['hoje'] += 1
        if idade_dias <= 7:
            contadores['ultimos_7_dias'] += 1
        if idade_dias <= 30:
            contadores['ultimos_30_dias'] += 1
        else:
            contadores['mais_antigos'] += 1

    print(f"\n📅 Distribuição por idade:")
    print(f"   • Hoje: {contadores['hoje']} imagens")
    print(f"   • Últimos 7 dias: {contadores['ultimos_7_dias']} imagens")
    print(f"   • Últimos 30 dias: {contadores['ultimos_30_dias']} imagens")
    print(f"   • Mais de 30 dias: {contadores['mais_antigos']} imagens")

    # Top 10 lojas com mais arquivos
    print(f"\n🏆 Top 10 lojas com mais imagens:")
    lojas_counts = {}
    for jpg_file in cameras_dir.rglob("*.jpg"):
        loja = jpg_file.parts[1] if len(jpg_file.parts) > 1 else "Unknown"
        lojas_counts[loja] = lojas_counts.get(loja, 0) + 1

    for i, (loja, count) in enumerate(sorted(lojas_counts.items(), key=lambda x: x[1], reverse=True)[:10], 1):
        print(f"   {i:2d}. {loja}: {count} imagens")

    print("=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerenciador de limpeza de imagens antigas")
    parser.add_argument('--dias', type=int, default=7, help='Dias de retenção (padrão: 7)')
    parser.add_argument('--dry-run', action='store_true', help='Simular sem deletar')
    parser.add_argument('--arquivar', action='store_true', help='Arquivar antes de deletar')
    parser.add_argument('--stats', action='store_true', help='Mostrar estatísticas apenas')

    args = parser.parse_args()

    if args.stats:
        estatisticas_armazenamento()
    else:
        limpar_arquivos_antigos(
            dias_retencao=args.dias,
            dry_run=args.dry_run,
            arquivar=args.arquivar
        )

#!/usr/bin/env python3
"""
Gerenciador de Configuração do Sistema de Câmeras
Permite escolher modo de armazenamento e outras opções
"""

import json
import os
from pathlib import Path
from datetime import datetime

CONFIG_FILE = Path(".camera_config.json")

DEFAULT_CONFIG = {
    "storage_mode": "organized",  # snapshot, organized, timestamped
    "retention_days": 7,
    "max_workers": 10,
    "retry_attempts": 3,
    "delay_between_cameras": 0.5,
    "enable_cleanup": True,
    "enable_validation": True,
    "log_level": "INFO",
    "credentials": {
        "username": "",  # Usar variável de ambiente
        "password": ""   # Usar variável de ambiente
    },
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat()
}

STORAGE_MODES = {
    "snapshot": {
        "name": "Snapshot (Sobrescrever)",
        "description": "Mantém apenas a última imagem de cada câmera",
        "pros": [
            "Ocupa mínimo espaço em disco",
            "Simples de gerenciar",
            "Acesso rápido à última imagem"
        ],
        "cons": [
            "Perde todo o histórico",
            "Sem possibilidade de análise temporal",
            "Não detecta mudanças ao longo do tempo"
        ],
        "disk_usage": "~35 MB (345 câmeras × 100 KB)",
        "structure": "cameras/Loja/P1.jpg"
    },
    "organized": {
        "name": "Organizado por Data (Recomendado)",
        "description": "Organiza imagens por ano/mês/dia com symlinks",
        "pros": [
            "Histórico completo e organizado",
            "Fácil buscar por data específica",
            "Symlinks para acesso rápido",
            "Fácil deletar períodos antigos"
        ],
        "cons": [
            "Mais complexo",
            "Requer limpeza periódica"
        ],
        "disk_usage": "~1.2 GB por mês (4 execuções/dia)",
        "structure": "cameras/Loja/2025-12/22/P1_143022.jpg"
    },
    "timestamped": {
        "name": "Timestamp no Nome (Atual)",
        "description": "Adiciona timestamp no nome do arquivo",
        "pros": [
            "Simples (código atual)",
            "Nunca perde dados"
        ],
        "cons": [
            "Desorganizado",
            "Difícil buscar imagem específica",
            "Cresce sem controle"
        ],
        "disk_usage": "~1.2 GB por mês (cresce indefinidamente)",
        "structure": "cameras/Loja/P1_Loja_20251222_143022.jpg"
    }
}

def carregar_config():
    """Carrega configuração do arquivo JSON"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()

def salvar_config(config):
    """Salva configuração no arquivo JSON"""
    config['updated_at'] = datetime.now().isoformat()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✅ Configuração salva em: {CONFIG_FILE.absolute()}")

def exibir_modo_storage(mode_key):
    """Exibe detalhes de um modo de armazenamento"""
    mode = STORAGE_MODES[mode_key]
    print(f"\n{'='*80}")
    print(f"📦 {mode['name']}")
    print(f"{'='*80}")
    print(f"📝 {mode['description']}")
    print(f"\n📁 Estrutura: {mode['structure']}")
    print(f"💾 Uso de disco: {mode['disk_usage']}")

    print(f"\n✅ Vantagens:")
    for pro in mode['pros']:
        print(f"   • {pro}")

    print(f"\n❌ Desvantagens:")
    for con in mode['cons']:
        print(f"   • {con}")
    print(f"{'='*80}")

def menu_interativo():
    """Menu interativo para configuração"""
    config = carregar_config()

    while True:
        print("\n" + "="*80)
        print("⚙️  CONFIGURADOR DO SISTEMA DE CÂMERAS AIVISUAL")
        print("="*80)
        print(f"\n📊 Configuração Atual:")
        print(f"   1. Modo de Armazenamento: {config['storage_mode']} ({STORAGE_MODES[config['storage_mode']]['name']})")
        print(f"   2. Dias de Retenção: {config['retention_days']} dias")
        print(f"   3. Workers Paralelos: {config['max_workers']}")
        print(f"   4. Tentativas de Retry: {config['retry_attempts']}")
        print(f"   5. Delay entre Câmeras: {config['delay_between_cameras']}s")
        print(f"   6. Limpeza Automática: {'Ativada' if config['enable_cleanup'] else 'Desativada'}")
        print(f"   7. Validação de Imagem: {'Ativada' if config['enable_validation'] else 'Desativada'}")
        print(f"   8. Nível de Log: {config['log_level']}")

        print("\n📋 Opções:")
        print("   c - Comparar modos de armazenamento")
        print("   s - Salvar e sair")
        print("   x - Sair sem salvar")
        print("   1-8 - Alterar configuração")

        escolha = input("\n➡️  Escolha uma opção: ").strip().lower()

        if escolha == 's':
            salvar_config(config)
            break
        elif escolha == 'x':
            print("❌ Saindo sem salvar")
            break
        elif escolha == 'c':
            comparar_modos()
        elif escolha == '1':
            config['storage_mode'] = menu_storage_mode()
        elif escolha == '2':
            dias = input(f"Dias de retenção (atual: {config['retention_days']}): ")
            if dias.isdigit():
                config['retention_days'] = int(dias)
        elif escolha == '3':
            workers = input(f"Workers paralelos (atual: {config['max_workers']}, recomendado: 5-20): ")
            if workers.isdigit():
                config['max_workers'] = int(workers)
        elif escolha == '4':
            retry = input(f"Tentativas de retry (atual: {config['retry_attempts']}): ")
            if retry.isdigit():
                config['retry_attempts'] = int(retry)
        elif escolha == '5':
            delay = input(f"Delay em segundos (atual: {config['delay_between_cameras']}): ")
            try:
                config['delay_between_cameras'] = float(delay)
            except:
                pass
        elif escolha == '6':
            config['enable_cleanup'] = not config['enable_cleanup']
        elif escolha == '7':
            config['enable_validation'] = not config['enable_validation']
        elif escolha == '8':
            print("\nNíveis disponíveis: DEBUG, INFO, WARNING, ERROR")
            nivel = input("Escolha: ").upper()
            if nivel in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
                config['log_level'] = nivel

def menu_storage_mode():
    """Menu para escolha de modo de armazenamento"""
    print("\n" + "="*80)
    print("📦 ESCOLHA O MODO DE ARMAZENAMENTO")
    print("="*80)

    modos = list(STORAGE_MODES.keys())
    for i, mode_key in enumerate(modos, 1):
        mode = STORAGE_MODES[mode_key]
        print(f"\n{i}. {mode['name']}")
        print(f"   📝 {mode['description']}")
        print(f"   💾 {mode['disk_usage']}")

    while True:
        escolha = input(f"\nEscolha (1-{len(modos)}) ou 'd' para detalhes: ").strip()

        if escolha == 'd':
            detalhe = input(f"Ver detalhes de qual modo? (1-{len(modos)}): ")
            if detalhe.isdigit() and 1 <= int(detalhe) <= len(modos):
                exibir_modo_storage(modos[int(detalhe)-1])
        elif escolha.isdigit() and 1 <= int(escolha) <= len(modos):
            return modos[int(escolha)-1]

def comparar_modos():
    """Exibe comparação detalhada entre os modos"""
    print("\n" + "="*80)
    print("📊 COMPARAÇÃO DE MODOS DE ARMAZENAMENTO")
    print("="*80)

    for mode_key in STORAGE_MODES.keys():
        exibir_modo_storage(mode_key)
        input("\nPressione Enter para continuar...")

def gerar_recomendacao(uso_previsto):
    """Gera recomendação baseada no uso previsto"""
    recomendacoes = {
        "monitoramento_tempo_real": {
            "storage_mode": "snapshot",
            "retention_days": 0,
            "max_workers": 20,
            "motivo": "Necessita apenas da última imagem, máxima velocidade"
        },
        "auditoria_semanal": {
            "storage_mode": "organized",
            "retention_days": 7,
            "max_workers": 10,
            "motivo": "Histórico organizado de 7 dias, balanceado"
        },
        "analise_mensal": {
            "storage_mode": "organized",
            "retention_days": 30,
            "max_workers": 10,
            "motivo": "Histórico organizado de 30 dias para análises"
        },
        "machine_learning": {
            "storage_mode": "organized",
            "retention_days": 90,
            "max_workers": 10,
            "motivo": "Dataset grande e organizado para treinar modelos"
        }
    }

    print("\n" + "="*80)
    print("💡 RECOMENDAÇÕES POR CASO DE USO")
    print("="*80)

    for i, (uso, rec) in enumerate(recomendacoes.items(), 1):
        print(f"\n{i}. {uso.replace('_', ' ').title()}")
        print(f"   📦 Modo: {STORAGE_MODES[rec['storage_mode']]['name']}")
        print(f"   📅 Retenção: {rec['retention_days']} dias")
        print(f"   ⚡ Workers: {rec['max_workers']}")
        print(f"   💬 Motivo: {rec['motivo']}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == '--compare':
            comparar_modos()
        elif sys.argv[1] == '--recommend':
            gerar_recomendacao(None)
        elif sys.argv[1] == '--show':
            config = carregar_config()
            print(json.dumps(config, indent=2))
    else:
        menu_interativo()

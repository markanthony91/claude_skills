#!/usr/bin/env python3
"""
Script para copiar metadados compartilhados de P1 para P2 e P3 da mesma loja

Campos copiados (dados da LOJA inteira):
- nome_completo (ajustado para P2/P3)
- lugar (Drive_Thru, Salão, etc)
- ip_internet (IP externo da loja)
- versao_sistema (versão do sistema da loja)

Campos NÃO copiados (específicos de cada câmera):
- uuid, ip_local, mac_address, temperatura_cpu, ultima_resposta, area
"""

import json
from pathlib import Path

METADATA_FILE = Path(__file__).parent / "data" / "camera_metadata.json"


def load_metadata():
    """Carrega metadados existentes"""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_metadata(metadata):
    """Salva metadados"""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def extract_store_name(camera_id):
    """
    Extrai nome da loja do ID da câmera
    Ex: "Salvador_Av_ACM_P1" -> "Salvador_Av_ACM"
    """
    # Remove _P1, _P2, _P3 do final
    if camera_id.endswith('_P1') or camera_id.endswith('_P2') or camera_id.endswith('_P3'):
        return camera_id[:-3]
    return camera_id


def get_position(camera_id):
    """
    Extrai posição (P1, P2, P3)
    Ex: "Salvador_Av_ACM_P1" -> "P1"
    """
    if camera_id.endswith('_P1'):
        return 'P1'
    elif camera_id.endswith('_P2'):
        return 'P2'
    elif camera_id.endswith('_P3'):
        return 'P3'
    return None


def copy_p1_to_p2_p3():
    """
    Copia metadados compartilhados de P1 para P2 e P3 da mesma loja
    """
    metadata = load_metadata()

    # Campos que serão copiados (dados da loja)
    SHARED_FIELDS = ['lugar', 'ip_internet', 'versao_sistema']

    # Encontrar todas as câmeras P1
    p1_cameras = {k: v for k, v in metadata.items() if k.endswith('_P1')}

    if not p1_cameras:
        print("⚠️ Nenhuma câmera P1 encontrada nos metadados")
        return

    print(f"\n📋 Encontradas {len(p1_cameras)} câmeras P1")
    print("=" * 70)

    added_count = 0
    updated_count = 0

    for p1_id, p1_data in p1_cameras.items():
        store_name = extract_store_name(p1_id)

        print(f"\n🏪 Loja: {store_name}")

        # Processar P2 e P3
        for position in ['P2', 'P3']:
            camera_id = f"{store_name}_{position}"

            # Preparar dados compartilhados
            shared_data = {}

            # Copiar campos compartilhados
            for field in SHARED_FIELDS:
                if field in p1_data:
                    shared_data[field] = p1_data[field]

            # Adicionar nome completo (ajustado para P2/P3)
            if 'nome_completo' in p1_data:
                nome_completo = p1_data['nome_completo'].replace('_P1', f'_{position}')
                shared_data['nome_completo'] = nome_completo

            # Verificar se já existe
            if camera_id in metadata:
                # Atualizar apenas campos compartilhados (preserva dados únicos)
                for field, value in shared_data.items():
                    metadata[camera_id][field] = value
                print(f"  ✓ {position}: Atualizado ({len(shared_data)} campos)")
                updated_count += 1
            else:
                # Criar novo
                metadata[camera_id] = shared_data
                print(f"  + {position}: Criado ({len(shared_data)} campos)")
                added_count += 1

    # Salvar
    save_metadata(metadata)

    print("\n" + "=" * 70)
    print(f"✅ Concluído!")
    print(f"   📊 {added_count} câmeras adicionadas")
    print(f"   🔄 {updated_count} câmeras atualizadas")
    print(f"   💾 Salvo em: {METADATA_FILE}")


def show_preview():
    """Mostra preview sem salvar"""
    metadata = load_metadata()

    p1_cameras = {k: v for k, v in metadata.items() if k.endswith('_P1')}

    if not p1_cameras:
        print("⚠️ Nenhuma câmera P1 encontrada")
        return

    print("\n🔍 PREVIEW - Metadados que serão copiados:")
    print("=" * 70)

    for p1_id, p1_data in p1_cameras.items():
        store_name = extract_store_name(p1_id)

        print(f"\n🏪 {store_name}")
        print(f"   P1 (origem): {p1_id}")

        # Campos compartilhados
        shared = []
        for field in ['lugar', 'ip_internet', 'versao_sistema']:
            if field in p1_data:
                shared.append(f"{field}={p1_data[field]}")

        if shared:
            print(f"   📦 Dados compartilhados: {', '.join(shared)}")

        print(f"   → P2: {store_name}_P2")
        print(f"   → P3: {store_name}_P3")


def main():
    """Menu principal"""
    print("\n" + "=" * 70)
    print("📋 COPIAR METADADOS P1 → P2/P3")
    print("=" * 70)
    print("\nEste script copia dados COMPARTILHADOS de P1 para P2 e P3:")
    print("  ✓ lugar (Drive_Thru, Salão, etc)")
    print("  ✓ ip_internet (IP externo da loja)")
    print("  ✓ versao_sistema")
    print("\nNÃO copia dados ÚNICOS de cada câmera:")
    print("  ✗ uuid, ip_local, mac_address, temperatura_cpu, area")
    print("\n" + "=" * 70)

    print("\n1. Ver preview (não salva)")
    print("2. Executar (copiar e salvar)")
    print("0. Cancelar")

    choice = input("\nEscolha uma opção: ").strip()

    if choice == '1':
        show_preview()
    elif choice == '2':
        print("\n⚠️  Isso irá modificar o arquivo de metadados.")
        confirm = input("Confirma? (s/N): ").strip().lower()
        if confirm in ['s', 'y', 'sim', 'yes']:
            copy_p1_to_p2_p3()
        else:
            print("❌ Cancelado")
    else:
        print("❌ Cancelado")


if __name__ == "__main__":
    main()

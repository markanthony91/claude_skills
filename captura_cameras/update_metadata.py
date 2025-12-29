#!/usr/bin/env python3
"""
Script Auxiliar para Atualizar Metadados das Câmeras
Facilita a adição de informações extras (Lugar, Área, UUID, IPs, etc.)
"""

import json
from pathlib import Path

# Caminho do arquivo de metadados
METADATA_FILE = Path(__file__).parent / "data" / "camera_metadata.json"


def load_metadata():
    """Carrega metadados existentes"""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_metadata(metadata):
    """Salva metadados no arquivo JSON"""
    METADATA_FILE.parent.mkdir(exist_ok=True)
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"✓ Metadados salvos em: {METADATA_FILE}")


def add_camera_metadata(camera_id, metadata_dict):
    """
    Adiciona ou atualiza metadados de uma câmera

    Args:
        camera_id: ID da câmera (ex: "Salvador_Av_ACM_P1")
        metadata_dict: Dicionário com os metadados

    Exemplo:
        add_camera_metadata("Salvador_Av_ACM_P1", {
            "nome_completo": "BK - Salvador Av ACM_P1",
            "lugar": "Drive_Thru",
            "area": "Pedido",
            "ip_local": "172.18.0.4",
            "uuid": "1161727969480FABKHMVBAXZ"
        })
    """
    metadata = load_metadata()
    metadata[camera_id] = metadata_dict
    save_metadata(metadata)
    print(f"✓ Metadados adicionados para: {camera_id}")


def remove_camera_metadata(camera_id):
    """Remove metadados de uma câmera"""
    metadata = load_metadata()
    if camera_id in metadata:
        del metadata[camera_id]
        save_metadata(metadata)
        print(f"✓ Metadados removidos para: {camera_id}")
    else:
        print(f"⚠ Câmera não encontrada: {camera_id}")


def list_all_metadata():
    """Lista todos os metadados cadastrados"""
    metadata = load_metadata()

    if not metadata:
        print("⚠ Nenhum metadado cadastrado")
        return

    print(f"\n📋 Total de câmeras com metadados: {len(metadata)}")
    print("=" * 70)

    for camera_id, data in metadata.items():
        print(f"\n🎥 {camera_id}")
        for key, value in data.items():
            print(f"   {key}: {value}")


def import_from_html_example():
    """
    Exemplo de como extrair metadados do HTML da AIVisual
    Esta função mostra a estrutura que você deve seguir
    """
    # Exemplo de extração (adapte conforme necessário)
    example_data = {
        "Salvador_Av_ACM_P1": {
            "nome_completo": "BK - Salvador Av ACM_P1",
            "lugar": "Drive_Thru",
            "area": "Pedido",
            "ultima_resposta": "2025-12-22 07:09:54",
            "ip_local": "172.18.0.4",
            "ip_internet": "187.29.40.134",
            "mac_address": "02:42:ac:12:00:04",
            "temperatura_cpu": "0,00",
            "uuid": "1161727969480FABKHMVBAXZ",
            "versao_sistema": "DTRHU-3.7.1"
        }
    }

    print("📝 Exemplo de estrutura de metadados:")
    print(json.dumps(example_data, indent=2, ensure_ascii=False))

    return example_data


def bulk_import(metadata_dict):
    """
    Importa múltiplos metadados de uma vez

    Args:
        metadata_dict: Dicionário completo com todos os metadados
    """
    metadata = load_metadata()
    metadata.update(metadata_dict)
    save_metadata(metadata)
    print(f"✓ {len(metadata_dict)} câmeras importadas")


# ==================== Menu Interativo ====================

def show_menu():
    """Mostra menu interativo"""
    print("\n" + "=" * 70)
    print("🎥 GERENCIADOR DE METADADOS DE CÂMERAS")
    print("=" * 70)
    print("\n1. Listar todos os metadados")
    print("2. Adicionar/Atualizar metadados de uma câmera")
    print("3. Remover metadados de uma câmera")
    print("4. Ver exemplo de estrutura")
    print("5. Importação em massa (JSON)")
    print("0. Sair")
    print("\n" + "=" * 70)


def interactive_add():
    """Adiciona metadados interativamente"""
    print("\n📝 ADICIONAR METADADOS")
    print("=" * 70)

    camera_id = input("ID da câmera (ex: Salvador_Av_ACM_P1): ").strip()

    if not camera_id:
        print("❌ ID inválido")
        return

    print("\nInforme os dados (deixe em branco para pular):")

    metadata_dict = {}

    fields = [
        ("nome_completo", "Nome completo"),
        ("lugar", "Lugar (Drive_Thru, Salão, etc)"),
        ("area", "Área (Pedido, Caixa, etc)"),
        ("ultima_resposta", "Última resposta"),
        ("ip_local", "IP local"),
        ("ip_internet", "IP internet"),
        ("mac_address", "MAC address"),
        ("temperatura_cpu", "Temperatura CPU"),
        ("uuid", "UUID"),
        ("versao_sistema", "Versão do sistema")
    ]

    for key, label in fields:
        value = input(f"{label}: ").strip()
        if value:
            metadata_dict[key] = value

    if metadata_dict:
        add_camera_metadata(camera_id, metadata_dict)
    else:
        print("⚠ Nenhum dado fornecido")


def interactive_bulk_import():
    """Importação em massa via JSON"""
    print("\n📦 IMPORTAÇÃO EM MASSA")
    print("=" * 70)
    print("\nCole o JSON completo (Ctrl+D quando terminar):")

    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    json_str = '\n'.join(lines)

    try:
        data = json.loads(json_str)
        bulk_import(data)
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao parsear JSON: {e}")


def main():
    """Função principal do menu interativo"""
    while True:
        show_menu()
        choice = input("Escolha uma opção: ").strip()

        if choice == '0':
            print("\n👋 Até logo!")
            break
        elif choice == '1':
            list_all_metadata()
        elif choice == '2':
            interactive_add()
        elif choice == '3':
            camera_id = input("ID da câmera para remover: ").strip()
            if camera_id:
                remove_camera_metadata(camera_id)
        elif choice == '4':
            import_from_html_example()
        elif choice == '5':
            interactive_bulk_import()
        else:
            print("❌ Opção inválida")

        input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    import sys

    # Se executado sem argumentos, mostra menu interativo
    if len(sys.argv) == 1:
        main()
    else:
        # Permite uso via linha de comando
        print("Uso via linha de comando:")
        print("  python3 update_metadata.py              # Menu interativo")
        print("\nUso via importação:")
        print("  from update_metadata import add_camera_metadata")
        print("  add_camera_metadata('Loja_P1', {...})")

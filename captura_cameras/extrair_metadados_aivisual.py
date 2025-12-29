#!/usr/bin/env python3
"""
Script para extrair metadados das câmeras do site AIVisual
Extrai informações de TODAS as câmeras P1 e aplica para P2 e P3
"""

import sys
import time
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

# Configurações
BASE_URL = "https://dashboard.aivisual.ai"
USERNAME = "bk@aiknow.ai"
PASSWORD = "nR}CMryIT,8/5!3i9"
METADATA_FILE = Path(__file__).parent / "data" / "camera_metadata.json"


def setup_driver():
    """Configura o Chrome WebDriver"""
    print("🔧 Configurando Chrome WebDriver...")

    chromedriver_autoinstaller.install()

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def login(driver):
    """Faz login no dashboard AIVisual"""
    print(f"\n🔐 Fazendo login em {BASE_URL}...")

    driver.get(f"{BASE_URL}/login")
    time.sleep(2)

    try:
        # Tentar encontrar campos de login
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")

        username_field.send_keys(USERNAME)
        password_field.send_keys(PASSWORD)

        # Submeter formulário
        password_field.submit()
        time.sleep(3)

        print("✅ Login realizado com sucesso")
        return True

    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False


def extract_camera_metadata(driver, card_element):
    """
    Extrai metadados de um card de câmera

    Estrutura HTML esperada:
    <div class="card-body">
      <h4>Nome: <b>BK - Salvador Av ACM_P1</b></h4>
      <h5>Lugar: <b>Drive_Thru</b></h5>
      <h5>Área: <b>Pedido</b></h5>
      <small id="UUID">
        Última resposta: <b class="response">...</b><br>
        IP da rede local: <b class="ethernet">...</b><br>
        IP de internet: <b class="internet">...</b><br>
        Endereço MAC: <b class="mac">...</b><br>
        Temperatura da CPU: <b class="cpu">...</b><br>
        UUID: <b>...</b><br>
        Versão do Sistema: <b class="version">...</b>
      </small>
    </div>
    """
    metadata = {}

    try:
        # Nome completo
        try:
            nome_element = card_element.find_element(By.XPATH, ".//h4[contains(text(), 'Nome:')]/b")
            metadata['nome_completo'] = nome_element.text.strip()
        except:
            pass

        # Lugar
        try:
            lugar_element = card_element.find_element(By.XPATH, ".//h5[contains(text(), 'Lugar:')]/b")
            metadata['lugar'] = lugar_element.text.strip()
        except:
            pass

        # Área
        try:
            area_element = card_element.find_element(By.XPATH, ".//h5[contains(text(), 'Área:')]/b")
            metadata['area'] = area_element.text.strip()
        except:
            pass

        # Informações do <small>
        try:
            # Última resposta
            response_element = card_element.find_element(By.CSS_SELECTOR, "b.response")
            metadata['ultima_resposta'] = response_element.text.strip()
        except:
            pass

        try:
            # IP local (ethernet)
            ethernet_element = card_element.find_element(By.CSS_SELECTOR, "b.ethernet")
            metadata['ip_local'] = ethernet_element.text.strip()
        except:
            pass

        try:
            # IP internet
            internet_element = card_element.find_element(By.CSS_SELECTOR, "b.internet")
            metadata['ip_internet'] = internet_element.text.strip()
        except:
            pass

        try:
            # MAC address
            mac_element = card_element.find_element(By.CSS_SELECTOR, "b.mac")
            metadata['mac_address'] = mac_element.text.strip()
        except:
            pass

        try:
            # Temperatura CPU
            cpu_element = card_element.find_element(By.CSS_SELECTOR, "b.cpu")
            metadata['temperatura_cpu'] = cpu_element.text.strip()
        except:
            pass

        try:
            # Versão do sistema
            version_element = card_element.find_element(By.CSS_SELECTOR, "b.version")
            metadata['versao_sistema'] = version_element.text.strip()
        except:
            pass

        try:
            # UUID (do ID do elemento <small>)
            small_element = card_element.find_element(By.TAG_NAME, "small")
            uuid = small_element.get_attribute("id")
            if uuid:
                metadata['uuid'] = uuid.strip()
        except:
            pass

    except Exception as e:
        print(f"⚠️ Erro ao extrair metadados: {e}")

    return metadata


def extract_camera_id_from_name(nome_completo):
    """
    Converte nome completo em ID da câmera
    Ex: "BK - Salvador Av ACM_P1" -> "Salvador_Av_ACM_P1"
    """
    # Remove "BK - " do início
    nome_limpo = nome_completo.replace("BK - ", "").strip()

    # Substitui espaços por underscores
    camera_id = nome_limpo.replace(" ", "_").replace("-", "_")

    # Remove caracteres especiais
    camera_id = "".join(c for c in camera_id if c.isalnum() or c == "_")

    return camera_id


def extract_all_metadata(driver):
    """Extrai metadados de todas as câmeras"""
    print("\n📡 Extraindo metadados de todas as câmeras...")

    all_metadata = {}

    try:
        # Navegar para a página de câmeras
        # Ajuste a URL conforme necessário
        driver.get(f"{BASE_URL}/cameras")
        time.sleep(3)

        # Encontrar todos os cards de câmeras
        cards = driver.find_elements(By.CLASS_NAME, "card-body")

        print(f"✓ Encontrados {len(cards)} cards de câmeras")

        for i, card in enumerate(cards, 1):
            print(f"\n🎥 Processando câmera {i}/{len(cards)}...")

            metadata = extract_camera_metadata(driver, card)

            if metadata and 'nome_completo' in metadata:
                camera_id = extract_camera_id_from_name(metadata['nome_completo'])

                # Verificar se é P1, P2 ou P3
                if any(camera_id.endswith(f'_P{i}') for i in [1, 2, 3]):
                    all_metadata[camera_id] = metadata
                    print(f"  ✓ {camera_id}")
                    print(f"    Campos extraídos: {len(metadata)}")
                else:
                    print(f"  ⚠️ Nome não corresponde ao padrão: {camera_id}")
            else:
                print(f"  ⚠️ Metadados incompletos ou sem nome")

            time.sleep(0.5)  # Pequeno delay entre cards

    except Exception as e:
        print(f"❌ Erro ao extrair metadados: {e}")

    return all_metadata


def copy_p1_to_p2_p3(metadata):
    """
    Copia dados compartilhados de P1 para P2 e P3 da mesma loja
    """
    print("\n📦 Copiando dados compartilhados para P2 e P3...")

    # Campos que serão copiados (dados da loja)
    SHARED_FIELDS = ['lugar', 'ip_internet', 'versao_sistema']

    # Encontrar todas as P1
    p1_cameras = {k: v for k, v in metadata.items() if k.endswith('_P1')}

    added_count = 0

    for p1_id, p1_data in p1_cameras.items():
        store_name = p1_id[:-3]  # Remove _P1

        # Criar P2 e P3
        for position in ['P2', 'P3']:
            camera_id = f"{store_name}_{position}"

            # Preparar dados compartilhados
            shared_data = {}

            # Copiar campos compartilhados
            for field in SHARED_FIELDS:
                if field in p1_data:
                    shared_data[field] = p1_data[field]

            # Adicionar nome completo (ajustado)
            if 'nome_completo' in p1_data:
                nome_completo = p1_data['nome_completo'].replace('_P1', f'_{position}')
                shared_data['nome_completo'] = nome_completo

            # Adicionar ao metadata
            if camera_id not in metadata:
                metadata[camera_id] = shared_data
                added_count += 1
                print(f"  + {camera_id}")

    print(f"✓ {added_count} câmeras P2/P3 adicionadas")

    return metadata


def save_metadata(metadata):
    """Salva metadados no arquivo JSON"""
    METADATA_FILE.parent.mkdir(exist_ok=True)

    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Metadados salvos em: {METADATA_FILE}")
    print(f"📊 Total de câmeras: {len(metadata)}")


def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print("🎥 EXTRATOR DE METADADOS AIVISUAL")
    print("=" * 70)

    print("\nEste script irá:")
    print("  1. Fazer login no dashboard AIVisual")
    print("  2. Extrair metadados de todas as câmeras P1")
    print("  3. Copiar dados compartilhados para P2 e P3")
    print("  4. Salvar tudo em camera_metadata.json")

    print("\n" + "=" * 70)

    confirm = input("\nDeseja continuar? (s/N): ").strip().lower()

    if confirm not in ['s', 'y', 'sim', 'yes']:
        print("❌ Cancelado")
        return

    driver = None

    try:
        # Setup
        driver = setup_driver()

        # Login
        if not login(driver):
            print("❌ Falha no login. Verifique as credenciais.")
            return

        # Extrair metadados
        metadata = extract_all_metadata(driver)

        if not metadata:
            print("⚠️ Nenhum metadado extraído")
            return

        print(f"\n✅ {len(metadata)} câmeras extraídas")

        # Copiar P1 para P2/P3
        metadata = copy_p1_to_p2_p3(metadata)

        # Salvar
        save_metadata(metadata)

        print("\n" + "=" * 70)
        print("✅ CONCLUÍDO COM SUCESSO!")
        print("=" * 70)

        print("\n📋 Próximos passos:")
        print("  1. Reinicie o dashboard: ./start_dashboard.sh")
        print("  2. Limpe o cache do navegador: Ctrl+Shift+R")
        print("  3. Verifique os metadados nos cards das câmeras")

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            print("\n🔒 Fechando navegador...")
            driver.quit()


if __name__ == "__main__":
    main()

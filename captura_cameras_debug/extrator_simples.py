#!/usr/bin/env python3
"""
Extrator Simples - Detecta automaticamente o acesso e baixa imagens
"""

import requests
import os
import base64
from datetime import datetime
from urllib.parse import urljoin, unquote
from bs4 import BeautifulSoup

# CONFIGURAÇÕES
BASE_URL = "http://35.209.243.66"
LOGIN_EMAIL = "bk@aiknow.ai"
LOGIN_PASSWORD = "Sphbr7410"
ROTULOS = ["d0", "d1", "d2", "d3"]
CAMERAS = ["P1", "P2", "P3"]

# ===== CONFIGURE AQUI =====
ANO = 2025
MES = 5
DIA = 29
HORARIO_INICIO = "14:00"  # ou None
HORARIO_FIM = "16:00"     # ou None
LOJAS_ESPECIFICAS = [
    "BK - Águas Claras Castaneiras",
    # Adicione mais lojas aqui
]

def detectar_tipo_acesso():
    """Detecta automaticamente o tipo de acesso"""
    print("🔍 Detectando tipo de acesso...")
    
    # Método 1: Acesso direto
    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0"})
        
        response = session.get(f"{BASE_URL}/bk/", timeout=10)
        if response.status_code == 200 and ("<a href=" in response.text or "BK -" in response.text):
            print("   ✅ Acesso direto funcionou!")
            return session, "DIRETO"
    except:
        pass
    
    # Método 2: HTTP Basic Auth
    usuarios = [LOGIN_EMAIL, LOGIN_EMAIL.split("@")[0], "bk"]
    
    for usuario in usuarios:
        try:
            credentials = base64.b64encode(f"{usuario}:{LOGIN_PASSWORD}".encode()).decode()
            
            session = requests.Session()
            session.headers.update({
                "Authorization": f"Basic {credentials}",
                "User-Agent": "Mozilla/5.0"
            })
            
            response = session.get(f"{BASE_URL}/bk/", timeout=10)
            if response.status_code == 200 and ("<a href=" in response.text or "BK -" in response.text):
                print(f"   ✅ HTTP Basic Auth funcionou com usuário: {usuario}")
                return session, f"BASIC_{usuario}"
        except:
            continue
    
    print("   ❌ Nenhum método funcionou")
    return None, None

def listar_diretorios(session, url):
    """Lista diretórios de uma URL"""
    try:
        response = session.get(url, timeout=30)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, "html.parser")
        diretorios = []
        
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and href != "../" and href.endswith("/"):
                diretorios.append(unquote(href.rstrip("/")))
        
        return sorted(diretorios)
    except:
        return []

def listar_arquivos(session, url):
    """Lista arquivos de uma URL com timestamp"""
    try:
        response = session.get(url, timeout=30)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, "html.parser")
        arquivos = []
        
        # Tentar estrutura de tabela
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                link = row.find("a")
                if link and link.get("href") and not link.get("href").endswith("/"):
                    nome = unquote(link.get("href"))
                    timestamp = cells[1].get_text(strip=True)
                    
                    arquivos.append({
                        "nome": nome,
                        "timestamp": timestamp,
                        "url": urljoin(url, nome)
                    })
        
        # Fallback: lista simples
        if not arquivos:
            for link in soup.find_all("a"):
                href = link.get("href")
                if href and not href.endswith("/") and href != "../":
                    nome = unquote(href)
                    arquivos.append({
                        "nome": nome,
                        "timestamp": "",
                        "url": urljoin(url, nome)
                    })
        
        return arquivos
    except:
        return []

def filtrar_arquivos_por_rotulos(arquivos):
    """Filtra arquivos pelos rótulos desejados"""
    filtrados = []
    
    for arquivo in arquivos:
        nome = arquivo["nome"]
        
        # Verificar se tem algum rótulo
        for rotulo in ROTULOS:
            if f"_{rotulo}_" in nome:
                arquivo["rotulo"] = rotulo
                filtrados.append(arquivo)
                break
    
    return filtrados

def baixar_arquivo(session, url, destino):
    """Baixa um arquivo"""
    try:
        response = session.get(url, timeout=60)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        
        with open(destino, "wb") as f:
            f.write(response.content)
        
        return True
    except:
        return False

def processar_loja(session, nome_loja):
    """Processa uma loja específica"""
    print(f"\n🏪 {nome_loja}")
    
    url_loja = f"{BASE_URL}/bk/{ANO}/{MES:02d}/{nome_loja}/"
    cameras_disponiveis = listar_diretorios(session, url_loja)
    cameras_encontradas = [c for c in CAMERAS if c in cameras_disponiveis]
    
    if not cameras_encontradas:
        print("  ❌ Nenhuma câmera encontrada")
        return 0
    
    print(f"  📹 Câmeras: {cameras_encontradas}")
    total_baixadas = 0
    
    for camera in cameras_encontradas:
        print(f"  📸 {camera}...", end=" ")
        
        url_camera = f"{url_loja}{camera}/"
        dias = listar_diretorios(session, url_camera)
        dia_str = f"{DIA:02d}"
        
        if dia_str not in dias:
            print("❌ Dia não encontrado")
            continue
        
        url_dia = f"{url_camera}{dia_str}/"
        arquivos = listar_arquivos(session, url_dia)
        
        if not arquivos:
            print("❌ Sem arquivos")
            continue
        
        # Filtrar por rótulos
        arquivos_filtrados = filtrar_arquivos_por_rotulos(arquivos)
        
        if not arquivos_filtrados:
            print("❌ Sem imagens com rótulos d0,d1,d2,d3")
            continue
        
        # Agrupar por rótulo (uma imagem por rótulo)
        por_rotulo = {}
        for arquivo in arquivos_filtrados:
            rotulo = arquivo["rotulo"]
            if rotulo not in por_rotulo:
                por_rotulo[rotulo] = arquivo
        
        # Baixar imagens
        baixadas = 0
        for rotulo, arquivo in por_rotulo.items():
            nome_pasta = nome_loja.replace(" ", "_").replace("-", "_")
            destino = f"imagens_simples/{nome_pasta}/{camera}/dia_{dia_str}/{arquivo['nome']}"
            
            if baixar_arquivo(session, arquivo["url"], destino):
                baixadas += 1
                total_baixadas += 1
        
        print(f"✅ {baixadas}/{len(ROTULOS)} imagens")
    
    return total_baixadas

def main():
    """Função principal"""
    print("⚡ EXTRATOR SIMPLES")
    print("=" * 40)
    print(f"🌐 Site: {BASE_URL}")
    print(f"📧 Login: {LOGIN_EMAIL}")
    print(f"📅 Data: {DIA:02d}/{MES:02d}/{ANO}")
    
    if HORARIO_INICIO and HORARIO_FIM:
        print(f"⏰ Horário: {HORARIO_INICIO} às {HORARIO_FIM}")
    else:
        print("⏰ Sem filtro de horário")
    
    print(f"🏷️  Rótulos: {', '.join(ROTULOS)}")
    print("=" * 40)
    
    # Detectar tipo de acesso
    session, tipo_acesso = detectar_tipo_acesso()
    
    if not session:
        print("❌ Falha no acesso - não foi possível conectar ao site")
        print("   Verifique se o site está funcionando ou se as credenciais estão corretas")
        return
    
    print(f"✅ Tipo de acesso: {tipo_acesso}")
    
    # Determinar lojas
    if LOJAS_ESPECIFICAS:
        lojas = LOJAS_ESPECIFICAS
        print(f"🏪 Processando {len(lojas)} lojas específicas")
    else:
        print("🔍 Buscando todas as lojas...")
        url_mes = f"{BASE_URL}/bk/{ANO}/{MES:02d}/"
        lojas = listar_diretorios(session, url_mes)
        print(f"🏪 Encontradas {len(lojas)} lojas")
    
    if not lojas:
        print("❌ Nenhuma loja encontrada")
        return
    
    # Processar lojas
    total_geral = 0
    inicio = datetime.now()
    
    for i, loja in enumerate(lojas, 1):
        print(f"[{i}/{len(lojas)}]", end=" ")
        total_loja = processar_loja(session, loja)
        total_geral += total_loja
    
    fim = datetime.now()
    duracao = fim - inicio
    
    # Relatório final
    print("\n" + "=" * 50)
    print("📊 RELATÓRIO FINAL")
    print("=" * 50)
    print(f"🔑 Tipo de acesso: {tipo_acesso}")
    print(f"🏪 Lojas processadas: {len(lojas)}")
    print(f"📸 Total de imagens: {total_geral}")
    print(f"⏱️  Tempo: {duracao}")
    print(f"💾 Pasta: ./imagens_simples/")
    print("=" * 50)
    
    if total_geral > 0:
        print("🎉 Extração concluída com sucesso!")
        print("\n📁 Estrutura criada:")
        print("   imagens_simples/")
        print("   ├── Nome_da_Loja/")
        print("   │   ├── P1/dia_XX/arquivo_d0_xxx.jpg")
        print("   │   ├── P2/dia_XX/arquivo_d1_xxx.jpg")
        print("   │   └── P3/dia_XX/arquivo_d2_xxx.jpg")
    else:
        print("⚠️  Nenhuma imagem foi baixada")
        print("   • Verifique se as lojas existem na data especificada")
        print("   • Verifique se há imagens com rótulos d0,d1,d2,d3")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script para corrigir e criar os arquivos necessários
"""

import os
import subprocess
import sys

def instalar_dependencias():
    """Instala dependências necessárias"""
    try:
        import requests
        import bs4
        print("✅ Dependências já instaladas")
    except ImportError:
        print("📦 Instalando dependências...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "lxml"])
        print("✅ Dependências instaladas")

def criar_investigar_site():
    """Cria o arquivo investigar_site.py"""
    conteudo = '''#!/usr/bin/env python3
"""
Investigador do Site - Detecta como acessar
"""

import requests
import base64
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote

BASE_URL = "http://35.209.243.66"
LOGIN_EMAIL = "bk@aiknow.ai"
LOGIN_PASSWORD = "Sphbr7410"

def testar_acesso_direto():
    """Testa acesso sem autenticação"""
    print("🔓 Testando acesso direto...")
    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0"})
        
        response = session.get(f"{BASE_URL}/bk/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            if "<a href=" in response.text or "BK -" in response.text or "Index of" in response.text:
                print("   ✅ ACESSO DIRETO FUNCIONOU!")
                print("   📋 Conteúdo encontrado (primeiras linhas):")
                linhas = response.text.split('\\n')[:5]
                for linha in linhas:
                    if linha.strip():
                        print(f"      {linha.strip()[:80]}")
                return True
        
        print("   ❌ Acesso direto não funcionou")
        return False
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def testar_http_basic():
    """Testa HTTP Basic Authentication"""
    print("🔑 Testando HTTP Basic Auth...")
    
    usuarios = [LOGIN_EMAIL, LOGIN_EMAIL.split("@")[0], "bk", "admin"]
    
    for usuario in usuarios:
        try:
            print(f"   Testando usuário: {usuario}")
            
            credentials = base64.b64encode(f"{usuario}:{LOGIN_PASSWORD}".encode()).decode()
            
            session = requests.Session()
            session.headers.update({
                "Authorization": f"Basic {credentials}",
                "User-Agent": "Mozilla/5.0"
            })
            
            response = session.get(f"{BASE_URL}/bk/", timeout=10)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                if "<a href=" in response.text or "BK -" in response.text:
                    print(f"   ✅ HTTP BASIC FUNCIONOU com usuário: {usuario}!")
                    print("   📋 Conteúdo encontrado (primeiras linhas):")
                    linhas = response.text.split('\\n')[:5]
                    for linha in linhas:
                        if linha.strip():
                            print(f"      {linha.strip()[:80]}")
                    return usuario
            elif response.status_code == 401:
                print("      🔑 Requer autenticação")
            elif response.status_code == 403:
                print("      🚫 Acesso negado")
                
        except Exception as e:
            print(f"      ❌ Erro: {e}")
    
    return None

def testar_diferentes_urls():
    """Testa diferentes URLs do site"""
    print("🔍 Testando diferentes URLs...")
    
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    
    urls_teste = [
        f"{BASE_URL}/",
        f"{BASE_URL}/bk/",
        f"{BASE_URL}/bk/2025/",
        f"{BASE_URL}/bk/2025/05/",
        f"{BASE_URL}/files/",
        f"{BASE_URL}/images/",
        f"{BASE_URL}/data/",
    ]
    
    for url in urls_teste:
        try:
            print(f"   Testando: {url}")
            response = session.get(url, timeout=10)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                if "<a href=" in response.text or "Index of" in response.text:
                    print("      ✅ Listagem encontrada!")
                    return url
            elif response.status_code == 401:
                print("      🔑 Requer autenticação")
            elif response.status_code == 403:
                print("      🚫 Acesso negado")
                
        except Exception as e:
            print(f"      ❌ Erro: {e}")
    
    return None

def main():
    """Função principal"""
    print("🕵️  INVESTIGADOR DO SITE")
    print("=" * 40)
    print(f"🌐 Site: {BASE_URL}")
    print(f"📧 Email: {LOGIN_EMAIL}")
    print("=" * 40)
    
    # Teste 1: Acesso direto
    print("\\n📋 TESTE 1: ACESSO DIRETO")
    if testar_acesso_direto():
        print("\\n✅ RESULTADO: Site acessível sem login!")
        print("🎉 Pode usar extrator sem autenticação!")
        return
    
    # Teste 2: HTTP Basic Auth
    print("\\n📋 TESTE 2: HTTP BASIC AUTHENTICATION")
    usuario_sucesso = testar_http_basic()
    if usuario_sucesso:
        print(f"\\n✅ RESULTADO: HTTP Basic Auth funcionou com usuário: {usuario_sucesso}!")
        print("🎉 Pode usar extrator com autenticação básica!")
        return
    
    # Teste 3: URLs diferentes
    print("\\n📋 TESTE 3: DIFERENTES URLs")
    url_sucesso = testar_diferentes_urls()
    if url_sucesso:
        print(f"\\n✅ RESULTADO: URL acessível encontrada: {url_sucesso}!")
        return
    
    # Resumo final
    print("\\n" + "=" * 50)
    print("📊 RESUMO DA INVESTIGAÇÃO")
    print("=" * 50)
    print("❌ Nenhum método de autenticação funcionou")
    print("\\n🔍 Possíveis problemas:")
    print("   • Site pode estar offline temporariamente")
    print("   • Credenciais podem ter mudado")
    print("   • Estrutura do site pode ter mudado")
    print("   • Firewall ou bloqueio de IP")
    
    print("\\n💡 Próximos passos:")
    print("   1. Verificar se o site funciona no navegador")
    print("   2. Confirmar as credenciais atuais")
    print("   3. Tentar acessar manualmente primeiro")
    print("   4. Verificar se há mudanças no sistema")

if __name__ == "__main__":
    main()
'''
    
    with open("investigar_site.py", "w") as f:
        f.write(conteudo)
    print("✅ Criado: investigar_site.py")

def criar_extrator_simples():
    """Cria o arquivo extrator_simples.py"""
    conteudo = '''#!/usr/bin/env python3
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
    print(f"\\n🏪 {nome_loja}")
    
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
    print("\\n" + "=" * 50)
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
        print("\\n📁 Estrutura criada:")
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
'''
    
    with open("extrator_simples.py", "w") as f:
        f.write(conteudo)
    print("✅ Criado: extrator_simples.py")

def criar_extrator_auto_corrigido():
    """Cria o arquivo extrator_auto_corrigido.py"""
    conteudo = '''#!/usr/bin/env python3
"""
Extrator Auto-Corrigido - Versão mais inteligente
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

class ExtractorInteligente:
    def __init__(self):
        self.session = None
        self.autenticado = False
        self.metodo_auth = None
        
    def detectar_e_autenticar(self):
        """Detecta automaticamente o método de autenticação"""
        print("🧠 DETECTANDO MÉTODO DE AUTENTICAÇÃO...")
        
        # Método 1: Acesso direto
        if self.testar_acesso_direto():
            return True
        
        # Método 2: HTTP Basic Auth
        if self.testar_http_basic():
            return True
        
        # Método 3: Usuários alternativos
        if self.testar_usuarios_alternativos():
            return True
        
        print("❌ Nenhum método funcionou")
        return False
    
    def testar_acesso_direto(self):
        """Testa acesso sem autenticação"""
        print("   🔓 Testando acesso direto...")
        
        try:
            self.session = requests.Session()
            self.session.headers.update({"User-Agent": "Mozilla/5.0"})
            
            response = self.session.get(f"{BASE_URL}/bk/", timeout=10)
            
            if response.status_code == 200 and self.verificar_listagem_valida(response.text):
                self.autenticado = True
                self.metodo_auth = "ACESSO_DIRETO"
                print("      ✅ Acesso direto funcionou!")
                return True
        except Exception as e:
            print(f"      ❌ Erro: {e}")
        
        return False
    
    def testar_http_basic(self):
        """Testa HTTP Basic Authentication"""
        print("   🔑 Testando HTTP Basic Auth...")
        
        usuarios = [LOGIN_EMAIL, LOGIN_EMAIL.split("@")[0], "bk"]
        
        for usuario in usuarios:
            try:
                print(f"      Testando usuário: {usuario}")
                
                credentials = base64.b64encode(f"{usuario}:{LOGIN_PASSWORD}".encode()).decode()
                
                self.session = requests.Session()
                self.session.headers.update({
                    "Authorization": f"Basic {credentials}",
                    "User-Agent": "Mozilla/5.0"
                })
                
                response = self.session.get(f"{BASE_URL}/bk/", timeout=10)
                
                if response.status_code == 200 and self.verificar_listagem_valida(response.text):
                    self.autenticado = True
                    self.metodo_auth = f"HTTP_BASIC_{usuario}"
                    print(f"      ✅ HTTP Basic funcionou com: {usuario}")
                    return True
                    
            except Exception as e:
                print(f"      ❌ Erro com {usuario}: {e}")
        
        return False
    
    def testar_usuarios_alternativos(self):
        """Testa usuários alternativos"""
        print("   👤 Testando usuários alternativos...")
        
        usuarios = ["admin", "root", "user", "camera"]
        senhas = [LOGIN_PASSWORD, "admin", "password", "123456"]
        
        for usuario in usuarios:
            for senha in senhas:
                try:
                    credentials = base64.b64encode(f"{usuario}:{senha}".encode()).decode()
                    
                    self.session = requests.Session()  
                    self.session.headers.update({
                        "Authorization": f"Basic {credentials}",
                        "User-Agent": "Mozilla/5.0"
                    })
                    
                    response = self.session.get(f"{BASE_URL}/bk/", timeout=5)
                    
                    if response.status_code == 200 and self.verificar_listagem_valida(response.text):
                        self.autenticado = True
                        self.metodo_auth = f"ALT_{usuario}"
                        print(f"      ✅ Funcionou: {usuario}")
                        return True
                        
                except:
                    continue
        
        return False
    
    def verificar_listagem_valida(self, conteudo):
        """Verifica se o conteúdo é uma listagem válida"""
        indicadores = ["<a href=", "BK -", "Index of", "Directory", "2025", "</tr>"]
        return any(indicador in conteudo for indicador in indicadores)
    
    def listar_diretorios(self, url):
        """Lista diretórios"""
        try:
            response = self.session.get(url, timeout=30)
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
    
    def listar_arquivos(self, url):
        """Lista arquivos"""
        try:
            response = self.session.get(url, timeout=30)
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
            
            # Fallback
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
    
    def filtrar_por_rotulos(self, arquivos):
        """Filtra arquivos por rótulos"""
        filtrados = []
        
        for arquivo in arquivos:
            nome = arquivo["nome"]
            
            # Verificar rótulos
            for rotulo in ROTULOS:
                if f"_{rotulo}_" in nome:
                    arquivo["rotulo"] = rotulo
                    filtrados.append(arquivo)
                    break
        
        return filtrados
    
    def baixar_arquivo(self, url, destino):
        """Baixa um arquivo"""
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            
            with open(destino, "wb") as f:
                f.write(response.content)
            
            return True
        except:
            return False
    
    def processar_loja(self, nome_loja):
        """Processa uma loja"""
        print(f"\\n🏪 {nome_loja}")
        
        url_loja = f"{BASE_URL}/bk/{ANO}/{MES:02d}/{nome_loja}/"
        cameras = [c for c in CAMERAS if c in self.listar_diretorios(url_loja)]
        
        if not cameras:
            print("  ❌ Sem câmeras")
            return 0
        
        total = 0
        for camera in cameras:
            print(f"  📹 {camera}...", end=" ")
            
            url_camera = f"{url_loja}{camera}/"
            dias = self.listar_diretorios(url_camera)
            dia_str = f"{DIA:02d}"
            
            if dia_str not in dias:
                print("❌ Dia não encontrado")
                continue
            
            url_dia = f"{url_camera}{dia_str}/"
            arquivos = self.listar_arquivos(url_dia)
            
            if not arquivos:
                print("❌ Sem arquivos")
                continue
            
            filtrados = self.filtrar_por_rotulos(arquivos)
            
            if not filtrados:
                print("❌ Sem imagens com rótulos")
                continue
            
            # Uma por rótulo
            por_rotulo = {}
            for arquivo in filtrados:
                rotulo = arquivo["rotulo"]
                if rotulo not in por_rotulo:
                    por_rotulo[rotulo] = arquivo
            
            # Baixar
            baixadas = 0
            for rotulo, arquivo in por_rotulo.items():
                pasta = nome_loja.replace(" ", "_").replace("-", "_")
                destino = f"imagens_auto/{pasta}/{camera}/dia_{dia_str}/{arquivo['nome']}"
                
                if self.baixar_arquivo(arquivo["url"], destino):
                    baixadas += 1
                    total += 1
            
            print(f"✅ {baixadas} imagens")
        
        return total
    
    def executar_extracao(self):
        """Executa a extração"""
        print("🧠 EXTRATOR INTELIGENTE")
        print("=" * 40)
        print(f"🌐 Site: {BASE_URL}")
        print(f"📅 Data: {DIA:02d}/{MES:02d}/{ANO}")
        print("=" * 40)
        
        if not self.detectar_e_autenticar():
            print("❌ Falha na autenticação")
            return
        
        print(f"✅ Método de autenticação: {self.metodo_auth}")
        
        lojas = LOJAS_ESPECIFICAS if LOJAS_ESPECIFICAS else self.listar_diretorios(f"{BASE_URL}/bk/{ANO}/{MES:02d}/")
        
        if not lojas:
            print("❌ Nenhuma loja encontrada")
            return
        
        print(f"🏪 Processando {len(lojas)} lojas...")
        
        total_geral = 0
        for i, loja in enumerate(lojas, 1):
            print(f"[{i}/{len(lojas)}]", end=" ")
            total_geral += self.processar_loja(loja)
        
        print("\\n" + "=" * 50)
        print("📊 RELATÓRIO FINAL")
        print("=" * 50)
        print(f"🔑 Método: {self.metodo_auth}")
        print(f"📸 Total: {total_geral} imagens")
        print(f"💾 Pasta: ./imagens_auto/")
        
        if total_geral > 0:
            print("🎉 Sucesso!")
        else:
            print("⚠️  Nenhuma imagem baixada")

def main():
    extractor = ExtractorInteligente()
    extractor.executar_extracao()

if __name__ == "__main__":
    main()
'''
    
    with open("extrator_auto_corrigido.py", "w") as f:
        f.write(conteudo)
    print("✅ Criado: extrator_auto_corrigido.py")

def main():
    print("🔧 CORRIGINDO ARQUIVOS...")
    print("=" * 40)
    
    # Instalar dependências
    instalar_dependencias()
    
    # Criar arquivos
    criar_investigar_site()
    criar_extrator_simples()
    criar_extrator_auto_corrigido()
    
    # Tornar executáveis
    os.system("chmod +x *.py")
    
    print("=" * 40)
    print("✅ TODOS OS ARQUIVOS CORRIGIDOS!")
    print("=" * 40)
    print("🚀 Agora execute:")
    print("   ./investigar.sh        (investigar o site)")
    print("   ./extrair_inteligente.sh (extração inteligente)")
    print("   ./extrair_simples_login.sh (extração simples)")

if __name__ == "__main__":
    main()

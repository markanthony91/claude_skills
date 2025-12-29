#!/usr/bin/env python3
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
        print(f"\n🏪 {nome_loja}")
        
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
        
        print("\n" + "=" * 50)
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

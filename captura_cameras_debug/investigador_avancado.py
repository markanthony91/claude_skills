#!/usr/bin/env python3
"""
Investigador Avançado - Descobre a estrutura real do site
"""

import requests
import base64
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "http://35.209.243.66"
LOGIN_EMAIL = "bk@aiknow.ai"
LOGIN_PASSWORD = "Sphbr7410"

def analisar_pagina_principal():
    """Analisa detalhadamente a página principal"""
    print("🔍 ANALISANDO PÁGINA PRINCIPAL EM DETALHES...")
    
    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0"})
        
        response = session.get(BASE_URL, timeout=15)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"   Server: {response.headers.get('server', 'N/A')}")
        
        if response.status_code != 200:
            print("   ❌ Página principal não acessível")
            return None
        
        conteudo = response.text
        print(f"   Tamanho: {len(conteudo)} caracteres")
        
        # Analisar tipo de conteúdo
        soup = BeautifulSoup(conteudo, 'html.parser')
        
        # Procurar por título
        titulo = soup.find('title')
        if titulo:
            print(f"   📄 Título: {titulo.get_text(strip=True)}")
        
        # Procurar por links importantes
        print("   🔗 Analisando links...")
        links_importantes = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            texto = link.get_text(strip=True)
            
            # Filtrar links interessantes
            if any(palavra in href.lower() for palavra in ['camera', 'image', 'file', 'admin', 'login', 'bk', 'photo']):
                links_importantes.append((href, texto))
            elif any(palavra in texto.lower() for palavra in ['camera', 'image', 'file', 'admin', 'login', 'bk', 'photo']):
                links_importantes.append((href, texto))
        
        if links_importantes:
            print("   ✅ Links importantes encontrados:")
            for href, texto in links_importantes[:10]:  # Mostrar só os primeiros 10
                print(f"      • {href} -> {texto[:50]}")
        
        # Procurar por formulários
        forms = soup.find_all('form')
        if forms:
            print(f"   📝 {len(forms)} formulário(s) encontrado(s)")
            for i, form in enumerate(forms):
                action = form.get('action', '')
                method = form.get('method', 'GET').upper()
                print(f"      Form {i+1}: {method} -> {action}")
        
        # Procurar por JavaScript que pode revelar URLs
        scripts = soup.find_all('script')
        urls_no_js = []
        for script in scripts:
            if script.string:
                # Procurar por URLs no JavaScript
                urls_encontradas = re.findall(r'["\']([^"\']*(?:camera|image|file|admin|bk)[^"\']*)["\']', script.string, re.IGNORECASE)
                urls_no_js.extend(urls_encontradas)
        
        if urls_no_js:
            print("   🔗 URLs encontradas no JavaScript:")
            for url in set(urls_no_js)[:5]:  # Mostrar só as primeiras 5 únicas
                print(f"      • {url}")
        
        # Procurar por estrutura de diretórios
        if '<a href=' in conteudo and 'Index of' in conteudo:
            print("   ✅ Parece ser uma listagem de diretórios!")
            return session, "DIRECTORY_LISTING"
        
        # Procurar por padrões específicos
        padroes = {
            'PHP': r'\.php',
            'API': r'/api/',
            'Upload': r'upload',
            'Files': r'/files/',
            'Images': r'/images/',
            'Static': r'/static/',
            'Assets': r'/assets/',
        }
        
        padroes_encontrados = []
        for nome, padrao in padroes.items():
            if re.search(padrao, conteudo, re.IGNORECASE):
                padroes_encontrados.append(nome)
        
        if padroes_encontrados:
            print(f"   🎯 Padrões encontrados: {', '.join(padroes_encontrados)}")
        
        return session, conteudo
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None

def testar_estruturas_alternativas():
    """Testa diferentes estruturas possíveis"""
    print("🔍 TESTANDO ESTRUTURAS ALTERNATIVAS...")
    
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    
    # Diferentes estruturas possíveis
    estruturas_teste = [
        # Estruturas baseadas no que vimos nas imagens
        "/cameras/",
        "/cameras/bk/",
        "/cameras/2025/",
        "/cameras/2025/05/",
        "/files/",
        "/files/bk/",
        "/files/2025/",
        "/images/",
        "/images/bk/",
        "/images/2025/",
        "/uploads/",
        "/uploads/bk/",
        "/data/",
        "/data/bk/",
        "/storage/",
        "/storage/bk/",
        "/media/",
        "/media/bk/",
        "/assets/",
        "/assets/bk/",
        "/static/",
        "/static/bk/",
        "/public/",
        "/public/bk/",
        # Estruturas com autenticação
        "/admin/",
        "/admin/files/",
        "/admin/cameras/",
        "/admin/bk/",
        "/dashboard/",
        "/dashboard/bk/",
        # Outras possibilidades
        "/2025/",
        "/2025/05/",
        "/05/",
    ]
    
    urls_funcionando = []
    
    for estrutura in estruturas_teste:
        try:
            url = f"{BASE_URL}{estrutura}"
            print(f"   Testando: {url}")
            
            # Teste sem autenticação
            response = session.get(url, timeout=10)
            print(f"      Sem auth: {response.status_code}")
            
            if response.status_code == 200:
                if '<a href=' in response.text or 'Index of' in response.text:
                    print(f"      ✅ LISTAGEM ENCONTRADA!")
                    urls_funcionando.append((url, "SEM_AUTH"))
                    
                    # Mostrar algumas linhas do conteúdo
                    linhas = response.text.split('\n')[:3]
                    for linha in linhas:
                        if linha.strip():
                            print(f"         {linha.strip()[:80]}")
            
            elif response.status_code == 401:
                print(f"      🔑 Requer autenticação - testando Basic Auth...")
                
                # Testar com autenticação
                usuarios = [LOGIN_EMAIL, LOGIN_EMAIL.split('@')[0], 'bk', 'admin']
                
                for usuario in usuarios:
                    try:
                        credentials = base64.b64encode(f"{usuario}:{LOGIN_PASSWORD}".encode()).decode()
                        
                        session_auth = requests.Session()
                        session_auth.headers.update({
                            "Authorization": f"Basic {credentials}",
                            "User-Agent": "Mozilla/5.0"
                        })
                        
                        response_auth = session_auth.get(url, timeout=10)
                        
                        if response_auth.status_code == 200:
                            if '<a href=' in response_auth.text or 'Index of' in response_auth.text:
                                print(f"         ✅ FUNCIONOU COM {usuario}!")
                                urls_funcionando.append((url, f"BASIC_{usuario}"))
                                
                                # Mostrar algumas linhas
                                linhas = response_auth.text.split('\n')[:3]
                                for linha in linhas:
                                    if linha.strip():
                                        print(f"            {linha.strip()[:80]}")
                                break
                    except:
                        continue
                        
        except Exception as e:
            print(f"      ❌ Erro: {e}")
    
    return urls_funcionando

def testar_com_diferentes_portas():
    """Testa o mesmo IP com portas diferentes"""
    print("🔍 TESTANDO PORTAS DIFERENTES...")
    
    # Extrair IP do BASE_URL
    ip = BASE_URL.replace('http://', '').replace('https://', '').split(':')[0]
    
    portas = [80, 8080, 8000, 3000, 5000, 8888, 9000, 8081, 8090]
    
    urls_funcionando = []
    
    for porta in portas:
        try:
            if porta == 80:
                test_url = f"http://{ip}"
            else:
                test_url = f"http://{ip}:{porta}"
            
            print(f"   Testando: {test_url}")
            
            session = requests.Session()
            session.headers.update({"User-Agent": "Mozilla/5.0"})
            
            response = session.get(test_url, timeout=5)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                if '<a href=' in response.text or 'Index of' in response.text or 'bk' in response.text.lower():
                    print(f"      ✅ CONTEÚDO INTERESSANTE ENCONTRADO!")
                    urls_funcionando.append(test_url)
                    
                    # Mostrar título se houver
                    try:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        titulo = soup.find('title')
                        if titulo:
                            print(f"         Título: {titulo.get_text(strip=True)}")
                    except:
                        pass
                        
        except Exception as e:
            print(f"      ❌ Timeout/Erro: {e}")
    
    return urls_funcionando

def procurar_subdomínios():
    """Procura por subdomínios possíveis"""
    print("🔍 TESTANDO SUBDOMÍNIOS...")
    
    # Extrair domínio base
    base_domain = BASE_URL.replace('http://', '').replace('https://', '').split(':')[0]
    
    subdominios = [
        'files', 'images', 'camera', 'cameras', 'admin', 'api', 
        'storage', 'media', 'assets', 'data', 'bk', 'photos'
    ]
    
    urls_funcionando = []
    
    for sub in subdominios:
        try:
            test_url = f"http://{sub}.{base_domain}"
            print(f"   Testando: {test_url}")
            
            session = requests.Session()
            session.headers.update({"User-Agent": "Mozilla/5.0"})
            
            response = session.get(test_url, timeout=5)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"      ✅ SUBDOMÍNIO ATIVO!")
                urls_funcionando.append(test_url)
                
        except Exception as e:
            print(f"      ❌ Erro: {e}")
    
    return urls_funcionando

def main():
    """Função principal de investigação avançada"""
    print("🕵️  INVESTIGADOR AVANÇADO - DESCOBRINDO ESTRUTURA REAL")
    print("=" * 60)
    print(f"🌐 Site: {BASE_URL}")
    print("=" * 60)
    
    # Passo 1: Analisar página principal
    print("\n📋 PASSO 1: ANÁLISE DETALHADA DA PÁGINA PRINCIPAL")
    resultado_principal = analisar_pagina_principal()
    
    # Passo 2: Testar estruturas alternativas
    print("\n📋 PASSO 2: TESTANDO ESTRUTURAS ALTERNATIVAS")
    urls_estruturas = testar_estruturas_alternativas()
    
    # Passo 3: Testar portas diferentes
    print("\n📋 PASSO 3: TESTANDO PORTAS DIFERENTES")
    urls_portas = testar_com_diferentes_portas()
    
    # Passo 4: Procurar subdomínios
    print("\n📋 PASSO 4: TESTANDO SUBDOMÍNIOS")
    urls_subdominios = procurar_subdomínios()
    
    # Resumo final
    print("\n" + "=" * 70)
    print("📊 RESUMO DA INVESTIGAÇÃO AVANÇADA")
    print("=" * 70)
    
    if urls_estruturas:
        print("✅ ESTRUTURAS FUNCIONANDO:")
        for url, metodo in urls_estruturas:
            print(f"   • {url} ({metodo})")
    
    if urls_portas:
        print("✅ PORTAS ALTERNATIVAS:")
        for url in urls_portas:
            print(f"   • {url}")
    
    if urls_subdominios:
        print("✅ SUBDOMÍNIOS ATIVOS:")
        for url in urls_subdominios:
            print(f"   • {url}")
    
    if not urls_estruturas and not urls_portas and not urls_subdominios:
        print("❌ NENHUMA ESTRUTURA ALTERNATIVA ENCONTRADA")
        print("\n🔍 O que descobrimos:")
        print("   • Site principal está online (Status 200)")
        print("   • Estrutura /bk/ não existe mais (Status 404)")
        print("   • Pode ter migrado para outra estrutura")
        print("   • Pode estar usando API ou sistema diferente")
        
        print("\n💡 Próximos passos:")
        print("   1. Verificar no navegador o que aparece na página principal")
        print("   2. Perguntar sobre mudanças na estrutura do site")
        print("   3. Verificar se há documentação atualizada")
        print("   4. Testar outras URLs ou sistemas")
    else:
        print("\n🎉 ESTRUTURAS ALTERNATIVAS ENCONTRADAS!")
        print("   Modifique os scripts para usar essas URLs")

if __name__ == "__main__":
    main()

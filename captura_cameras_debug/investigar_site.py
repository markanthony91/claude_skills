#!/usr/bin/env python3
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
                linhas = response.text.split('\n')[:5]
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
                    linhas = response.text.split('\n')[:5]
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
    print("\n📋 TESTE 1: ACESSO DIRETO")
    if testar_acesso_direto():
        print("\n✅ RESULTADO: Site acessível sem login!")
        print("🎉 Pode usar extrator sem autenticação!")
        return
    
    # Teste 2: HTTP Basic Auth
    print("\n📋 TESTE 2: HTTP BASIC AUTHENTICATION")
    usuario_sucesso = testar_http_basic()
    if usuario_sucesso:
        print(f"\n✅ RESULTADO: HTTP Basic Auth funcionou com usuário: {usuario_sucesso}!")
        print("🎉 Pode usar extrator com autenticação básica!")
        return
    
    # Teste 3: URLs diferentes
    print("\n📋 TESTE 3: DIFERENTES URLs")
    url_sucesso = testar_diferentes_urls()
    if url_sucesso:
        print(f"\n✅ RESULTADO: URL acessível encontrada: {url_sucesso}!")
        return
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO DA INVESTIGAÇÃO")
    print("=" * 50)
    print("❌ Nenhum método de autenticação funcionou")
    print("\n🔍 Possíveis problemas:")
    print("   • Site pode estar offline temporariamente")
    print("   • Credenciais podem ter mudado")
    print("   • Estrutura do site pode ter mudado")
    print("   • Firewall ou bloqueio de IP")
    
    print("\n💡 Próximos passos:")
    print("   1. Verificar se o site funciona no navegador")
    print("   2. Confirmar as credenciais atuais")
    print("   3. Tentar acessar manualmente primeiro")
    print("   4. Verificar se há mudanças no sistema")

if __name__ == "__main__":
    main()

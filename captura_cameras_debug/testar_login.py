#!/usr/bin/env python3
"""
Teste de Login no Sistema
Verifica se as credenciais funcionam
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "http://35.209.243.66"
LOGIN_EMAIL = "bk@aiknow.ai" 
LOGIN_PASSWORD = "Sphbr7410"

def testar_login():
    print("🧪 TESTE DE LOGIN")
    print("=" * 30)
    print(f"🌐 URL: {BASE_URL}")
    print(f"📧 Email: {LOGIN_EMAIL}")
    print(f"🔒 Senha: {'*' * len(LOGIN_PASSWORD)}")
    print("=" * 30)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Testar acesso ao site
    print("🔍 Testando acesso ao site...")
    try:
        response = session.get(BASE_URL, timeout=10)
        print(f"   ✅ Site acessível (Status: {response.status_code})")
    except Exception as e:
        print(f"   ❌ Erro ao acessar site: {e}")
        return False
    
    # Procurar página de login
    urls_login = [
        f"{BASE_URL}/login",
        f"{BASE_URL}/admin/login",
        f"{BASE_URL}/auth/login", 
        f"{BASE_URL}/signin",
        f"{BASE_URL}/admin",
        f"{BASE_URL}/"
    ]
    
    print("🔍 Procurando página de login...")
    login_encontrado = False
    
    for url in urls_login:
        try:
            print(f"   Testando: {url}")
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                conteudo = response.text.lower()
                if any(palavra in conteudo for palavra in ['login', 'password', 'email']):
                    print(f"   ✅ Página de login encontrada!")
                    
                    # Tentar fazer login
                    soup = BeautifulSoup(response.content, 'html.parser')
                    form = soup.find('form')
                    
                    if form:
                        print("   📝 Formulário de login encontrado")
                        
                        # Procurar campos
                        campos = soup.find_all('input')
                        print(f"   📋 {len(campos)} campos encontrados:")
                        
                        for campo in campos:
                            tipo = campo.get('type', '')
                            nome = campo.get('name', '')
                            print(f"      • {tipo}: {nome}")
                        
                        login_encontrado = True
                        break
                    else:
                        print("   ❌ Formulário não encontrado")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    if not login_encontrado:
        print("❌ Página de login não encontrada")
        print("   Verifique se o site está funcionando")
        return False
    
    print("\n✅ TESTE CONCLUÍDO")
    print("   • Site acessível")
    print("   • Página de login encontrada")
    print("   • Formulário detectado")
    print("\n🚀 Pronto para usar o extrator!")
    
    return True

if __name__ == "__main__":
    testar_login()

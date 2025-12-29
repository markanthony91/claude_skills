from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time

def debug_elementos_pagina(driver, descricao=""):
    """Função para debugar elementos da página"""
    print(f"\n=== DEBUG: {descricao} ===")
    print(f"URL atual: {driver.current_url}")
    print(f"Título da página: {driver.title}")
    
    # Listar todos os inputs
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"\nInputs encontrados ({len(inputs)}):")
    for i, inp in enumerate(inputs):
        tipo = inp.get_attribute("type")
        nome = inp.get_attribute("name")
        id_elem = inp.get_attribute("id")
        placeholder = inp.get_attribute("placeholder")
        print(f"  {i}: type='{tipo}', name='{nome}', id='{id_elem}', placeholder='{placeholder}'")
    
    print("=" * 50)

def automatizar_consulta_alphaville():
    """
    Automatiza o acesso ao site Recupera Alphaville seguindo o passo a passo exato
    """
    
    # Configurações do Chrome para evitar detecção
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar sem interface gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-javascript")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2
    })
    
    # Inicializar o driver
    driver = webdriver.Chrome(options=chrome_options)
    
    # Scripts para mascarar automação
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en']})")
    
    try:
        # Passo 1: Abrir o site com estratégias anti-detecção
        print("Passo 1: Abrindo o site...")
        
        # Primeiro, ir para a página principal
        try:
            driver.get("https://recupera.alphaville.com.br/")
            time.sleep(3)
            print("✓ Página principal acessada")
        except:
            print("⚠️ Erro ao acessar página principal")
        
        # Agora ir para a URL específica
        url = "https://recupera.alphaville.com.br/Recupera/login/login.aspx"
        driver.get(url)
        
        # Aguardar página carregar
        wait = WebDriverWait(driver, 20)
        time.sleep(3)
        
        # Verificar se foi redirecionado para página de erro
        if "entrada.aspx" in driver.current_url or "msg=" in driver.current_url:
            print("⚠️ Detectado redirecionamento para página de erro")
            print("Tentando acessar diretamente...")
            
            # Tentar limpar cookies e acessar novamente
            driver.delete_all_cookies()
            time.sleep(2)
            
            # Tentar URLs alternativas
            urls_alternativas = [
                "https://recupera.alphaville.com.br/Recupera/login/login.aspx?page=login",
                "https://recupera.alphaville.com.br/Recupera/login/login.aspx?page=login&Empresa=ALPHAVILLE",
                "https://recupera.alphaville.com.br/recupera/login/login.aspx",
                "https://recupera.alphaville.com.br/Login/"
            ]
            
            for url_alt in urls_alternativas:
                try:
                    print(f"Tentando: {url_alt}")
                    driver.get(url_alt)
                    time.sleep(3)
                    
                    # Verificar se chegou na página certa
                    if "entrada.aspx" not in driver.current_url and "msg=" not in driver.current_url:
                        print(f"✓ Sucesso com URL: {url_alt}")
                        break
                except:
                    continue
            else:
                print("❌ Todas as URLs falharam. Tentando abrir nova sessão...")
                driver.quit()
                
                # Tentar sem headless para debug
                chrome_options = Options()
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")
                
                driver = webdriver.Chrome(options=chrome_options)
                driver.get("https://recupera.alphaville.com.br/Recupera/login/login.aspx")
                time.sleep(5)
        
        debug_elementos_pagina(driver, "Página de Login")
        
        # Passo 2: Inserir usuário no campo "txtOperador"
        print("Passo 2: Inserindo usuário...")
        try:
            campo_usuario = wait.until(EC.presence_of_element_located((By.ID, "txtOperador")))
            campo_usuario.clear()
            campo_usuario.send_keys("adriana.cls")
            print("✓ Usuário inserido com sucesso")
        except Exception as e:
            print(f"❌ Erro no campo usuário: {e}")
            # Tentar xpath alternativo
            try:
                campo_usuario = driver.find_element(By.XPATH, "//input[@id='txtOperador']")
                campo_usuario.clear()
                campo_usuario.send_keys("adriana.cls")
                print("✓ Usuário inserido com xpath alternativo")
            except:
                print("❌ Campo usuário não encontrado!")
                return None
        
        time.sleep(1)
        
        # Passo 3: Inserir senha no campo "txtSenha"
        print("Passo 3: Inserindo senha...")
        try:
            campo_senha = driver.find_element(By.ID, "txtSenha")
            campo_senha.clear()
            campo_senha.send_keys("2099cla")
            print("✓ Senha inserida com sucesso")
        except Exception as e:
            print(f"❌ Erro no campo senha: {e}")
            # Tentar xpath alternativo
            try:
                campo_senha = driver.find_element(By.XPATH, "//input[@id='txtSenha']")
                campo_senha.clear()
                campo_senha.send_keys("2099cla")
                print("✓ Senha inserida com xpath alternativo")
            except:
                print("❌ Campo senha não encontrado!")
        
        time.sleep(1)
        
        # Passo 4: Clicar no botão "cmdOk"
        print("Passo 4: Clicando no botão de login...")
        try:
            botao_login = driver.find_element(By.ID, "cmdOk")
            driver.execute_script("arguments[0].click();", botao_login)
            print("✓ Botão de login clicado com sucesso")
        except Exception as e:
            print(f"❌ Erro no botão login: {e}")
            # Tentar xpath alternativo
            try:
                botao_login = driver.find_element(By.XPATH, "//input[@id='cmdOk']")
                driver.execute_script("arguments[0].click();", botao_login)
                print("✓ Botão de login clicado com xpath alternativo")
            except:
                print("❌ Botão de login não encontrado!")
        
        # Aguardar login ser processado
        print("Aguardando login ser processado...")
        time.sleep(5)
        
        # Verificar se login foi bem-sucedido
        current_url = driver.current_url
        print(f"URL após login: {current_url}")
        
        debug_elementos_pagina(driver, "Página após login")
        
        # Passo 5: Clicar em "Novo Módulo"
        print("Passo 5: Clicando em 'Novo Módulo'...")
        try:
            # Tentar primeiro seletor
            novo_modulo = wait.until(EC.element_to_be_clickable((
                By.XPATH, 
                "//td[@onmouseup=\"mnuLocation('../login/redirectNovo.aspx');\"][normalize-space()='Novo Módulo']"
            )))
            driver.execute_script("arguments[0].click();", novo_modulo)
            print("✓ 'Novo Módulo' clicado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao clicar 'Novo Módulo': {e}")
            # Tentar seletor CSS alternativo
            try:
                novo_modulo = driver.find_element(By.CSS_SELECTOR, 
                    "body > div:nth-child(4) > div:nth-child(3) > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1)")
                driver.execute_script("arguments[0].click();", novo_modulo)
                print("✓ 'Novo Módulo' clicado com CSS selector")
            except:
                # Tentar buscar por texto
                try:
                    novo_modulo = driver.find_element(By.XPATH, "//td[contains(text(), 'Novo Módulo')]")
                    driver.execute_script("arguments[0].click();", novo_modulo)
                    print("✓ 'Novo Módulo' encontrado por texto")
                except:
                    print("❌ 'Novo Módulo' não encontrado!")
        
        time.sleep(3)
        
        # Passo 6: Clicar em "Operação"
        print("Passo 6: Clicando em 'Operação'...")
        try:
            operacao = wait.until(EC.element_to_be_clickable((
                By.XPATH, 
                "//app-menu-item[contains(text(),'Operação')]"
            )))
            driver.execute_script("arguments[0].click();", operacao)
            print("✓ 'Operação' clicado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao clicar 'Operação': {e}")
            # Tentar seletor CSS alternativo
            try:
                operacao = driver.find_element(By.CSS_SELECTOR, "app-menu-item[title='Operação']")
                driver.execute_script("arguments[0].click();", operacao)
                print("✓ 'Operação' clicado com CSS selector")
            except:
                # Tentar buscar por texto simples
                try:
                    operacao = driver.find_element(By.XPATH, "//*[contains(text(), 'Operação')]")
                    driver.execute_script("arguments[0].click();", operacao)
                    print("✓ 'Operação' encontrado por texto")
                except:
                    print("❌ 'Operação' não encontrado!")
        
        time.sleep(3)
        
        debug_elementos_pagina(driver, "Página de Operação")
        
        # Passo 7: Inserir nome no campo "nome"
        print("Passo 7: Inserindo nome no campo...")
        try:
            campo_nome = wait.until(EC.element_to_be_clickable((By.NAME, "nome")))
            campo_nome.clear()
            campo_nome.send_keys("YARA REGINA GONÇALVES DIAS")
            print("✓ Nome inserido com sucesso")
        except Exception as e:
            print(f"❌ Erro no campo nome: {e}")
            # Tentar CSS selector alternativo
            try:
                campo_nome = driver.find_element(By.CSS_SELECTOR, "input[name='nome']")
                campo_nome.clear()
                campo_nome.send_keys("YARA REGINA GONÇALVES DIAS")
                print("✓ Nome inserido com CSS selector")
            except:
                # Tentar xpath alternativo
                try:
                    campo_nome = driver.find_element(By.XPATH, "//input[@name='nome']")
                    campo_nome.clear()
                    campo_nome.send_keys("YARA REGINA GONÇALVES DIAS")
                    print("✓ Nome inserido com xpath")
                except:
                    print("❌ Campo nome não encontrado!")
                    return None
        
        time.sleep(1)
        
        # Passo 8: Clicar no botão de busca (lupa/Nome)
        print("Passo 8: Clicando no botão de busca...")
        try:
            # Tentar encontrar botão de busca próximo ao campo nome
            botao_busca = driver.find_element(By.XPATH, "//div[contains(@class, 'busca') or contains(@onclick, 'busca')]")
            driver.execute_script("arguments[0].click();", botao_busca)
            print("✓ Botão de busca clicado")
        except:
            try:
                # Tentar buscar por imagem de lupa
                botao_busca = driver.find_element(By.XPATH, "//input[@type='image' and contains(@src, 'lupa')]")
                driver.execute_script("arguments[0].click();", botao_busca)
                print("✓ Lupa clicada")
            except:
                try:
                    # Tentar Enter no campo nome
                    campo_nome.send_keys(Keys.RETURN)
                    print("✓ Enter enviado no campo nome")
                except:
                    # Tentar qualquer botão próximo
                    try:
                        botao_busca = driver.find_element(By.XPATH, "//button | //input[@type='button'] | //input[@type='submit']")
                        driver.execute_script("arguments[0].click();", botao_busca)
                        print("✓ Botão genérico clicado")
                    except:
                        print("❌ Nenhum botão de busca encontrado!")
        
        # Aguardar resultados
        print("Aguardando resultados da busca...")
        time.sleep(5)
        
        debug_elementos_pagina(driver, "Página de Resultados")
        
        # Extrair informações
        print("\nExtraindo dados...")
        divisao = "Não encontrado"
        unidade = "Não encontrado"
        
        try:
            page_source = driver.page_source
            
            # Estratégia 1: Procurar em tabelas
            tabelas = driver.find_elements(By.TAG_NAME, "table")
            print(f"Encontradas {len(tabelas)} tabelas")
            
            for tabela in tabelas:
                try:
                    linhas = tabela.find_elements(By.TAG_NAME, "tr")
                    for linha in linhas:
                        colunas = linha.find_elements(By.TAG_NAME, "td")
                        if len(colunas) >= 2:
                            label = colunas[0].text.lower().strip()
                            valor = colunas[1].text.strip()
                            
                            if "divisão" in label or "divisao" in label:
                                divisao = valor
                                print(f"✓ Divisão encontrada na tabela: {divisao}")
                            
                            if "unidade" in label:
                                unidade = valor
                                print(f"✓ Unidade encontrada na tabela: {unidade}")
                except:
                    continue
            
            # Estratégia 2: Procurar por spans/divs com labels
            if divisao == "Não encontrado":
                try:
                    elementos_divisao = driver.find_elements(By.XPATH, "//*[contains(text(), 'Divisão') or contains(text(), 'Divisao')]")
                    for elemento in elementos_divisao:
                        try:
                            parent = elemento.find_element(By.XPATH, "./..")
                            texto_completo = parent.text
                            if ":" in texto_completo:
                                divisao = texto_completo.split(":")[-1].strip()
                                print(f"✓ Divisão encontrada por label: {divisao}")
                                break
                        except:
                            continue
                except:
                    pass
            
            if unidade == "Não encontrado":
                try:
                    elementos_unidade = driver.find_elements(By.XPATH, "//*[contains(text(), 'Unidade')]")
                    for elemento in elementos_unidade:
                        try:
                            parent = elemento.find_element(By.XPATH, "./..")
                            texto_completo = parent.text
                            if ":" in texto_completo:
                                unidade = texto_completo.split(":")[-1].strip()
                                print(f"✓ Unidade encontrada por label: {unidade}")
                                break
                        except:
                            continue
                except:
                    pass
            
            # Estratégia 3: Regex no código fonte
            if divisao == "Não encontrado":
                import re
                matches = re.finditer(r'(?:divisão|divisao)[:\s]*([^<>\n]+)', page_source, re.IGNORECASE)
                for match in matches:
                    divisao_candidata = match.group(1).strip()
                    if divisao_candidata and len(divisao_candidata) > 2:
                        divisao = divisao_candidata
                        print(f"✓ Divisão encontrada por regex: {divisao}")
                        break
            
            if unidade == "Não encontrado":
                import re
                matches = re.finditer(r'unidade[:\s]*([^<>\n]+)', page_source, re.IGNORECASE)
                for match in matches:
                    unidade_candidata = match.group(1).strip()
                    if unidade_candidata and len(unidade_candidata) > 2:
                        unidade = unidade_candidata
                        print(f"✓ Unidade encontrada por regex: {unidade}")
                        break
        
        except Exception as e:
            print(f"Erro ao extrair dados: {e}")
        
        # Mostrar resultados
        print("\n" + "="*60)
        print("🎯 RESULTADOS DA CONSULTA")
        print("="*60)
        print(f"👤 Pessoa: YARA REGINA GONÇALVES DIAS")
        print(f"🏢 **Divisão**: {divisao}")
        print(f"🏬 **Unidade**: {unidade}")
        print("="*60)
        
        return {
            "divisao": divisao,
            "unidade": unidade,
            "pessoa": "YARA REGINA GONÇALVES DIAS"
        }
    
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        print("Salvando screenshot para debug...")
        try:
            driver.save_screenshot("error_screenshot.png")
            print("Screenshot salvo como 'error_screenshot.png'")
        except:
            pass
    
    finally:
        # Fechar automaticamente
        driver.quit()

# Função para instalar dependências necessárias
def instalar_dependencias():
    """
    Instala as dependências necessárias
    """
    import subprocess
    import sys
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
        print("Selenium instalado com sucesso!")
    except Exception as e:
        print(f"Erro ao instalar selenium: {e}")

if __name__ == "__main__":
    print("🔧 Script de Automação - Site Recupera Alphaville")
    print("="*60)
    print("📋 Seguindo passo a passo exato fornecido")
    print("="*60)
    
    # Verificar se selenium está instalado
    try:
        import selenium
    except ImportError:
        print("Selenium não encontrado. Instalando...")
        instalar_dependencias()
    
    # Executar automação
    result = automatizar_consulta_alphaville()
    
    if result:
        print("\n✅ Automação concluída com sucesso!")
    else:
        print("\n❌ Automação falhou. Verifique os logs acima.")

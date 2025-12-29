#!/usr/bin/env python3
"""
Configurador para Extrator com Login
"""

import os
from datetime import datetime

def configurar():
    print("🎯 CONFIGURADOR COM LOGIN")
    print("=" * 40)
    print("🔑 Credenciais já configuradas:")
    print("   📧 Email: bk@aiknow.ai")
    print("   🔒 Senha: Sphbr7410")
    print("   🌐 Site: http://35.209.243.66")
    print("=" * 40)
    
    # Data
    print("\n📅 CONFIGURAÇÃO DE DATA:")
    ano = int(input("   Ano (default: 2025): ") or "2025")
    mes = int(input("   Mês (1-12, default: 5): ") or "5")
    dia = int(input("   Dia (1-31, default: 29): ") or "29")
    
    # Horário
    print("\n⏰ CONFIGURAÇÃO DE HORÁRIO:")
    usar_horario = input("   Filtrar por horário? (s/N): ").lower() == 's'
    
    if usar_horario:
        horario_inicio = input("   Horário início (HH:MM, ex: 14:00): ")
        horario_fim = input("   Horário fim (HH:MM, ex: 16:00): ")
    else:
        horario_inicio = None
        horario_fim = None
    
    # Lojas
    print("\n🏪 CONFIGURAÇÃO DE LOJAS:")
    print("1. Lojas específicas")
    print("2. Buscar todas após login")
    
    opcao = input("Escolha (1-2, default: 1): ") or "1"
    
    if opcao == "1":
        lojas_str = input("Digite nomes das lojas (separados por vírgula): ")
        lojas = [loja.strip() for loja in lojas_str.split(',') if loja.strip()]
    else:
        lojas = []
    
    # Criar arquivo de configuração
    config_content = f'''#!/usr/bin/env python3
"""
Configuração com Login - Gerada em {datetime.now()}
"""

# === CONFIGURAÇÕES DE LOGIN ===
BASE_URL = "http://35.209.243.66"
LOGIN_EMAIL = "bk@aiknow.ai"
LOGIN_PASSWORD = "Sphbr7410"

# === CONFIGURAÇÕES DE EXTRAÇÃO ===
ANO = {ano}
MES = {mes}
DIA = {dia}

HORARIO_INICIO = "{horario_inicio}" if "{horario_inicio}" != "None" else None
HORARIO_FIM = "{horario_fim}" if "{horario_fim}" != "None" else None

LOJAS_ESPECIFICAS = {lojas}

# === FIXO ===
ROTULOS = ['d0', 'd1', 'd2', 'd3']
CAMERAS = ['P1', 'P2', 'P3']

# === RESUMO ===
print("📋 CONFIGURAÇÃO COM LOGIN:")
print(f"   🔑 Site: {{BASE_URL}}")
print(f"   📧 Login: {{LOGIN_EMAIL}}")
print(f"   📅 Data: {{DIA:02d}}/{{MES:02d}}/{{ANO}}")
if HORARIO_INICIO and HORARIO_FIM:
    print(f"   ⏰ Horário: {{HORARIO_INICIO}} às {{HORARIO_FIM}}")
else:
    print("   ⏰ Sem filtro de horário")
print(f"   🏷️  Rótulos: {{', '.join(ROTULOS)}}")
if LOJAS_ESPECIFICAS:
    print(f"   🏪 Lojas específicas: {{len(LOJAS_ESPECIFICAS)}}")
else:
    print("   🏪 Todas as lojas")
print("=" * 50)
'''
    
    with open('config_login.py', 'w') as f:
        f.write(config_content)
    
    print("\n✅ Configuração salva em: config_login.py")
    print("🧪 Para testar login: python3 testar_login.py")
    print("🚀 Para extrair: python3 extrator_com_login_simples.py")

if __name__ == "__main__":
    configurar()

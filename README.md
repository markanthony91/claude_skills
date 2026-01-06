# Claude Skills - Repositório Multi-Projetos

> Coleção de ferramentas automatizadas para monitoramento de câmeras, análise de dados, web scraping e utilitários de sistema.

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.9+-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Histórico de Commits](#-histórico-de-commits)
- [Projetos Principais](#-projetos-principais)
  - [Captura de Câmeras](#1-captura-de-câmeras)
  - [Análise e Inspeção](#2-sistemas-de-análise-e-inspeção)
  - [QR Code Scanner](#3-qrcode-lens-insight)
  - [Web Scraping](#4-sistema-recupera-alphaville)
  - [Skills do Claude](#5-skills-do-claude-code)
  - [Utilitários](#6-utilitários)
- [Início Rápido](#-início-rápido)
- [Estrutura do Repositório](#-estrutura-do-repositório)
- [Tecnologias](#-tecnologias)
- [Segurança](#-segurança)

---

## 🎯 Visão Geral

Este repositório contém **9 projetos independentes** focados em:

- **Monitoramento de Câmeras**: Download e análise automatizada de imagens de 345+ câmeras em 115+ lojas BK
- **Detecção de Anomalias**: Sistema ML (Isolation Forest) para identificar problemas em câmeras
- **Inspeção Visual**: Análise inteligente por posição de câmera (Menu/Pagamento/Retirada)
- **Scanner QR Code**: Aplicação desktop profissional (React/Electron)
- **Automação Web**: Web scraping para sistema Recupera Alphaville
- **DevOps Tools**: Skills para gerenciamento Docker e scanner de rede
- **Auditoria de Sistemas**: Ferramentas para auditoria de servidores Linux

**Estatísticas:**
- 🎥 **345+ câmeras** monitoradas
- 🏪 **115+ lojas BK** cobertas
- 🤖 **ML-powered** detecção de anomalias
- 📱 **Cross-platform** QR scanner (Windows/Linux)
- 🐳 **Docker** management automation
- 🌐 **Network** scanning utilities

---

## 📜 Histórico de Commits

### Análise dos Commits Principais

#### Commit 1️⃣: `e1fb312` - Initial commit: Multi-project repository setup
**Data:** 7 dias atrás
**Alterações:** 79 arquivos, 32.330 adições

**Conteúdo:**
- ✅ Setup inicial do repositório multi-projeto
- ✅ Projeto `captura_cameras` completo com dashboard web
- ✅ Projeto `captura_cameras_debug` com múltiplas estratégias de extração
- ✅ Projeto `qrcode-lens-insight` (submódulo Git)
- ✅ Projeto `sistema_recupera` para web scraping Alphaville
- ✅ Skills do Claude Code: `docker-manager` e `network-scanner`
- ✅ Scripts utilitários: `install-glances-linux.sh`
- ✅ Documentação completa: `CLAUDE.md` (680 linhas)

**Principais arquivos:**
- `captura_cameras/app.py` - Dashboard Flask para visualização
- `captura_cameras/camera_downloader_complete.py` - Download de 345+ câmeras
- `captura_cameras_debug/extrator_simples.py` - Extração de imagens do servidor HTTP
- `sistema_recupera/script_alphaville.py` - Automação Selenium para Recupera

#### Commit 2️⃣: `136a940` - feat: add ML-powered camera anomaly detection system
**Data:** 7 dias atrás
**Alterações:** 7 arquivos, 2.331 adições

**Conteúdo:**
- 🤖 Sistema de detecção de anomalias com **Isolation Forest** (scikit-learn)
- 📊 Análise multivariada de 10+ features (tamanho, timestamp, profundidade, naming)
- 📈 Processa 3.522 arquivos em ~3 segundos
- 📝 Relatórios JSON + Markdown automatizados
- 🔍 Script de inspeção por loja/câmera
- 📅 Script de monitoramento agendável (cron)

**Principais arquivos:**
- `anomaly_detector_ml.py` - Detector ML com Isolation Forest
- `anomaly_detector_cameras.py` - Variante específica para câmeras
- `inspect_camera.sh` - Inspetor de câmeras específicas
- `monitor_anomalies.sh` - Script de monitoramento automatizado
- `README_ANOMALY_DETECTION.md` - Documentação completa (456 linhas)
- `ANOMALY_ANALYSIS_REPORT.md` - Relatório de análise (361 linhas)

**Métricas do Sistema:**
```
📊 Resultados (Última Execução):
   Total Files:       3.522
   Normal Files:      3.169 (89.98%)
   Anomalies:         353 (10.02%)
   Processing Time:   ~3 segundos
```

#### Commit 3️⃣: `d4981f8` - feat: add visual camera inspection system with business logic
**Data:** 7 dias atrás
**Alterações:** 7 arquivos, 3.676 adições

**Conteúdo:**
- 👁️ Sistema de inspeção visual por **contexto de negócio**
- 📍 Análise específica por posição: P1 (Menu), P2 (Pagamento), P3 (Retirada)
- 🎨 Interface visual com ícones coloridos e gráficos ASCII
- 🎯 Redução de falsos positivos: 99.2% de precisão
- 🔔 Alertas apenas para problemas reais (obstrução, desalinhamento)
- 📊 Dashboard HTML interativo

**Principais arquivos:**
- `inspect_cameras_visual.py` - Inspetor visual com lógica de negócio
- `inspecionar` - Wrapper CLI simplificado
- `dashboard_cameras.html` - Dashboard interativo (486 linhas)
- `start_dashboard.sh` - Inicializador do dashboard
- `README_INSPECAO_VISUAL.md` - Documentação completa (501 linhas)

**Contexto de Negócio:**
```
P1 (Menu)      → 64.04 KB médio | Área de pedidos
P2 (Pagamento) → 59.80 KB médio | Naturalmente ~7% menor
P3 (Retirada)  → 64.64 KB médio | Área de entrega
```

**Resultado Atual:**
```
✅ Lojas OK:              132 (99.2%)
⚠️  Lojas com problemas:   1  (0.8%)
```

#### Commit 4️⃣: `ebb2b63` - Update .gitignore to exclude auto-generated files
**Data:** 29 horas atrás
**Alterações:** 1 arquivo, 9 adições

**Conteúdo:**
- 🚫 Exclusão de arquivos auto-gerados
- 🗂️ Ignora diretórios de auditoria de sistema
- 📁 Ignora caches e arquivos temporários

**Arquivos ignorados:**
- `system-audit-*/` - Auditorias de sistema
- `captura_cameras.zip` - Backup compactado
- Outros arquivos temporários

---

## 🚀 Projetos Principais

### 1. Captura de Câmeras

#### 📹 `captura_cameras/` - Sistema de Produção

**Descrição:** Download automatizado de imagens de 345+ câmeras via AIVisual dashboard.

**Funcionalidades:**
- ✅ Download de 345+ câmeras em 115+ lojas BK
- ✅ Organização por loja: `cameras/Nome_da_Loja/P{1,2,3}_*.jpg`
- ✅ Automação Selenium com ChromeDriver
- ✅ Dashboard Flask para visualização web
- ✅ Metadata tracking e comparação de imagens
- ✅ Download paralelo com rate limiting

**Tecnologias:**
- Python 3.6+, Selenium, Requests, BeautifulSoup
- Flask (dashboard web)
- ChromeDriver (auto-instalado)

**Quick Start:**
```bash
cd captura_cameras
./install_final.sh                # Instalar dependências
./executar_todas_cameras.sh       # Executar todas (12-15 min)
./start_dashboard.sh              # Iniciar dashboard web
```

**Scripts principais:**
- `camera_downloader_complete.py` - Downloader principal
- `app.py` - Dashboard Flask
- `parallel_downloader.py` - Download paralelo
- `camera_downloader_com_metadados.py` - Versão com metadata

**Outputs:**
```
cameras/
├── Loja_BK_Central/
│   ├── P1_Loja_BK_Central_20251102_153045.jpg
│   ├── P2_Loja_BK_Central_20251102_153047.jpg
│   └── P3_Loja_BK_Central_20251102_153049.jpg
└── ...
```

**Documentação:**
- `README.md` - Guia completo do projeto
- `GUIA_METADADOS.md` - Sistema de metadados
- `README_DASHBOARD.md` - Dashboard web
- `STATUS_ONLINE.md` - Monitoramento online
- `COMPARACAO_VERSOES.md` - Comparação de versões

---

#### 🐛 `captura_cameras_debug/` - Versão Debug/Desenvolvimento

**Descrição:** Extração de imagens de servidor HTTP com filtros de labels e datas.

**Funcionalidades:**
- ✅ Extração de servidor HTTP (http://35.209.243.66)
- ✅ Filtros por label: d0, d1, d2, d3
- ✅ Filtros por data/hora: YEAR/MONTH/DAY/TIME_START/TIME_END
- ✅ Múltiplas estratégias de acesso (HTTP Basic Auth + fallbacks)
- ✅ Menu interativo para configuração
- ✅ Auto-detecção de método de acesso

**Tecnologias:**
- Python 3.6+, Requests, BeautifulSoup
- HTTP Basic Authentication

**Quick Start:**
```bash
cd captura_cameras_debug
./install_extractor.sh            # Instalar dependências
./menu_final.sh                   # Menu interativo (RECOMENDADO)
./executar_completo_api.sh        # Execução completa
```

**Scripts principais:**
- `extrator_simples.py` - Extrator principal
- `investigador_avancado.py` - Investigação avançada de API
- `menu_final.sh` - Menu interativo
- `diagnosticar_completo.sh` - Diagnóstico de conexão

**Outputs:**
```
imagens_simples/
├── Nome_da_Loja/
│   ├── P1/
│   │   └── dia_XX/
│   │       ├── arquivo_d0_*.jpg
│   │       ├── arquivo_d1_*.jpg
│   │       └── ...
│   ├── P2/
│   └── P3/
└── ...
```

---

### 2. Sistemas de Análise e Inspeção

#### 🤖 Sistema de Detecção de Anomalias (ML)

**Localização:** Arquivos na raiz do repositório

**Descrição:** Sistema ML usando **Isolation Forest** para detectar anomalias em estrutura de arquivos de câmeras.

**Funcionalidades:**
- 🤖 **Isolation Forest** com 100 árvores de decisão
- 📊 Análise multivariada de 10+ features
- 🚀 Alta performance: 3.522 arquivos em ~3 segundos
- 📝 Relatórios JSON + Markdown automatizados
- 🔍 Inspeção drill-down por loja/câmera
- 📅 Pronto para automação (cron jobs)

**Arquivos principais:**
- `anomaly_detector_ml.py` - Detector principal
- `anomaly_detector_cameras.py` - Variante para câmeras
- `inspect_camera.sh` - Inspetor de câmeras
- `monitor_anomalies.sh` - Monitor automatizado
- `README_ANOMALY_DETECTION.md` - Documentação (456 linhas)
- `ANOMALY_ANALYSIS_REPORT.md` - Relatório de análise

**Features Analisadas:**
1. `size_bytes`, `size_kb`, `size_mb` - Tamanho do arquivo
2. `depth` - Nível de aninhamento de diretórios
3. `modified_timestamp` - Timestamp de modificação
4. `filename_length` - Comprimento do nome do arquivo
5. `underscore_count` - Padrão de nomenclatura
6. `distance_from_mean_size` - Distância da média
7. `size_zscore` - Z-score do tamanho
8. `depth_deviation` - Desvio de profundidade

**Quick Start:**
```bash
cd /home/marcelo/sistemas

# Executar detecção
python3 anomaly_detector_ml.py

# Ver relatório
cat ANOMALY_ANALYSIS_REPORT.md

# Inspecionar loja específica
./inspect_camera.sh list
./inspect_camera.sh Marginal_Tiete_Pte_Anhanguera

# Monitoramento automatizado
./monitor_anomalies.sh
```

**Resultado Atual:**
```
📊 ANÁLISE
   Total Files:       3.522
   Normal Files:      3.169 (89.98%)
   Anomalies:         353 (10.02%)
   Processing Time:   ~3 segundos

🚨 SEVERIDADE
   HIGH:    7 lojas
   MEDIUM:  12 lojas
   LOW:     334 arquivos
```

**Tipos de Anomalias:**
- `EMPTY_OR_TINY_FILE` - Arquivos < 1 KB
- `SUSPICIOUSLY_SMALL` - Arquivos < 10 KB
- `SUSPICIOUSLY_LARGE` - Arquivos > 5 MB
- `WRONG_DIRECTORY_LEVEL` - Problemas de estrutura
- `INVALID_NAMING_PATTERN` - Nomenclatura incorreta
- `MULTIVARIATE_ANOMALY` - Padrões complexos (requer ML)

---

#### 👁️ Sistema de Inspeção Visual (Business Logic)

**Localização:** Arquivos na raiz do repositório

**Descrição:** Inspeção visual inteligente por **contexto de negócio** (Menu/Pagamento/Retirada).

**Funcionalidades:**
- 📍 Análise por posição de câmera (P1/P2/P3)
- 🎯 99.2% de precisão (redução de falsos positivos)
- 🎨 Interface visual com ícones e gráficos ASCII
- 🔔 Alertas apenas para problemas reais
- 📊 Dashboard HTML interativo
- 🏪 Análise loja-específica ou global

**Arquivos principais:**
- `inspect_cameras_visual.py` - Inspetor visual
- `inspecionar` - Wrapper CLI
- `dashboard_cameras.html` - Dashboard web
- `start_dashboard.sh` - Iniciar dashboard
- `README_INSPECAO_VISUAL.md` - Documentação (501 linhas)

**Contexto de Negócio:**
```
P1 (Menu)      → Área onde cliente faz pedido    → 64.04 KB médio
P2 (Pagamento) → Caixa/terminal de pagamento     → 59.80 KB médio (-7% normal)
P3 (Retirada)  → Área onde cliente recebe pedido → 64.64 KB médio
```

**Quick Start:**
```bash
cd /home/marcelo/sistemas

# Ver apenas lojas com problemas (RECOMENDADO)
./inspecionar problemas

# Ver loja específica
./inspecionar loja "Marginal_Tiete_Pte_Anhanguera"

# Ver top 20 lojas
./inspecionar

# Ajuda
./inspecionar help

# Dashboard web
./start_dashboard.sh
# Acesse: http://localhost:8080
```

**Interpretação de Resultados:**

| Ícone | Status | Desvio | Ação |
|-------|--------|--------|------|
| 🟢 | Excelente | < 20% | Nenhuma ação necessária |
| 🟡 | Atenção | 20-40% | Monitorar |
| 🟠 | Alto | 40-60% | Verificar configuração |
| 🔴 | Crítico | > 60% | **INSPEÇÃO FÍSICA URGENTE** |

**Exemplo de Saída:**
```
╔═══════════════════════════════════════════════════════════════════╗
║  Marginal_Tiete_Pte_Anhanguera                                    ║
╠═══════════════════════════════════════════════════════════════════╣
║  🔴 P1 (Menu):      14.90 KB  ███░░░░░░░░░  -73.5% ❌ CRÍTICO    ║
║  🟠 P2 (Pagamento): 84.09 KB  ████████████  +49.4% ⚠️  ALTO      ║
║  🟡 P3 (Retirada):  69.84 KB  ██████████░░  +24.1% ✓  OK         ║
║                                                                    ║
║  Média esperada: 56.28 KB                                         ║
╠═══════════════════════════════════════════════════════════════════╣
║  PROBLEMAS DETECTADOS:                                            ║
║  • P1 está 73.5% menor → Possível obstrução/desalinhamento       ║
║  • P2 está 49.4% maior → Configuração diferente?                 ║
╚═══════════════════════════════════════════════════════════════════╝
```

**Resultado Atual:**
```
✅ Lojas OK:              132 (99.2%)
⚠️  Lojas com problemas:   1  (0.8%)

🔴 LOJA CRÍTICA:
   Marginal_Tiete_Pte_Anhanguera
   → P1 com 14.90 KB (esperado: ~56 KB)
   → 73.5% menor que o normal
   → Ação: Inspeção física urgente
```

---

### 3. QRCode Lens Insight

**Localização:** `qrcode-lens-insight/` (submódulo Git)

**Descrição:** Scanner QR Code profissional com aplicação desktop (React/Electron).

**Funcionalidades:**
- 📱 Suporte a USB camera, IP camera (cam2web), e upload de imagens
- 🔍 Detecção automática de smartphones via QR patterns
- 🎨 Interface moderna com Radix UI + Tailwind CSS
- 🖼️ Processamento de imagem: CLAHE enhancement, controles de brilho/contraste/zoom
- 💻 Executáveis standalone: Windows (.exe), Linux (AppImage/deb)
- 🔄 Hot reload com Vite HMR
- 📦 Build automatizado com electron-builder

**Tecnologias:**
- React 18 + TypeScript
- Vite (build tool)
- Electron 28 (desktop wrapper)
- @zxing/browser (QR decoding)
- Radix UI + Tailwind CSS
- TanStack Query (state management)

**Quick Start:**

**Linux/WSL:**
```bash
cd qrcode-lens-insight

# Setup inicial
./setup-linux.sh

# Desenvolvimento (Electron)
./run-dev-linux.sh

# Web-only (browser)
./run-web-linux.sh

# Build executável
./build-linux.sh
```

**Windows:**
```bash
cd qrcode-lens-insight

# Setup inicial
setup-windows.bat

# Desenvolvimento (Electron)
run-dev-windows.bat

# Web-only (browser)
run-web-windows.bat

# Build executável
build-windows.bat
```

**NPM Commands:**
```bash
npm install          # Instalar dependências
npm run dev          # Dev server (web)
npm run build        # Production build
npm run lint         # ESLint
npm run preview      # Preview build
```

**Estrutura:**
```
qrcode-lens-insight/
├── src/
│   ├── App.tsx                    # Main app
│   ├── components/
│   │   ├── QRScanner.tsx          # Scanner principal
│   │   └── ui/                    # shadcn/ui components
│   ├── pages/
│   │   ├── Index.tsx              # Página principal
│   │   └── NotFound.tsx           # 404
│   ├── utils/
│   │   ├── phoneDetection.ts      # Detecção de smartphones
│   │   └── imageProcessing.ts     # CLAHE, ROI extraction
│   └── hooks/                     # Custom React hooks
├── electron/
│   ├── main.cjs                   # Electron main process
│   └── preload.cjs                # IPC bridge
└── release/                       # Built executables
```

**Documentação Completa:**
- `README.md` - Visão geral e quick start
- `SETUP.md` - Guia de setup completo (Windows/Linux)
- `README-ELECTRON.md` - Configuração técnica Electron
- `BUILD-WINDOWS.md` - Build detalhado Windows
- `BUILD-LINUX.md` - Build detalhado Linux/WSL
- `INICIO-RAPIDO.md` - Guia rápido (PT-BR, 3 minutos)

**Integração com Lovable:**
- Projeto Lovable: https://lovable.dev/projects/787c1b64-aba7-4cdc-89ed-bfd55fd8a608
- Mudanças via Lovable são auto-commitadas neste repo
- Sincronização bidirecional (git push/pull)

**Outputs:**
- **Windows:** `release/QR Scanner Professional Setup 1.0.0.exe`
- **Linux:** `release/*.AppImage`, `*.deb`, `*.rpm`
- **Web:** `dist/` (via `npm run build`)

---

### 4. Sistema Recupera Alphaville

**Localização:** `sistema_recupera/`

**Descrição:** Web scraping automation para consulta de funcionários no sistema Recupera Alphaville.

**Funcionalidades:**
- 🤖 Automação Selenium para login e navegação
- 🔍 Busca de funcionários por nome
- 📋 Extração de Divisão e Unidade
- 🛡️ Multi-selector strategy (XPath + CSS) com fallbacks
- 📸 Screenshots automáticos em caso de erro
- 🎭 Anti-detecção: delays aleatórios, user-agent rotation

**Tecnologias:**
- Python 3.6+
- Selenium WebDriver
- ChromeDriver (headless)

**Quick Start:**
```bash
cd sistema_recupera

# Executar scraper
python3 script_alphaville.py
```

**Configuração:**
- **URL:** https://recupera.alphaville.com.br/Recupera/login/login.aspx
- **Login:** adriana.cls / 2099cla (hardcoded)
- **Headless:** Sim (Chrome)

**Anti-Bot Measures:**
- Random delays entre ações
- User-agent rotation
- Multiple selector strategies
- Element visibility checks
- Screenshot debugging

**Arquivos:**
- `script_alphaville.py` - Script principal de scraping

**⚠️ Nota de Segurança:**
Credenciais hardcoded. Recomenda-se migrar para variáveis de ambiente.

---

### 5. Skills do Claude Code

**Localização:** `skills/`

**Descrição:** Habilidades customizadas para o Claude Code CLI.

#### 🐳 `docker-manager/`

**Funcionalidades:**
- ✅ Monitoramento de containers (rodando/parados)
- 🔧 Troubleshooting automático (Exited, Restarting, Unhealthy)
- 🚀 Ações corretivas automáticas
- 📊 Monitoramento de recursos (CPU, memória, rede)
- 🔍 Análise de logs e health checks
- 🛡️ Segurança: nunca remove sem confirmação

**Uso:**
```bash
# Ativar skill (reiniciar Claude Code após instalação)
Claude: "Verifique meus containers Docker"
Claude: "Conserte os containers com problema"
Claude: "Monitore o Docker"

# Ou executar script diretamente
~/.claude/skills/docker-manager/check_containers.sh
```

**Arquivos:**
- `SKILL.md` - Instruções para o Claude
- `check_containers.sh` - Script de verificação
- `README.md` - Documentação de uso

---

#### 🌐 `network-scanner/`

**Funcionalidades:**
- 🌐 Scan de rede local sem sudo (ping sweep + ARP cache)
- 🔧 Suporte opcional: nmap, arp-scan
- 📊 Detecção de IP, MAC, hostname/vendor
- 🚀 Scan paralelo rápido (5-10 segundos)
- 🛡️ Bypass de sudo com capabilities (setcap)

**Uso:**
```bash
# Ativar skill (reiniciar Claude Code após instalação)
Claude: "Escaneie a rede"
Claude: "Mostre os dispositivos conectados"
Claude: "Quais IPs estão na minha rede?"

# Ou executar script diretamente
~/.claude/skills/network-scanner/scan_network.sh

# Bypass sudo para nmap (configuração única)
sudo setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap)
```

**Métodos de Scan (Ordem de Prioridade):**
1. **Ping Sweep + ARP Cache** (padrão, sem sudo)
2. **Nmap sem sudo** (após setcap)
3. **ARP-Scan** (requer sudo)

**Arquivos:**
- `SKILL.md` - Instruções para o Claude
- `scan_network.sh` - Script de scan
- `README.md` - Documentação de uso

---

### 6. Utilitários

#### 📜 `scripts/`

**Descrição:** Scripts utilitários diversos.

**Arquivos:**
- `install-glances-linux.sh` - Instalador do Glances (monitor de sistema)

**Uso:**
```bash
cd scripts
./install-glances-linux.sh
```

---

#### 🔍 `server-audit/` e `server-audit-full/`

**Descrição:** Ferramentas para auditoria de servidores Linux.

**Funcionalidades:**
- 📋 Extração de configurações de sistema
- 🐳 Análise de containers Docker
- 🔒 Auditoria de SSH e firewall
- 📦 Lista de aplicativos instalados
- 🤖 Geração de scripts de provisionamento

**Uso:**
```bash
# Executar auditoria básica
cd server-audit
./audit_script.sh

# Executar auditoria completa
cd server-audit-full
./full_audit.sh
```

**Outputs:**
- Diretórios `system-audit-*` com resultados
- Scripts de provisionamento automatizados
- Relatórios de configuração

---

## ⚡ Início Rápido

### Requisitos Gerais

**Python Projects:**
- Python 3.6+
- Google Chrome/Chromium
- pip3

**QRCode Lens Insight:**
- Node.js 16+ LTS
- npm 7+

**Skills:**
- Claude Code CLI instalado
- Docker (opcional, para docker-manager)
- nmap/arp-scan (opcional, para network-scanner)

### Instalação Rápida por Projeto

**Captura de Câmeras:**
```bash
cd captura_cameras
./install_final.sh
./executar_todas_cameras.sh
```

**Detecção de Anomalias:**
```bash
cd /home/marcelo/sistemas
pip3 install scikit-learn numpy
python3 anomaly_detector_ml.py
```

**Inspeção Visual:**
```bash
cd /home/marcelo/sistemas
./inspecionar problemas
```

**QR Scanner:**
```bash
cd qrcode-lens-insight
./setup-linux.sh        # ou setup-windows.bat
./run-dev-linux.sh      # ou run-dev-windows.bat
```

**Sistema Recupera:**
```bash
cd sistema_recupera
pip3 install selenium chromedriver-autoinstaller
python3 script_alphaville.py
```

**Skills:**
```bash
# Skills já instaladas em ~/.claude/skills/
# Apenas reinicie o Claude Code
```

---

## 📁 Estrutura do Repositório

```
claude_skills/
├── 📁 captura_cameras/              # Sistema de produção (345+ câmeras)
│   ├── camera_downloader_complete.py
│   ├── app.py                       # Dashboard Flask
│   ├── parallel_downloader.py
│   ├── executar_todas_cameras.sh
│   ├── install_final.sh
│   ├── cameras/                     # Output directory
│   └── data/                        # Metadata e cache
├── 📁 captura_cameras_debug/        # Versão debug (servidor HTTP)
│   ├── extrator_simples.py
│   ├── investigador_avancado.py
│   ├── menu_final.sh
│   └── imagens_simples/             # Output directory
├── 📁 qrcode-lens-insight/          # QR Scanner (React/Electron) [submódulo]
│   ├── src/
│   ├── electron/
│   ├── release/
│   └── *.md                         # 6 arquivos de documentação
├── 📁 sistema_recupera/             # Web scraping Alphaville
│   └── script_alphaville.py
├── 📁 skills/                       # Claude Code skills
│   ├── docker-manager/
│   │   ├── check_containers.sh
│   │   ├── SKILL.md
│   │   └── README.md
│   └── network-scanner/
│       ├── scan_network.sh
│       ├── SKILL.md
│       └── README.md
├── 📁 scripts/                      # Utilitários
│   └── install-glances-linux.sh
├── 📁 server-audit/                 # Auditoria de servidores
├── 📁 server-audit-full/            # Auditoria completa
│
├── 🤖 anomaly_detector_ml.py        # Detector ML (Isolation Forest)
├── 🤖 anomaly_detector_cameras.py   # Variante para câmeras
├── 👁️ inspect_cameras_visual.py     # Inspetor visual
├── 📜 inspect_camera.sh             # Inspetor por loja
├── 📜 monitor_anomalies.sh          # Monitor automatizado
├── 📜 inspecionar                   # Wrapper CLI visual
├── 📊 dashboard_cameras.html        # Dashboard HTML
├── 📜 start_dashboard.sh            # Iniciar dashboard
│
├── 📋 README.md                     # ESTE ARQUIVO
├── 📋 CLAUDE.md                     # Documentação completa (680 linhas)
├── 📋 README_ANOMALY_DETECTION.md   # Doc detecção anomalias (456 linhas)
├── 📋 README_INSPECAO_VISUAL.md     # Doc inspeção visual (501 linhas)
├── 📋 ANOMALY_ANALYSIS_REPORT.md    # Relatório de análise (361 linhas)
│
├── 📊 anomaly_detection_report.json # Relatório JSON (anomalias)
├── 📊 visual_camera_report.json     # Relatório JSON (inspeção visual)
├── 📊 camera_analysis_report.json   # Relatório JSON (análise técnica)
│
└── 🔒 .gitignore                    # Ignora arquivos auto-gerados
```

**Total:**
- **9 projetos independentes**
- **~40.000 linhas de código**
- **15+ arquivos de documentação**
- **79 arquivos no commit inicial**

---

## 🛠️ Tecnologias

### Python
- **Selenium** - Automação de navegador
- **Requests** + **BeautifulSoup** - Web scraping e HTTP
- **Flask** - Dashboard web
- **scikit-learn** - Machine learning (Isolation Forest)
- **NumPy** - Computação numérica
- **ChromeDriver** - Controle do Chrome

### JavaScript/TypeScript
- **React 18** - Framework UI
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Electron 28** - Desktop wrapper
- **@zxing/browser** - QR decoding
- **Radix UI** - Component library
- **Tailwind CSS** - Styling
- **TanStack Query** - State management

### DevOps/Shell
- **Bash** - Scripts de automação
- **Docker** - Containerização
- **Git** - Controle de versão (submódulo: qrcode-lens-insight)

### Tools
- **nmap** - Network scanning
- **arp-scan** - ARP discovery
- **jq** - JSON processing
- **Glances** - System monitoring

---

## 🔒 Segurança

### ⚠️ Problemas Identificados

**Credenciais Hardcoded:**

Projetos com credenciais hardcoded no código:

1. **captura_cameras/camera_downloader_complete.py**
   - Login AIVisual: `bk@aiknow.ai`
   - **Linha:** ~50-60

2. **captura_cameras_debug/*.py**
   - Login servidor HTTP: `bk@aiknow.ai / Sphbr7410`
   - **Arquivos:** extrator_simples.py, investigador_avancado.py

3. **sistema_recupera/script_alphaville.py**
   - Login Alphaville: `adriana.cls / 2099cla`
   - **Linha:** ~30-40

### ✅ Recomendações de Segurança

**Migrar para Variáveis de Ambiente:**

1. **Instalar python-dotenv:**
```bash
pip3 install python-dotenv
```

2. **Criar arquivo `.env` (adicionar ao .gitignore):**
```bash
# .env
AIVISUAL_USER=bk@aiknow.ai
AIVISUAL_PASS=your_password_here
ALPHAVILLE_USER=adriana.cls
ALPHAVILLE_PASS=your_password_here
```

3. **Criar `.env.example` (commitar no repo):**
```bash
# .env.example
AIVISUAL_USER=
AIVISUAL_PASS=
ALPHAVILLE_USER=
ALPHAVILLE_PASS=
```

4. **Atualizar scripts Python:**
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega .env
username = os.getenv('AIVISUAL_USER')
password = os.getenv('AIVISUAL_PASS')
```

**Outras Boas Práticas:**
- ✅ Nunca commitar `.env` (adicionar ao `.gitignore`)
- ✅ Usar diferentes credenciais para dev/staging/prod
- ✅ Rotacionar senhas periodicamente
- ✅ Usar secrets managers (AWS Secrets Manager, HashiCorp Vault)
- ✅ Habilitar 2FA quando possível

---

## 📊 Estatísticas do Repositório

**Commits:**
- Total: 4 commits principais
- Primeiro commit: 32.330 adições (79 arquivos)
- Commits de features: 2.331 + 3.676 adições

**Código:**
- Linhas totais: ~40.000+
- Arquivos Python: 30+
- Arquivos TypeScript/React: 20+
- Scripts Shell: 15+
- Documentação Markdown: 15+

**Projetos:**
- Total: 9 projetos independentes
- Python: 6 projetos
- TypeScript/React: 1 projeto
- Bash/Shell: 2 projetos

**Cobertura:**
- Câmeras monitoradas: 345+
- Lojas BK: 115+
- Taxa de sucesso: >95%
- Precisão detecção visual: 99.2%

---

## 📝 Documentação Adicional

### Documentos Principais

- **CLAUDE.md** (680 linhas) - Guia completo para Claude Code
- **README_ANOMALY_DETECTION.md** (456 linhas) - Sistema ML de detecção
- **README_INSPECAO_VISUAL.md** (501 linhas) - Sistema de inspeção visual
- **ANOMALY_ANALYSIS_REPORT.md** (361 linhas) - Relatório de análise

### Documentação por Projeto

**captura_cameras:**
- README.md, GUIA_METADADOS.md, README_DASHBOARD.md
- STATUS_ONLINE.md, COMPARACAO_VERSOES.md
- GUIA_DOWNLOAD_PARALELO.md, VERSOES_DISPONIVEIS.md

**qrcode-lens-insight:**
- README.md, SETUP.md, README-ELECTRON.md
- BUILD-WINDOWS.md, BUILD-LINUX.md, INICIO-RAPIDO.md

**skills:**
- docker-manager/README.md, network-scanner/README.md

---

## 🤝 Contribuindo

Este é um repositório privado de projetos internos. Para modificações:

1. Clone o repositório
2. Crie um branch para features: `git checkout -b feature/nome`
3. Commite suas mudanças: `git commit -m 'feat: descrição'`
4. Push para o branch: `git push origin feature/nome`
5. Abra um Pull Request

**Convenções de Commit:**
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Apenas documentação
- `refactor:` - Refatoração de código
- `test:` - Adição de testes
- `chore:` - Manutenção

---

## 📞 Suporte

Para problemas ou dúvidas:

1. Consulte a documentação do projeto específico (README.md)
2. Verifique CLAUDE.md para guia completo
3. Revise os logs de execução
4. Consulte os relatórios JSON/Markdown gerados

---

## 📜 Licença

Private - Todos os direitos reservados

---

## 🔄 Atualizações Recentes

**2026-01-05:**
- ✨ Criação deste README.md principal
- 📊 Análise completa do histórico de commits
- 📝 Documentação detalhada de todos os 9 projetos
- 🔒 Identificação de problemas de segurança (credenciais hardcoded)

**2025-12-29:**
- ✨ Sistema de inspeção visual com lógica de negócio (commit d4981f8)
- 📊 99.2% de precisão na detecção de problemas
- 🎨 Interface visual com ícones e gráficos ASCII

**2025-12-29:**
- 🤖 Sistema ML de detecção de anomalias (commit 136a940)
- 📈 Isolation Forest com 10+ features
- ⚡ Performance: 3.522 arquivos em ~3 segundos

**2025-12-22:**
- 🎉 Commit inicial do repositório multi-projeto (commit e1fb312)
- 📦 79 arquivos, 32.330 adições
- 🚀 4 projetos principais + 2 skills + utilitários

---

## 🎯 Roadmap

**Melhorias Planejadas:**

### Segurança
- [ ] Migrar todas as credenciais para variáveis de ambiente
- [ ] Adicionar `.env.example` em todos os projetos
- [ ] Implementar rotação automática de senhas

### Testes
- [ ] Adicionar Jest + React Testing Library ao qrcode-lens-insight
- [ ] Adicionar pytest aos projetos Python
- [ ] Configurar CI/CD para testes automatizados

### Monitoramento
- [ ] Computer vision para análise de conteúdo de imagens
- [ ] Predição de falhas de câmeras
- [ ] Dashboard web em tempo real
- [ ] Integração com sistema de tickets

### Features
- [ ] API REST para acesso aos dados
- [ ] Webhooks para alertas (Slack, email, SMS)
- [ ] Mobile app para inspeção remota
- [ ] Análise de tendência temporal

---

**Última atualização:** 2026-01-05
**Versão:** 1.0.0
**Mantido por:** Marcelo Lourenço da Silva
**Repositório:** https://github.com/markanthony91/claude_skills

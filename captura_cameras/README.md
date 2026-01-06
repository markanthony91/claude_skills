# Camera Image Downloader - Production System

> Sistema automatizado para download de imagens de 345+ câmeras em 115+ lojas BK via AIVisual dashboard, com dashboard Flask, sistema de metadados, download paralelo e análise de imagens.

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Status](https://img.shields.io/badge/Status-Production-success.svg)]()

---

## 📋 Índice

- [Quick Start](#-quick-start)
- [Features Principais](#-features-principais)
- [Versões Disponíveis](#-versões-disponíveis)
- [Dashboard Web](#-dashboard-web)
- [Sistema de Metadados](#-sistema-de-metadados)
- [Download Paralelo](#-download-paralelo)
- [Scripts Disponíveis](#-scripts-disponíveis)
- [Documentação Completa](#-documentação-completa)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Configuração](#-configuração)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### Instalação e Primeira Execução

```bash
# 1. Instalar dependências (primeira vez)
./install_final.sh

# 2. Executar download de todas as câmeras (~12-15 minutos)
./executar_todas_cameras.sh

# 3. Iniciar dashboard web para visualização
./start_dashboard.sh
# Acesse: http://localhost:5000
```

### Execuções Rápidas

```bash
# Modo rápido (menos câmeras)
./executar_rapido.sh

# Versão melhorada com mais features
./executar_melhorado.sh

# Com extração de metadados
./executar_com_metadados.sh

# Download paralelo (mais rápido)
./executar_paralelo_com_metadados.sh

# Testar estrutura
./testar_estrutura.sh
```

---

## ✨ Features Principais

### Core Features
- ✅ **345+ câmeras** monitoradas em 115+ lojas BK
- ✅ **Organização automática** por loja e posição (P1/P2/P3)
- ✅ **Login automatizado** no AIVisual dashboard
- ✅ **Progress tracking** com reports detalhados
- ✅ **Rate limiting** (2s delay entre downloads)
- ✅ **Success rate** >95%

### Advanced Features
- 🎨 **Dashboard Web Flask** com visualização interativa
- 📊 **Sistema de metadados** completo (loja, região, status online)
- ⚡ **Download paralelo** com multiprocessing
- 🔍 **Comparação de imagens** entre execuções
- 🧹 **Cleanup automático** de arquivos antigos
- ⚙️ **Gerenciamento de configuração** centralizado
- 📈 **Status online** das câmeras em tempo real
- 🗂️ **Cache de análises** para performance

---

## 📦 Versões Disponíveis

O projeto possui **5 versões** do downloader para diferentes necessidades:

### 1. `camera_downloader_complete.py` (Principal - Recomendado)
**Uso:** Produção padrão
```bash
python3 camera_downloader_complete.py
# ou
./executar_todas_cameras.sh
```

**Features:**
- Download sequencial de 345+ câmeras
- 2s delay entre downloads
- Report detalhado final
- Organização por loja e posição

**Tempo:** ~12-15 minutos

---

### 2. `camera_downloader_main.py` (Versão Melhorada)
**Uso:** Produção com features extras
```bash
python3 camera_downloader_main.py
# ou
./executar_melhorado.sh
```

**Features extras:**
- Todas as features da versão complete
- Logging estruturado
- Retry automático em falhas
- Estatísticas detalhadas por loja
- Validação de imagens baixadas

**Tempo:** ~12-15 minutos

---

### 3. `camera_downloader_com_metadados.py` (Com Metadados)
**Uso:** Produção com extração de metadados
```bash
python3 camera_downloader_com_metadados.py
# ou
./executar_com_metadados.sh
```

**Features extras:**
- Todas as features da versão melhorada
- **Extração de metadados** (loja, região, status, horários)
- **Salva em JSON** (`data/camera_metadata.json`)
- **Análise de disponibilidade** de câmeras
- **Detecção de padrões** de offline

**Tempo:** ~15-18 minutos
**Output:** Imagens + `data/camera_metadata.json`

---

### 4. `parallel_downloader_com_metadados.py` (Paralelo)
**Uso:** Produção HIGH PERFORMANCE
```bash
python3 parallel_downloader_com_metadados.py
# ou
./executar_paralelo_com_metadados.sh
```

**Features extras:**
- **Download paralelo** com multiprocessing
- **4-8 workers** simultâneos
- **3-5x mais rápido** que versão sequencial
- Extração de metadados
- Pool de conexões HTTP
- Progress bar em tempo real

**Tempo:** ~3-5 minutos (vs 12-15 minutos sequencial)
**Recomendado para:** Execuções frequentes, automação

---

### 5. `camera_downloader_parallel.py` (Paralelo Simples)
**Uso:** Download paralelo sem metadados
```bash
python3 camera_downloader_parallel.py
```

**Features:**
- Download paralelo básico
- Sem extração de metadados
- Mais leve e rápido

**Tempo:** ~3-4 minutos

---

## 🎨 Dashboard Web

### Dashboard Flask Interativo

**Iniciar:**
```bash
./start_dashboard.sh
# ou
python3 app.py
```

**Acesse:** http://localhost:5000

### Features do Dashboard

#### Página Principal
- 📊 **Visão geral** de todas as lojas
- 🗺️ **Grid de imagens** das 3 câmeras (P1/P2/P3)
- 🔍 **Busca e filtros** por loja
- 📈 **Estatísticas** em tempo real
- 🎨 **Layout responsivo** de 3 colunas

#### Análise de Lojas
- 📷 **Comparação** entre P1, P2, P3
- 📊 **Tamanho de arquivos** e padrões
- 🕒 **Timestamp** das últimas capturas
- ⚠️ **Alertas** para câmeras offline ou com problemas

#### Metadados
- 🏪 **Informações da loja** (nome, região)
- 📍 **Status online/offline** por câmera
- 🕐 **Horários de funcionamento**
- 📈 **Histórico** de disponibilidade

#### Comparação de Imagens
- 🔄 **Diff visual** entre execuções
- 📊 **Mudanças detectadas**
- 📈 **Timeline** de alterações
- 💾 **Cache** de comparações

### Tecnologias do Dashboard
- **Flask 2.0+** - Framework web
- **Jinja2** - Template engine
- **Bootstrap 5** - UI framework
- **Chart.js** - Gráficos interativos
- **AJAX** - Updates dinâmicos

### Documentação
Ver **README_DASHBOARD.md** para detalhes completos.

---

## 📊 Sistema de Metadados

### Extração Automática

O sistema extrai e armazena metadados completos de cada loja e câmera:

**Executar extração:**
```bash
./extrair_metadados.sh
# ou
python3 extrair_metadados_aivisual.py
```

### Dados Extraídos

**Por Loja:**
- Nome da loja
- Região/Estado
- Endereço
- Horários de funcionamento
- Total de câmeras

**Por Câmera:**
- Posição (P1/P2/P3)
- Status (online/offline)
- URL do feed
- Última captura
- Taxa de disponibilidade (%)
- Padrões de offline (horários, dias)

### Formato de Armazenamento

**Arquivo:** `data/camera_metadata.json`

```json
{
  "generated_at": "2026-01-05T12:00:00",
  "total_stores": 115,
  "total_cameras": 345,
  "stores": [
    {
      "name": "Loja_BK_Central",
      "region": "SP",
      "cameras": {
        "P1": {
          "status": "online",
          "last_capture": "2026-01-05T11:58:00",
          "availability": 98.5,
          "url": "https://..."
        },
        "P2": {...},
        "P3": {...}
      }
    }
  ]
}
```

### Uso dos Metadados

**Copiar metadados P1 para P2/P3:**
```bash
python3 copiar_metadados_p1_para_p2_p3.py
```

**Análise de disponibilidade:**
- Identificar câmeras frequentemente offline
- Detectar padrões (offline em horários específicos)
- Gerar relatórios de SLA
- Alertas proativos

### Documentação
Ver **GUIA_METADADOS.md** e **METADADOS_README.md** para detalhes.

---

## ⚡ Download Paralelo

### Performance Comparison

| Versão | Tempo | Throughput | Recomendado para |
|--------|-------|------------|------------------|
| Sequencial | 12-15 min | ~30 cams/min | Produção estável |
| Paralelo | 3-5 min | ~100 cams/min | **Alta frequência** |

### Configuração

**Editar workers:**
```python
# parallel_downloader_com_metadados.py
NUM_WORKERS = 4  # Padrão: 4-8 workers

# Ajustar conforme CPU/Rede:
# - CPU fraca: 2-4 workers
# - CPU média: 4-6 workers
# - CPU forte: 6-8 workers
```

**Rate limiting por worker:**
```python
DELAY_PER_WORKER = 0.5  # 0.5s delay entre cada worker
```

### Features do Paralelo

- ✅ **Multiprocessing** com pool de workers
- ✅ **Progress bar** em tempo real
- ✅ **Retry automático** em falhas
- ✅ **Pool de conexões HTTP** reutilizável
- ✅ **Graceful shutdown** (Ctrl+C)
- ✅ **Estatísticas** por worker

### Documentação
Ver **GUIA_DOWNLOAD_PARALELO.md** para detalhes.

---

## 📜 Scripts Disponíveis

### Instalação e Setup

| Script | Descrição | Tempo |
|--------|-----------|-------|
| `install_final.sh` | **Instalação completa** de todas as dependências | ~2-3 min |
| `install_vision.sh` | Instalação apenas do dashboard (Flask) | ~1 min |
| `installer.sh` | Instalador básico (dependências core) | ~1 min |
| `installation-ubuntu-22.04.sh` | Instalador específico Ubuntu 22.04 | ~2 min |

### Execução de Downloads

| Script | Versão | Tempo | Features |
|--------|--------|-------|----------|
| `executar_todas_cameras.sh` | **Complete** (Padrão) | 12-15 min | Download básico |
| `executar_rapido.sh` | Complete (Quick) | 5-8 min | Menos câmeras |
| `executar_melhorado.sh` | Main (Melhorado) | 12-15 min | + Logging + Retry |
| `executar_com_metadados.sh` | Metadados | 15-18 min | + Metadados |
| `executar_paralelo_com_metadados.sh` | **Paralelo** (Mais rápido) | 3-5 min | + Paralelo + Metadados |

### Metadados e Análise

| Script | Descrição |
|--------|-----------|
| `extrair_metadados.sh` | Extrair metadados do AIVisual |
| `copiar_metadados_p1_para_p2_p3.py` | Copiar metadados entre câmeras |

### Testes e Validação

| Script | Descrição |
|--------|-----------|
| `testar_estrutura.sh` | Validar estrutura de diretórios |
| `test_estrutura.py` | Testes unitários da estrutura |

### Dashboard

| Script | Descrição |
|--------|-----------|
| `start_dashboard.sh` | Iniciar dashboard Flask |
| `app.py` | Aplicação Flask principal |

### Utilitários

| Script | Descrição |
|--------|-----------|
| `cleanup_manager.py` | Limpeza automática de arquivos antigos |
| `config_manager.py` | Gerenciamento centralizado de configuração |
| `image_comparison.py` | Comparação de imagens entre execuções |

---

## 📚 Documentação Completa

O projeto possui **10 arquivos de documentação** cobrindo todos os aspectos:

### Documentação Principal

| Arquivo | Descrição | Linhas |
|---------|-----------|--------|
| **README.md** | Este arquivo - Visão geral completa | 600+ |
| **CLAUDE.md** | Guia para Claude Code (na raiz do repo) | 680 |

### Guias Específicos

| Arquivo | Foco | Linhas |
|---------|------|--------|
| **README_DASHBOARD.md** | Dashboard Flask completo | 392 |
| **GUIA_METADADOS.md** | Sistema de metadados | 278 |
| **METADADOS_README.md** | Uso de metadados | 328 |
| **GUIA_DOWNLOAD_PARALELO.md** | Download paralelo | 262 |
| **COMPARACAO_VERSOES.md** | Comparação das 5 versões | 213 |
| **VERSOES_DISPONIVEIS.md** | Detalhes de cada versão | 273 |
| **STATUS_ONLINE.md** | Monitoramento de status | 387 |
| **LAYOUT_3_COLUNAS.md** | Layout do dashboard | 306 |
| **MELHORIAS.md** | Roadmap e melhorias futuras | 538 |

**Total:** 3.900+ linhas de documentação

### Como Usar a Documentação

**Para começar:**
1. Leia este **README.md** para visão geral
2. Execute **Quick Start** acima

**Para features específicas:**
- Dashboard → **README_DASHBOARD.md**
- Metadados → **GUIA_METADADOS.md**
- Paralelo → **GUIA_DOWNLOAD_PARALELO.md**
- Comparar versões → **COMPARACAO_VERSOES.md**

**Para troubleshooting:**
- Consulte seção **Troubleshooting** abaixo
- Veja **CLAUDE.md** na raiz do repositório

---

## 📁 Estrutura do Projeto

```
captura_cameras/
├── 📜 Scripts Python (Downloaders)
│   ├── camera_downloader_complete.py      # Versão principal (produção)
│   ├── camera_downloader_main.py          # Versão melhorada
│   ├── camera_downloader_com_metadados.py # Com metadados
│   ├── camera_downloader_parallel.py      # Paralelo simples
│   └── parallel_downloader_com_metadados.py # Paralelo + metadados
│
├── 🎨 Dashboard Flask
│   ├── app.py                             # Aplicação Flask principal
│   ├── static/
│   │   ├── css/style.css                  # Estilos customizados
│   │   └── js/app.js                      # JavaScript interativo
│   └── templates/
│       └── index.html                     # Template principal
│
├── 📊 Sistema de Metadados
│   ├── extrair_metadados_aivisual.py      # Extrator de metadados
│   ├── copiar_metadados_p1_para_p2_p3.py  # Copiar metadados
│   └── data/
│       ├── camera_metadata.json           # Metadados das câmeras
│       └── analysis_cache.json            # Cache de análises
│
├── 🔧 Utilitários
│   ├── cleanup_manager.py                 # Limpeza automática
│   ├── config_manager.py                  # Configuração centralizada
│   ├── image_comparison.py                # Comparação de imagens
│   ├── test_estrutura.py                  # Testes de estrutura
│   └── update_metadata.py                 # Atualizar metadados
│
├── 🚀 Scripts de Execução (.sh)
│   ├── install_final.sh                   # Instalação completa
│   ├── executar_todas_cameras.sh          # Execução padrão
│   ├── executar_rapido.sh                 # Execução rápida
│   ├── executar_melhorado.sh              # Versão melhorada
│   ├── executar_com_metadados.sh          # Com metadados
│   ├── executar_paralelo_com_metadados.sh # Paralelo
│   ├── extrair_metadados.sh               # Extrair metadados
│   ├── testar_estrutura.sh                # Testar estrutura
│   └── start_dashboard.sh                 # Iniciar dashboard
│
├── 📂 Diretórios de Output
│   ├── cameras/                           # Imagens baixadas (principal)
│   ├── cameras_teste/                     # Imagens de teste
│   └── logs/                              # Logs de execução
│
├── 📋 Documentação (10 arquivos .md)
│   ├── README.md                          # Este arquivo
│   ├── README_DASHBOARD.md                # Doc do dashboard
│   ├── GUIA_METADADOS.md                  # Doc de metadados
│   ├── METADADOS_README.md                # Uso de metadados
│   ├── GUIA_DOWNLOAD_PARALELO.md          # Download paralelo
│   ├── COMPARACAO_VERSOES.md              # Comparação de versões
│   ├── VERSOES_DISPONIVEIS.md             # Detalhes das versões
│   ├── STATUS_ONLINE.md                   # Status monitoring
│   ├── LAYOUT_3_COLUNAS.md                # Layout dashboard
│   └── MELHORIAS.md                       # Roadmap
│
└── 📦 Outros
    ├── requirements_dashboard.txt         # Deps do dashboard
    ├── requirements_vision.txt            # Deps de visão computacional
    ├── .camera_config.json                # Configuração de câmeras
    └── .gitignore                         # Arquivos ignorados
```

**Totais:**
- **20+ scripts Python**
- **10+ scripts Shell**
- **10 arquivos de documentação**
- **3.900+ linhas de docs**
- **~15.000 linhas de código**

---

## ⚙️ Configuração

### Credenciais

**⚠️ Security Warning**: Credenciais estão hardcoded em `camera_downloader_complete.py`

**Recomendado:** Migrar para variáveis de ambiente:

1. **Instalar python-dotenv:**
```bash
pip3 install python-dotenv
```

2. **Criar arquivo `.env`:**
```bash
# .env (adicionar ao .gitignore!)
AIVISUAL_USER=bk@aiknow.ai
AIVISUAL_PASS=your_password_here
```

3. **Atualizar script:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
username = os.getenv('AIVISUAL_USER')
password = os.getenv('AIVISUAL_PASS')
```

### Configuração de Câmeras

**Arquivo:** `.camera_config.json`

```json
{
  "delay": 2,
  "timeout": 30,
  "max_retries": 3,
  "parallel_workers": 4,
  "enable_metadata": true,
  "enable_cleanup": true,
  "cleanup_days": 30
}
```

### Dashboard Configuration

**Porta do servidor:**
```python
# app.py
app.run(host='0.0.0.0', port=5000, debug=False)
```

### Cleanup Automático

**Configurar limpeza:**
```python
# cleanup_manager.py
RETENTION_DAYS = 30  # Manter imagens por 30 dias
AUTO_CLEANUP = True  # Habilitar limpeza automática
```

---

## 🛠️ Troubleshooting

### ChromeDriver Issues

**Problema:** "ChromeDriver not found"
```bash
python3 -c "import chromedriver_autoinstaller; chromedriver_autoinstaller.install()"
```

**Problema:** "ChromeDriver version mismatch"
```bash
pip3 install --upgrade chromedriver-autoinstaller
```

### Module Not Found

**Problema:** "ModuleNotFoundError: No module named 'selenium'"
```bash
pip3 install selenium requests beautifulsoup4 chromedriver-autoinstaller
# ou
./install_final.sh
```

### Login Failures

**Possíveis causas:**
1. Credenciais desatualizadas → Verificar em `camera_downloader_complete.py`
2. AIVisual dashboard inacessível → Testar acesso manual
3. Seletores mudaram → Atualizar XPath/CSS selectors no código
4. Captcha/bot detection → Usar delays maiores, rotacionar user-agents

### Download Issues

**Problema:** Downloads muito lentos
- **Normal:** ~2 segundos por câmera (delay intencional)
- **Total:** 345 × 2s ≈ 11-12 minutos
- **Solução:** Usar versão paralela (`executar_paralelo_com_metadados.sh`)

**Problema:** Muitas imagens faltando
```bash
# Verificar logs
cat logs/download_YYYYMMDD.log

# Re-executar apenas câmeras com falha
python3 camera_downloader_main.py --retry-failed
```

### Dashboard Issues

**Problema:** "Address already in use" (porta 5000)
```bash
# Encontrar processo
lsof -i :5000

# Matar processo
lsof -ti:5000 | xargs kill -9

# Ou usar porta diferente
python3 app.py --port 8080
```

**Problema:** Dashboard não mostra imagens
1. Verificar se `cameras/` existe e tem imagens
2. Verificar permissões: `chmod -R 755 cameras/`
3. Verificar logs do Flask no console

### Metadata Issues

**Problema:** Metadados não são extraídos
```bash
# Re-executar extração
./extrair_metadados.sh

# Verificar se arquivo foi criado
ls -lh data/camera_metadata.json
```

**Problema:** JSON corrompido
```bash
# Validar JSON
python3 -m json.tool data/camera_metadata.json

# Fazer backup e recriar
cp data/camera_metadata.json data/camera_metadata.json.bak
rm data/camera_metadata.json
./extrair_metadados.sh
```

### Parallel Download Issues

**Problema:** Alto uso de CPU
```python
# Reduzir workers em parallel_downloader_com_metadados.py
NUM_WORKERS = 2  # Em vez de 4-8
```

**Problema:** Muitos erros de timeout
```python
# Aumentar timeout
TIMEOUT = 60  # Em vez de 30
```

---

## 📊 Performance

### Benchmarks

| Métrica | Valor |
|---------|-------|
| **Câmeras totais** | 345+ |
| **Lojas** | 115+ |
| **Success rate** | >95% |
| **Tempo sequencial** | 12-15 min |
| **Tempo paralelo** | 3-5 min |
| **Throughput sequencial** | ~30 cams/min |
| **Throughput paralelo** | ~100 cams/min |
| **Tamanho médio imagem** | 50-70 KB |
| **Storage por execução** | ~20-25 MB |

### Otimizações

**Para mais velocidade:**
1. Usar versão paralela
2. Aumentar workers (máx 8)
3. Reduzir delay (mín 0.5s)
4. Usar SSD para storage

**Para mais confiabilidade:**
1. Usar versão sequencial
2. Aumentar delay (3-5s)
3. Habilitar retry automático
4. Monitorar logs em tempo real

---

## 🔒 Security Best Practices

1. **✅ Migrar credenciais para .env**
2. **✅ Adicionar .env ao .gitignore**
3. **✅ Usar diferentes credenciais dev/prod**
4. **✅ Rotacionar senhas periodicamente**
5. **✅ Habilitar 2FA no AIVisual**
6. **✅ Limitar acesso ao dashboard (firewall)**
7. **✅ Usar HTTPS para dashboard em produção**
8. **✅ Validar inputs do usuário**

---

## 🎯 Roadmap

Ver **MELHORIAS.md** para roadmap completo (538 linhas).

**Próximas Features:**
- [ ] API REST para acesso aos dados
- [ ] Autenticação no dashboard
- [ ] Alertas em tempo real (Slack/Email)
- [ ] Computer vision para análise de imagens
- [ ] ML para detecção de anomalias
- [ ] Mobile app para monitoramento
- [ ] Backup automático para cloud
- [ ] Integração com sistemas de tickets

---

## 📞 Support

**Para problemas ou dúvidas:**

1. Consulte a **documentação específica** da feature (10 arquivos .md)
2. Verifique **Troubleshooting** acima
3. Revise **logs** em `logs/`
4. Consulte **CLAUDE.md** na raiz do repositório
5. Examine console output para erros específicos

**Logs importantes:**
- `logs/download_YYYYMMDD.log` - Downloads
- `logs/metadata_YYYYMMDD.log` - Metadados
- `logs/dashboard_YYYYMMDD.log` - Dashboard
- `logs/cleanup_YYYYMMDD.log` - Limpeza

---

## 🔗 Related Projects

Este projeto faz parte do repositório multi-projetos. Ver `/home/marcelo/sistemas/README.md` para:

- **captura_cameras_debug** - Versão debug com extração de servidor HTTP
- **Sistema de Detecção de Anomalias (ML)** - Isolation Forest para detectar problemas
- **Sistema de Inspeção Visual** - Análise por contexto de negócio (P1/P2/P3)
- **qrcode-lens-insight** - Scanner QR Code desktop (React/Electron)
- **sistema_recupera** - Web scraping Alphaville
- **Skills Claude Code** - docker-manager, network-scanner

---

## 📜 License

Private - Todos os direitos reservados

---

## 🔄 Changelog

**2026-01-05 - v3.0 - Major Update**
- ✨ README completamente reescrito e expandido
- 📊 Adicionada documentação de todas as 5 versões
- 🎨 Documentação completa do Dashboard Flask
- 📈 Documentação do sistema de metadados
- ⚡ Documentação do download paralelo
- 📚 Índice de toda documentação (10 arquivos)
- 🔧 Troubleshooting expandido
- 📦 Estrutura completa do projeto

**2025-12-27**
- ✨ Dashboard Flask com layout 3 colunas
- 📊 Sistema de metadados completo
- ⚡ Download paralelo com multiprocessing
- 🔍 Comparação de imagens
- 🧹 Cleanup automático

**2025-11-02 - v2.0**
- ✨ Versão melhorada (main)
- 📊 Sistema de metadados inicial
- 📈 Status online das câmeras

**2025-05-29 - v1.0 - Initial Release**
- 🎉 Primeira versão funcional
- 📷 Download de 345+ câmeras
- 📁 Organização automática

---

**Last Updated:** 2026-01-05
**Version:** 3.0.0
**Author:** Marcelo Lourenço da Silva
**Status:** Production

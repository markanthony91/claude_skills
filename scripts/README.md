# Scripts Utilitários

> Coleção de scripts utilitários para instalação e configuração de ferramentas de sistema.

---

## 📋 Índice

- [Scripts Disponíveis](#-scripts-disponíveis)
- [install-glances-linux.sh](#-install-glances-linuxsh)
- [bluetooth-fix.sh](#-bluetooth-fixsh)
- [setup-n8n-docker.sh](#-setup-n8n-dockersh)
- [setup_v4l2loopback_ubuntu2004.sh](#-setup_v4l2loopback_ubuntu2004sh)
- [Requisitos](#-requisitos)
- [Uso](#-uso)
- [Troubleshooting](#-troubleshooting)

---

## 📜 Scripts Disponíveis

| Script | Descrição | Versão | Autor |
|--------|-----------|--------|-------|
| **install-glances-linux.sh** | Instalador completo do Glances com Docker, Prometheus e Tailscale | 2.1 | Mark - Aiknow Systems / BK Brasil |
| **bluetooth-fix.sh** | Diagnóstico e correção de problemas Bluetooth (Realtek RTL8852BE) | 2.0 | Claude AI Assistant |
| **setup-n8n-docker.sh** | Instalador do N8N (automação/workflow) via Docker | 0.236.3 | Autotic |
| **setup_v4l2loopback_ubuntu2004.sh** | Configurador de câmera virtual v4l2loopback para WSL/Ubuntu 20.04 | 1.0 | - |

---

## 🖥️ install-glances-linux.sh

### Descrição

Script automatizado para instalação completa do **Glances** (sistema de monitoramento) em servidores Linux, com suporte a Docker, exportação Prometheus e integração Tailscale.

### O que é o Glances?

**Glances** é uma ferramenta de monitoramento cross-platform escrita em Python que permite:
- 📊 Monitoramento de CPU, memória, disco, rede
- 🐳 Monitoramento de containers Docker
- 📈 Exportação de métricas para Prometheus
- 🌐 Interface web acessível remotamente
- 🔔 Alertas e notificações
- 📱 API REST para integração

### Features do Script

#### ✨ Instalação Automática
- ✅ Detecta distribuição Linux (Ubuntu/Debian/Pop!_OS)
- ✅ Instala Docker e Docker Compose
- ✅ Configura Glances via Docker
- ✅ Habilita exportação Prometheus
- ✅ Integra com Tailscale para acesso seguro
- ✅ Configuração automática de firewall
- ✅ Auto-start no boot

#### 🔧 Componentes Instalados

1. **Docker Engine**
   - Docker CE (Community Edition)
   - Docker Compose v2
   - Configuração de permissões de usuário

2. **Glances Container**
   - Imagem oficial Docker: `nicolargo/glances`
   - Modo privileged para acesso completo ao host
   - Exportação Prometheus habilitada
   - Configuração persistente

3. **Integração Tailscale**
   - Acesso via VPN Tailscale
   - IP estático na VPN
   - Firewall configurado para segurança

4. **Prometheus Exporter**
   - Métricas exportadas na porta 9091
   - Formato compatível com Prometheus
   - Dashboards no Grafana

### Requisitos

#### Sistema Operacional
- Ubuntu 22.04+ LTS
- Debian 11+ (Bullseye)
- Pop!_OS 22.04+

#### Pré-requisitos
- ✅ Acesso root ou sudo
- ✅ **Tailscale instalado e conectado** (obrigatório)
- ✅ Conexão com internet
- ✅ Mínimo 1GB RAM
- ✅ Mínimo 2GB espaço em disco

#### Verificar Tailscale

Antes de executar o script, verifique se o Tailscale está funcionando:

```bash
# Verificar status do Tailscale
tailscale status

# Verificar IP do Tailscale
tailscale ip -4
```

Se não estiver instalado:
```bash
# Instalar Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Conectar à rede
sudo tailscale up
```

---

## 🚀 Uso

### Instalação Básica

```bash
cd /home/marcelo/sistemas/scripts

# Dar permissão de execução (se necessário)
chmod +x install-glances-linux.sh

# Executar com sudo
sudo ./install-glances-linux.sh
```

### Processo de Instalação

O script executará as seguintes etapas:

1. **Verificações Iniciais** (~10 segundos)
   - Verifica se é executado como root/sudo
   - Detecta distribuição Linux
   - Verifica se Tailscale está instalado
   - Obtém IP do Tailscale

2. **Instalação do Docker** (~2-5 minutos)
   - Remove versões antigas do Docker
   - Adiciona repositório oficial Docker
   - Instala Docker CE e Docker Compose
   - Adiciona usuário ao grupo docker
   - Testa instalação do Docker

3. **Configuração do Glances** (~1-2 minutos)
   - Cria diretório de configuração
   - Baixa imagem Docker do Glances
   - Configura container com:
     - Porta web: 61208
     - Porta Prometheus: 9091
     - Modo privileged
     - Auto-restart
   - Inicia container

4. **Configuração do Firewall** (~30 segundos)
   - Configura UFW (se instalado)
   - Permite acesso apenas via Tailscale
   - Bloqueia acesso externo direto

5. **Verificação Final** (~10 segundos)
   - Testa se Glances está rodando
   - Exibe URLs de acesso
   - Mostra status do container

**Tempo Total:** ~5-8 minutos

---

## 📊 Acessando o Glances

### Interface Web

Após a instalação, o Glances estará disponível em:

```
http://<TAILSCALE_IP>:61208
```

**Exemplo:**
```
http://100.64.0.10:61208
```

### Prometheus Metrics

Métricas disponíveis em:

```
http://<TAILSCALE_IP>:9091
```

### Via Docker

Acessar logs do container:
```bash
docker logs glances
```

Acessar shell do container:
```bash
docker exec -it glances bash
```

Reiniciar container:
```bash
docker restart glances
```

Parar container:
```bash
docker stop glances
```

Remover container:
```bash
docker stop glances
docker rm glances
```

---

## 🔧 Configuração Avançada

### Portas Utilizadas

| Serviço | Porta | Protocolo | Acesso |
|---------|-------|-----------|--------|
| **Glances Web** | 61208 | HTTP | Via Tailscale |
| **Prometheus** | 9091 | HTTP | Via Tailscale |
| Docker API | 2375 | TCP | Local apenas |

### Arquivos de Configuração

**Docker Compose:**
```bash
# Geralmente em:
/var/lib/docker/glances/
```

**Glances Config:**
```bash
# Dentro do container em:
/glances/conf/glances.conf
```

### Variáveis de Ambiente

O container Glances é iniciado com:

```bash
docker run -d \
  --name glances \
  --restart=always \
  --privileged \
  -e GLANCES_OPT="-w -e" \
  -p 61208:61208 \
  -p 9091:9091 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /etc/os-release:/etc/os-release:ro \
  nicolargo/glances
```

**Flags:**
- `-w` - Habilita modo web server
- `-e` - Habilita exportação Prometheus
- `--privileged` - Acesso total ao host
- `--restart=always` - Auto-start no boot

---

## 📈 Integração com Prometheus/Grafana

### Prometheus Configuration

Adicione ao seu `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'glances'
    static_configs:
      - targets: ['<TAILSCALE_IP>:9091']
        labels:
          instance: 'servidor-nome'
```

### Métricas Disponíveis

O Glances exporta métricas de:
- `cpu_*` - CPU usage, load average
- `mem_*` - Memory, swap
- `disk_*` - Disk I/O, usage
- `network_*` - Network interfaces
- `docker_*` - Container stats
- `process_*` - Process monitoring

### Dashboards Grafana

Dashboards recomendados:
- **Glances Dashboard** (ID: 5535)
- **Docker Container Dashboard** (ID: 893)

Importar no Grafana:
```
Dashboard → Import → ID: 5535
```

---

## 🛠️ Troubleshooting

### Problema: "Tailscale não está instalado"

**Erro:**
```
❌ ERRO: Tailscale não está instalado!
```

**Solução:**
```bash
# Instalar Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Verificar
tailscale status
```

---

### Problema: "Docker já instalado mas não funciona"

**Erro:**
```
docker: command not found
```

**Solução:**
```bash
# Verificar instalação
which docker

# Reinstalar se necessário
sudo apt remove docker docker-engine docker.io containerd runc
sudo ./install-glances-linux.sh
```

---

### Problema: Container não inicia

**Erro:**
```
Error starting userland proxy
```

**Solução:**
```bash
# Verificar portas em uso
sudo lsof -i :61208
sudo lsof -i :9091

# Matar processos se necessário
sudo lsof -ti:61208 | xargs sudo kill -9

# Reiniciar container
docker restart glances
```

---

### Problema: "Permission denied" ao acessar Docker

**Erro:**
```
Got permission denied while trying to connect to Docker daemon
```

**Solução:**
```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Fazer logout e login novamente
# ou
newgrp docker

# Testar
docker ps
```

---

### Problema: Glances mostra dados incorretos

**Possíveis causas:**
1. Container não está em modo privileged
2. Docker socket não montado corretamente

**Solução:**
```bash
# Recriar container com permissões corretas
docker stop glances
docker rm glances

# Re-executar script
sudo ./install-glances-linux.sh
```

---

### Problema: Não consigo acessar via Tailscale

**Verificações:**
```bash
# 1. Verificar se Tailscale está conectado
tailscale status

# 2. Verificar IP Tailscale
tailscale ip -4

# 3. Verificar container está rodando
docker ps | grep glances

# 4. Verificar portas
sudo netstat -tlnp | grep 61208

# 5. Testar localmente primeiro
curl http://localhost:61208

# 6. Testar via Tailscale
curl http://$(tailscale ip -4):61208
```

---

### Problema: Alto uso de recursos

**Container Glances usando muita CPU/RAM**

**Solução:**
```bash
# Limitar recursos do container
docker update glances \
  --memory="512m" \
  --cpus="0.5"

# Ou recriar com limites
docker stop glances
docker rm glances

docker run -d \
  --name glances \
  --restart=always \
  --privileged \
  --memory="512m" \
  --cpus="0.5" \
  -e GLANCES_OPT="-w -e" \
  -p 61208:61208 \
  -p 9091:9091 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  nicolargo/glances
```

---

## 🔒 Segurança

### Boas Práticas

1. **✅ Acesso apenas via Tailscale**
   - Script configura firewall para bloquear acesso externo
   - Apenas IPs da rede Tailscale podem acessar

2. **✅ Não expor portas publicamente**
   - NUNCA abrir portas 61208 ou 9091 no firewall público
   - Usar apenas via VPN Tailscale

3. **✅ Atualizar regularmente**
   ```bash
   docker pull nicolargo/glances:latest
   docker stop glances
   docker rm glances
   sudo ./install-glances-linux.sh
   ```

4. **✅ Monitorar logs**
   ```bash
   docker logs glances --tail 100 -f
   ```

5. **✅ Backup de configuração**
   ```bash
   docker inspect glances > glances-config-backup.json
   ```

---

## 📊 Performance

### Uso de Recursos

| Recurso | Uso Típico |
|---------|------------|
| **CPU** | 1-3% |
| **RAM** | 50-150 MB |
| **Disco** | ~100 MB (imagem Docker) |
| **Rede** | ~1-5 KB/s |

### Otimizações

**Para reduzir uso de recursos:**
```bash
# Reduzir frequência de refresh (padrão: 2s)
docker update glances --env GLANCES_OPT="-w -e -t 5"
# -t 5 = refresh a cada 5 segundos
```

**Para melhorar performance:**
```bash
# Usar SSD para Docker
# Limitar histórico de métricas
# Desabilitar plugins não usados
```

---

## 🔧 bluetooth-fix.sh

### Descrição

Script de **diagnóstico e correção automatizada** de problemas Bluetooth em Linux (Pop!_OS, Ubuntu e derivados), com suporte especial para adaptadores Realtek RTL8852BE problemáticos no kernel 6.12+.

### Features

- ✅ **Diagnóstico completo** do sistema Bluetooth
- ✅ **Detecção automática** de hardware (USB/PCI)
- ✅ **Verificação de módulos** do kernel (bluetooth, btusb, btintel, btrtl)
- ✅ **Verificação de serviços** systemd
- ✅ **Correção específica Realtek RTL8852BE**
- ✅ **Menu interativo** com múltiplas opções
- ✅ **Interface colorida** com status visual
- ✅ **Reinício automático** de serviços

### Quando Usar

- Bluetooth não funciona após atualização do sistema
- Adaptador Bluetooth não detectado
- Problemas com Realtek RTL8852BE (ID: 0bda:887b)
- Kernel 6.12+ causando problemas
- Serviço bluetooth inativo ou com falhas

### Uso

```bash
cd /home/marcelo/sistemas/scripts

# Executar (NÃO usar sudo!)
./bluetooth-fix.sh
```

**IMPORTANTE:** Execute como usuário normal, não como root!

### Menu de Opções

O script oferece um menu interativo com:

1. **Diagnóstico Completo** - Verifica todo o sistema
2. **Reiniciar Serviço Bluetooth** - Restart rápido
3. **Recarregar Módulos** - Recarrega btusb, bluetooth, etc.
4. **Verificar Logs** - Mostra logs do systemd
5. **Testar Dispositivos** - Lista devices pareados
6. **Reinstalar Bluez** - Reinstala stack Bluetooth
7. **Correção Realtek RTL8852BE** - Fix específico para este adaptador

### Hardware Suportado

- ✅ Adaptadores USB Bluetooth
- ✅ Adaptadores PCI/PCIe Bluetooth
- ✅ Intel Wireless Bluetooth
- ✅ **Realtek RTL8852BE** (com correção específica)
- ✅ Qualcomm Atheros
- ✅ Broadcom

### Troubleshooting

**Problema: Script não executa**
```bash
chmod +x bluetooth-fix.sh
./bluetooth-fix.sh
```

**Problema: "Deve ser executado como usuário normal"**
```bash
# NÃO faça: sudo ./bluetooth-fix.sh
# Correto:
./bluetooth-fix.sh
```

**Problema: Realtek RTL8852BE ainda não funciona**
- Use opção 7 do menu
- Reinicie o sistema após a correção
- Verifique se kernel está atualizado

---

## 🔄 setup-n8n-docker.sh

### Descrição

Instalador automatizado do **N8N** (plataforma de automação/workflow) via Docker. O N8N é uma alternativa open-source ao Zapier/Make.com para criar automações e workflows.

### O que é o N8N?

**N8N** (nodemation) é uma ferramenta de automação que permite:
- 🔗 Conectar 400+ serviços e APIs
- 🤖 Criar workflows visuais (no-code/low-code)
- ⚡ Automações complexas com lógica condicional
- 📊 Integração com webhooks e APIs REST
- 🔧 Processamento de dados e transformações
- 📅 Agendamento de tarefas (cron)

### Features do Script

- ✅ **Instalação automática** do Docker
- ✅ **Atualização** do sistema (apt update/upgrade)
- ✅ **Configuração de timezone** (America/Sao_Paulo)
- ✅ **Container N8N** na porta 5678
- ✅ **Persistência de dados** em ~/.n8n
- ✅ **Auto-restart** habilitado
- ✅ **Versão específica** (0.236.3)

### Uso

```bash
cd /home/marcelo/sistemas/scripts

# Executar instalação
bash setup-n8n-docker.sh
```

### Acesso

Após instalação, acesse:
```
http://<seu-ip>:5678
```

O script mostra a URL automaticamente no final.

### Gerenciar Container

```bash
# Ver status
docker ps | grep n8n

# Ver logs
docker logs n8n

# Parar
docker stop n8n

# Iniciar
docker start n8n

# Reiniciar
docker restart n8n

# Remover
docker stop n8n && docker rm n8n
```

### Dados Persistentes

Todos os workflows e configurações ficam em:
```
~/.n8n/
```

### Recursos da Comunidade

- **Telegram N8N Brasil:** https://t.me/n8nbr
- **WhatsApp:** https://chat.whatsapp.com/EST1hV8aITs33IdS0BoNOY
- **Curso Setup:** https://autotic.com.br/n8n-curso-completo-de-setup
- **Curso Workflows:** https://autotic.com.br/curso-intensivo-de-n8n

### Use Cases

- Automação de marketing (envio de emails, posts sociais)
- Integração entre sistemas (CRM, ERP, e-commerce)
- Processamento de dados (ETL, transformações)
- Notificações e alertas
- Backups automatizados
- Webhooks e APIs

---

## 📹 setup_v4l2loopback_ubuntu2004.sh

### Descrição

Script para configurar **v4l2loopback** (câmera virtual) em Ubuntu 20.04 LTS e WSL2. Permite criar um dispositivo de vídeo virtual que pode ser usado por aplicações como OBS, Zoom, Teams, etc.

### O que é o v4l2loopback?

**v4l2loopback** é um módulo do kernel Linux que cria dispositivos de vídeo virtuais (/dev/videoN). Útil para:
- 🎥 Streaming com OBS para aplicações que precisam de webcam
- 🎬 Captura de tela como fonte de vídeo
- 🎮 Compartilhamento de jogos como webcam
- 💻 Desenvolvimento e testes de aplicações de vídeo
- 🎓 Aulas remotas com múltiplas fontes de vídeo

### Features do Script

- ✅ **Otimizado para Ubuntu 20.04 LTS**
- ✅ **Compatível com WSL2**
- ✅ **Verificação de dependências**
- ✅ **Busca automática** de módulos .ko alternativos
- ✅ **Configuração persistente**
- ✅ **Device em /dev/video10**
- ✅ **Label personalizado**: "WSL Virtual Cam (Ubuntu 20.04)"
- ✅ **Tratamento de erros** robusto

### Uso

```bash
cd /home/marcelo/sistemas/scripts

# Executar com sudo (OBRIGATÓRIO)
sudo ./setup_v4l2loopback_ubuntu2004.sh
```

### Configuração Padrão

```bash
VIDEO_DEVICE=/dev/video10
CARD_LABEL="WSL Virtual Cam (Ubuntu 20.04)"
```

### Verificar Instalação

```bash
# Listar dispositivos de vídeo
ls -la /dev/video*

# Ver informações do device
v4l2-ctl --list-devices

# Testar com ffplay
ffplay /dev/video10
```

### Usar com OBS

1. No OBS, adicione fonte "Câmera Virtual"
2. Selecione "/dev/video10"
3. Configure output para este device
4. Aplicações verão como webcam normal

### Troubleshooting

**Problema: Módulo não carrega**
```bash
# Verificar se módulo existe
modinfo v4l2loopback

# Recompilar DKMS
sudo dkms install v4l2loopback/0.12.7
```

**Problema: /dev/video10 não existe**
```bash
# Carregar módulo manualmente
sudo modprobe v4l2loopback video_nr=10 card_label="Virtual Cam"

# Verificar
ls -la /dev/video10
```

**Problema: "Permission denied"**
```bash
# Adicionar usuário ao grupo video
sudo usermod -aG video $USER

# Fazer logout e login
```

### Compatibilidade

- ✅ Ubuntu 20.04 LTS
- ✅ WSL2 (Windows Subsystem for Linux)
- ⚠️ Outras distros: Pode funcionar mas script é otimizado para Ubuntu 20.04

---

## 🔗 Links Úteis

- **Glances GitHub:** https://github.com/nicolargo/glances
- **Glances Docker Hub:** https://hub.docker.com/r/nicolargo/glances
- **Documentação oficial:** https://glances.readthedocs.io/
- **Tailscale:** https://tailscale.com/
- **Prometheus:** https://prometheus.io/

---

## 📞 Suporte

**Para problemas:**

1. Verificar logs do script durante instalação
2. Verificar logs do container: `docker logs glances`
3. Verificar status: `docker ps -a`
4. Consultar documentação oficial do Glances
5. Verificar conectividade Tailscale

**Logs importantes:**
- Script de instalação: output no terminal
- Docker daemon: `journalctl -u docker`
- Glances container: `docker logs glances`

---

## 📜 Changelog

**Versão 2.1 (Atual)**
- 🐛 Corrigido para docker-compose legado
- ✨ Detecta comando docker-compose automaticamente
- 📝 Melhorias na documentação

**Versão 2.0**
- ✨ Suporte a Docker Compose v2
- 🔒 Integração com Tailscale
- 📊 Exportação Prometheus

**Versão 1.0**
- 🎉 Release inicial
- 🐳 Instalação básica do Glances via Docker

---

## 🔗 Projetos Relacionados

Este script faz parte do repositório multi-projetos. Ver `/home/marcelo/sistemas/README.md` para:

- **server-audit** - Auditoria de servidores Linux
- **skills/docker-manager** - Gerenciamento de containers Docker
- **skills/network-scanner** - Scanner de rede local

---

## 📜 Licença

Private - Todos os direitos reservados
Aiknow Systems / Burger King Brasil

---

**Autor:** Mark - Aiknow Systems / BK Brasil
**Versão:** 2.1
**Última Atualização:** 2026-01-05
**Status:** Production

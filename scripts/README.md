# Scripts Utilitários

> Coleção de scripts utilitários para instalação e configuração de ferramentas de sistema.

---

## 📋 Índice

- [Scripts Disponíveis](#-scripts-disponíveis)
- [install-glances-linux.sh](#-install-glances-linuxsh)
- [Requisitos](#-requisitos)
- [Uso](#-uso)
- [Troubleshooting](#-troubleshooting)

---

## 📜 Scripts Disponíveis

| Script | Descrição | Versão | Autor |
|--------|-----------|--------|-------|
| **install-glances-linux.sh** | Instalador completo do Glances com Docker, Prometheus e Tailscale | 2.1 | Mark - Aiknow Systems / BK Brasil |

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

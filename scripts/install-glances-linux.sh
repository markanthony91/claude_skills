#!/bin/bash
################################################################################
# Script de Instalação do Glances para Servidores Linux
# Autor: Mark - Aiknow Systems / Burger King Brasil
# Versão: 2.1 - Corrigido para docker-compose legado
#
# Instala:
#   - Docker & Docker Compose
#   - Glances (via Docker)
#   - Exportação Prometheus
#   - Integração com Tailscale
#
# Requisitos:
#   - Ubuntu 22.04+ / Debian 11+ / Pop!_OS
#   - Tailscale já instalado e conectado
#   - Acesso root ou sudo
################################################################################

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Funções de log
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_step() {
    echo -e "${MAGENTA}[STEP]${NC} $1"
}

# Função para detectar comando docker-compose
detect_docker_compose_command() {
    # Testar docker compose (plugin nativo - novo)
    if docker compose version &> /dev/null; then
        echo "docker compose"
        return 0
    fi
    
    # Testar docker-compose (standalone - antigo)
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
        return 0
    fi
    
    # Nenhum encontrado
    echo ""
    return 1
}

# Banner
clear
echo -e "${GREEN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        INSTALAÇÃO GLANCES - CLIENTE LINUX                    ║
║        Monitoramento para Burger King Brasil                 ║
║                                                              ║
║        Glances + Prometheus Exporter + Web UI                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"
echo ""

# Verificar root
if [[ $EUID -ne 0 ]]; then
   log_error "Este script deve ser executado como root"
   echo "Execute: sudo bash $0"
   exit 1
fi

################################################################################
# VERIFICAÇÕES INICIAIS
################################################################################

log_step "Verificando pré-requisitos..."
echo ""

# Detectar distribuição
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_NAME=$NAME
    OS_VERSION=$VERSION_ID
    log_info "Sistema Operacional: $OS_NAME $OS_VERSION"
else
    log_error "Não foi possível detectar o sistema operacional"
    exit 1
fi

# Verificar Tailscale
log_info "Verificando Tailscale..."
if ! command -v tailscale &> /dev/null; then
    log_error "Tailscale não está instalado!"
    echo ""
    log_info "Instalando Tailscale..."
    curl -fsSL https://tailscale.com/install.sh | sh
    log_success "Tailscale instalado!"
    log_warning "Execute 'sudo tailscale up' para conectar e depois execute este script novamente"
    exit 0
fi

# Obter IP do Tailscale
TAILSCALE_IP=$(tailscale ip -4 2>/dev/null || echo "")
if [ -z "$TAILSCALE_IP" ]; then
    log_error "Tailscale não está conectado!"
    log_info "Execute: sudo tailscale up"
    exit 1
fi

HOSTNAME=$(hostname)
HOSTNAME_SHORT=$(hostname -s)

log_success "Tailscale conectado!"
log_info "  Hostname: $HOSTNAME"
log_info "  Hostname curto: $HOSTNAME_SHORT"
log_info "  Tailscale IP: $TAILSCALE_IP"

# Detectar se está no WSL
IS_WSL=false
if grep -qEi "(Microsoft|WSL)" /proc/version &> /dev/null; then
    IS_WSL=true
    log_warning "Executando no WSL detectado!"
fi

################################################################################
# COLETAR INFORMAÇÕES DO SERVIDOR
################################################################################

echo ""
log_step "Informações do servidor:"
echo ""

# Tentar extrair store ID do hostname
DEFAULT_STORE_ID="000"
if [[ $HOSTNAME_SHORT =~ bk-.*-([0-9]+) ]]; then
    DEFAULT_STORE_ID="${BASH_REMATCH[1]}"
fi

read -p "Store ID (ex: 001) [$DEFAULT_STORE_ID]: " STORE_ID
STORE_ID=${STORE_ID:-$DEFAULT_STORE_ID}

# Tentar extrair região do hostname
DEFAULT_REGION="sudeste"
if [[ $HOSTNAME_SHORT =~ bk-([a-z]+)- ]]; then
    REGION_CODE="${BASH_REMATCH[1]}"
    case $REGION_CODE in
        sp|rj|mg|es) DEFAULT_REGION="sudeste" ;;
        pr|sc|rs) DEFAULT_REGION="sul" ;;
        ba|se|al|pe|pb|rn|ce|pi|ma) DEFAULT_REGION="nordeste" ;;
        am|pa|ap|rr|ro|ac|to) DEFAULT_REGION="norte" ;;
        go|mt|ms|df) DEFAULT_REGION="centro-oeste" ;;
    esac
fi

read -p "Região (sudeste/sul/nordeste/norte/centro-oeste) [$DEFAULT_REGION]: " REGION
REGION=${REGION:-$DEFAULT_REGION}

read -p "Tipo de servidor (loja/escritorio/datacenter/notebook) [loja]: " SERVER_TYPE
SERVER_TYPE=${SERVER_TYPE:-loja}

# Cidade/localização
read -p "Cidade [${HOSTNAME_SHORT}]: " CITY
CITY=${CITY:-$HOSTNAME_SHORT}

# IP do servidor central Prometheus
read -p "IP Tailscale do servidor central Prometheus [deixe vazio se não souber]: " PROMETHEUS_IP
PROMETHEUS_IP=${PROMETHEUS_IP:-}

################################################################################
# VERIFICAR INSTALAÇÃO EXISTENTE
################################################################################

echo ""
log_step "Verificando instalações existentes..."

GLANCES_EXISTS=false
GLANCES_CONTAINER=""

# Verificar se Glances já está rodando
if command -v docker &> /dev/null; then
    GLANCES_CONTAINER=$(docker ps -a --filter "name=glances" --format "{{.Names}}" 2>/dev/null | head -n 1 || echo "")
    
    if [ ! -z "$GLANCES_CONTAINER" ]; then
        GLANCES_EXISTS=true
        CONTAINER_STATUS=$(docker inspect -f '{{.State.Status}}' "$GLANCES_CONTAINER" 2>/dev/null || echo "unknown")
        
        log_warning "Container Glances existente detectado!"
        log_info "  Container: $GLANCES_CONTAINER"
        log_info "  Status: $CONTAINER_STATUS"
        
        echo ""
        echo "Como deseja proceder?"
        echo ""
        echo "  ${GREEN}1)${NC} Recriar container (recomendado - preserva dados)"
        echo "  ${YELLOW}2)${NC} Manter container existente (cancelar instalação)"
        echo ""
        
        read -p "Escolha [1]: " GLANCES_OPTION
        GLANCES_OPTION=${GLANCES_OPTION:-1}
        
        case $GLANCES_OPTION in
            1)
                log_info "Parando e removendo container existente..."
                docker stop "$GLANCES_CONTAINER" 2>/dev/null || true
                docker rm "$GLANCES_CONTAINER" 2>/dev/null || true
                log_success "Container removido!"
                ;;
            2)
                log_info "Mantendo container existente"
                exit 0
                ;;
            *)
                log_error "Opção inválida"
                exit 1
                ;;
        esac
    fi
fi

# Verificar se porta 61208 está em uso
if ss -tuln 2>/dev/null | grep -q ":61208 " || netstat -tuln 2>/dev/null | grep -q ":61208 "; then
    log_warning "Porta 61208 (Glances Web UI) já está em uso!"
    
    if ! $GLANCES_EXISTS; then
        log_error "Porta ocupada por outro processo. Verifique e libere a porta."
        exit 1
    fi
fi

################################################################################
# CONFIRMAÇÃO
################################################################################

echo ""
log_warning "╔════════════════════════════════════════════════════════════╗"
log_warning "║  RESUMO DA INSTALAÇÃO                                      ║"
log_warning "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "  🏪 Store ID: BK$STORE_ID"
echo "  📍 Região: $REGION"
echo "  🏙️  Cidade: $CITY"
echo "  🖥️  Tipo: $SERVER_TYPE"
echo "  🌐 Tailscale IP: $TAILSCALE_IP"
echo "  💻 Hostname: $HOSTNAME"
if [ "$IS_WSL" = true ]; then
    echo "  ⚠️  Ambiente: WSL (Windows Subsystem for Linux)"
fi
if [ ! -z "$PROMETHEUS_IP" ]; then
    echo "  📊 Prometheus: $PROMETHEUS_IP"
fi
echo ""
echo "  Serviços que serão instalados:"
echo "    ✓ Docker & Docker Compose"
echo "    ✓ Glances (http://$TAILSCALE_IP:61208)"
echo "    ✓ Prometheus Exporter (http://$TAILSCALE_IP:9091)"
echo ""

read -p "Continuar com a instalação? (s/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    log_error "Instalação cancelada"
    exit 1
fi

################################################################################
# INSTALAÇÃO DO DOCKER
################################################################################

echo ""
log_step "Instalando Docker e Docker Compose..."

if command -v docker &> /dev/null; then
    log_success "Docker já instalado!"
    docker --version
else
    log_info "Instalando Docker..."
    
    # Atualizar repositórios
    apt-get update -qq
    
    # Instalar dependências
    apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        software-properties-common \
        apt-transport-https \
        jq \
        wget
    
    # Detectar qual repo usar
    if [[ "$OS_NAME" == *"Pop"* ]] || [[ "$OS_NAME" == *"Pop!_OS"* ]]; then
        # Pop!_OS usa repos do Ubuntu
        UBUNTU_CODENAME="jammy"
        log_info "Detectado Pop!_OS - usando repositórios Ubuntu"
    else
        UBUNTU_CODENAME=$(lsb_release -cs)
    fi
    
    # Adicionar repositório Docker
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $UBUNTU_CODENAME stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Instalar Docker
    apt-get update -qq
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Iniciar e habilitar Docker
    systemctl enable docker
    systemctl start docker
    
    # Adicionar usuário atual ao grupo docker (se não for root)
    if [ "$SUDO_USER" ]; then
        usermod -aG docker $SUDO_USER
        log_info "Usuário $SUDO_USER adicionado ao grupo docker"
    fi
    
    log_success "Docker instalado com sucesso!"
    docker --version
fi

# Detectar comando docker-compose
log_info "Detectando comando docker-compose..."
DOCKER_COMPOSE_CMD=$(detect_docker_compose_command)

if [ -z "$DOCKER_COMPOSE_CMD" ]; then
    log_warning "Nenhuma versão de docker-compose encontrada!"
    log_info "Instalando docker-compose plugin..."
    
    apt-get update -qq
    apt-get install -y docker-compose-plugin
    
    # Tentar detectar novamente
    DOCKER_COMPOSE_CMD=$(detect_docker_compose_command)
    
    if [ -z "$DOCKER_COMPOSE_CMD" ]; then
        # Fallback: instalar versão standalone
        log_info "Instalando docker-compose standalone..."
        curl -SL https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        DOCKER_COMPOSE_CMD="docker-compose"
    fi
fi

log_success "Usando comando: $DOCKER_COMPOSE_CMD"

################################################################################
# CONFIGURAR GLANCES
################################################################################

echo ""
log_step "Configurando Glances..."

GLANCES_DIR="/opt/glances"
mkdir -p $GLANCES_DIR/config

# Criar configuração do Glances
cat > $GLANCES_DIR/config/glances.conf << EOF
# Glances Configuration
# Servidor: $HOSTNAME
# Store: BK$STORE_ID
# Generated: $(date)

[global]
check_update=false
history_size=1200
refresh=3
strftime=%Y-%m-%d %H:%M:%S

[prometheus]
host=0.0.0.0
port=9091
prefix=glances
labels=hostname:$HOSTNAME_SHORT,store_id:BK$STORE_ID,region:$REGION,city:$CITY,type:$SERVER_TYPE,os:linux,tailscale_ip:$TAILSCALE_IP,is_wsl:$IS_WSL

[outputs]
# Web server
web_host=0.0.0.0
web_port=61208

# ==================== MONITORING MODULES ====================

[quicklook]
disable=False

[cpu]
disable=False
user_careful=50
user_warning=70
user_critical=90
system_careful=50
system_warning=70
system_critical=90

[percpu]
disable=False

[mem]
disable=False
careful=50
warning=70
critical=90

[memswap]
disable=False
careful=50
warning=70
critical=90

[load]
disable=False
# Ajustar baseado em número de cores
careful=0.7
warning=1.0
critical=5.0

[network]
disable=False
# Ocultar interfaces virtuais
hide=tailscale0,docker0,lo,veth.*,br-.*,virbr.*

[diskio]
disable=False

[fs]
disable=False
careful=50
warning=70
critical=90
# Ocultar filesystems temporários
hide=/boot.*,/snap.*,/run.*,/dev.*,/sys.*

[folders]
disable=False

[sensors]
disable=False

[hddtemp]
disable=True

[raid]
disable=False

[smart]
disable=False

[processlist]
disable=False
max_processes=50

[processcount]
disable=False

[docker]
disable=False
all=True
max_name_size=20

[ports]
disable=False

[alert]
disable=False

# ==================== PLUGINS ADICIONAIS ====================

[ip]
disable=False
public_ip_disabled=True

[wifi]
disable=True

[gpu]
disable=False

[amps]
disable=False
EOF

log_success "Configuração do Glances criada!"

################################################################################
# CRIAR DOCKER COMPOSE
################################################################################

log_info "Criando docker-compose.yml..."

# Determinar se precisa montar /mnt/c (WSL)
EXTRA_VOLUMES=""
if [ "$IS_WSL" = true ]; then
    EXTRA_VOLUMES="      # Montar discos Windows (WSL)
      - /mnt/c:/rootfs/c:ro
      - /mnt/d:/rootfs/d:ro"
fi

cat > $GLANCES_DIR/docker-compose.yml << EOF
version: '3.8'

# Glances Monitoring - Burger King Brasil
# Servidor: $HOSTNAME
# Store: BK$STORE_ID
# Generated: $(date)

services:
  glances:
    image: nicolargo/glances:latest-full
    container_name: glances
    restart: unless-stopped
    
    # Network e privilégios
    pid: host
    privileged: true
    network_mode: host
    
    # Variáveis de ambiente
    environment:
      - TZ=America/Sao_Paulo
      - GLANCES_OPT=-q --export prometheus --time 10 -w
      - DOCKER_HOST=unix:///var/run/docker.sock
    
    # Volumes
    volumes:
      # Configuração
      - ./config/glances.conf:/glances/conf/glances.conf:ro
      
      # Docker socket para monitorar containers
      - /var/run/docker.sock:/var/run/docker.sock:ro
      
      # Sistema de arquivos (read-only)
      - /:/rootfs:ro
      - /sys:/sys:ro
      - /etc/os-release:/etc/os-release:ro
      - /etc/hostname:/etc/hostname:ro
      - /etc/localtime:/etc/localtime:ro
$EXTRA_VOLUMES
    
    # Labels
    labels:
      - "service=glances"
      - "monitoring=true"
      - "store_id=BK$STORE_ID"
      - "region=$REGION"
      - "com.centurylinklabs.watchtower.enable=true"
    
    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:61208/api/4/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
EOF

log_success "docker-compose.yml criado!"

################################################################################
# AJUSTAR PERMISSÕES
################################################################################

log_info "Ajustando permissões..."

chmod 755 $GLANCES_DIR
chmod 644 $GLANCES_DIR/config/glances.conf
chmod 644 $GLANCES_DIR/docker-compose.yml

log_success "Permissões ajustadas!"

################################################################################
# INICIAR GLANCES
################################################################################

echo ""
log_step "Iniciando Glances..."

cd $GLANCES_DIR

# Pull da imagem
log_info "Baixando imagem do Glances..."
$DOCKER_COMPOSE_CMD pull

# Iniciar container
log_info "Iniciando container..."
$DOCKER_COMPOSE_CMD up -d

# Aguardar inicialização
log_info "Aguardando Glances iniciar (20 segundos)..."
sleep 20

################################################################################
# VERIFICAR STATUS
################################################################################

echo ""
log_step "Verificando status do Glances..."

# Verificar container
CONTAINER_STATUS=$(docker inspect -f '{{.State.Status}}' glances 2>/dev/null || echo "not running")

if [ "$CONTAINER_STATUS" = "running" ]; then
    log_success "Container está rodando!"
else
    log_error "Container NÃO está rodando! Status: $CONTAINER_STATUS"
    echo ""
    log_info "Logs do container:"
    $DOCKER_COMPOSE_CMD logs --tail=50
    exit 1
fi

# Verificar API
echo ""
log_info "Testando endpoints..."

ENDPOINTS_OK=true

# API Status
if curl -sf http://localhost:61208/api/4/status > /dev/null 2>&1; then
    log_success "API Web UI está respondendo (porta 61208)"
else
    log_error "API Web UI NÃO está respondendo"
    ENDPOINTS_OK=false
fi

# Prometheus Exporter
if curl -sf http://localhost:9091/metrics | grep -q "glances"; then
    log_success "Prometheus Exporter está respondendo (porta 9091)"
    
    # Contar métricas
    METRICS_COUNT=$(curl -s http://localhost:9091/metrics | grep -c "^glances_" || echo "0")
    log_info "  Métricas exportadas: $METRICS_COUNT"
else
    log_error "Prometheus Exporter NÃO está respondendo"
    ENDPOINTS_OK=false
fi

################################################################################
# CRIAR SCRIPTS DE GERENCIAMENTO
################################################################################

echo ""
log_step "Criando scripts de gerenciamento..."

# Script principal
cat > /usr/local/bin/glances-manage << EOFSCRIPT
#!/bin/bash
# Script de gerenciamento do Glances - Burger King

GLANCES_DIR="/opt/glances"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Detectar comando docker-compose
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    echo -e "\${RED}Erro: docker-compose não encontrado\${NC}"
    exit 1
fi

show_info() {
    TAILSCALE_IP=\$(tailscale ip -4 2>/dev/null || echo "N/A")
    
    echo -e "\${CYAN}═══════════════════════════════════════════════════\${NC}"
    echo -e "\${GREEN}Glances - Informações do Servidor\${NC}"
    echo -e "\${CYAN}═══════════════════════════════════════════════════\${NC}"
    echo ""
    echo "  Hostname: \$(hostname)"
    echo "  Tailscale IP: \$TAILSCALE_IP"
    echo ""
    echo "  Endpoints:"
    echo "    Web UI:     http://\$TAILSCALE_IP:61208"
    echo "    API:        http://\$TAILSCALE_IP:61208/api/4"
    echo "    Prometheus: http://\$TAILSCALE_IP:9091/metrics"
    echo ""
}

case "\$1" in
    start)
        echo -e "\${GREEN}Iniciando Glances...\${NC}"
        cd \$GLANCES_DIR && \$DOCKER_COMPOSE_CMD up -d
        ;;
    stop)
        echo -e "\${YELLOW}Parando Glances...\${NC}"
        cd \$GLANCES_DIR && \$DOCKER_COMPOSE_CMD down
        ;;
    restart)
        echo -e "\${YELLOW}Reiniciando Glances...\${NC}"
        cd \$GLANCES_DIR && \$DOCKER_COMPOSE_CMD restart
        ;;
    status)
        echo -e "\${GREEN}Status do Glances:\${NC}"
        cd \$GLANCES_DIR && \$DOCKER_COMPOSE_CMD ps
        echo ""
        
        # Testar endpoints
        echo -e "\${GREEN}Testando endpoints:\${NC}"
        if curl -sf http://localhost:61208/api/4/status > /dev/null 2>&1; then
            echo -e "  Web UI:     \${GREEN}✓ OK\${NC}"
        else
            echo -e "  Web UI:     \${RED}✗ DOWN\${NC}"
        fi
        
        if curl -sf http://localhost:9091/metrics > /dev/null 2>&1; then
            echo -e "  Prometheus: \${GREEN}✓ OK\${NC}"
        else
            echo -e "  Prometheus: \${RED}✗ DOWN\${NC}"
        fi
        
        echo ""
        show_info
        ;;
    logs)
        cd \$GLANCES_DIR && \$DOCKER_COMPOSE_CMD logs -f --tail=100
        ;;
    update)
        echo -e "\${GREEN}Atualizando Glances...\${NC}"
        cd \$GLANCES_DIR && \$DOCKER_COMPOSE_CMD pull && \$DOCKER_COMPOSE_CMD up -d
        ;;
    info)
        show_info
        ;;
    config)
        nano \$GLANCES_DIR/config/glances.conf
        echo ""
        echo -e "\${YELLOW}Reinicie o Glances para aplicar mudanças:\${NC}"
        echo "  glances-manage restart"
        ;;
    metrics)
        echo -e "\${GREEN}Métricas do Prometheus:\${NC}"
        curl -s http://localhost:9091/metrics | grep "^glances_" | head -20
        echo ""
        echo "... (mostrando primeiras 20 métricas)"
        echo ""
        TOTAL=\$(curl -s http://localhost:9091/metrics | grep -c "^glances_" || echo "0")
        echo "Total de métricas: \$TOTAL"
        ;;
    test)
        echo -e "\${GREEN}Testando conexão com Prometheus...\${NC}"
        
        if [ -z "\$2" ]; then
            echo "Uso: glances-manage test <prometheus_ip>"
            echo "Exemplo: glances-manage test 100.64.0.100"
            exit 1
        fi
        
        PROM_IP=\$2
        echo "Testando: http://\$PROM_IP:9090"
        
        if curl -sf "http://\$PROM_IP:9090/-/healthy" > /dev/null 2>&1; then
            echo -e "\${GREEN}✓ Prometheus está acessível!\${NC}"
            
            # Verificar se este servidor está sendo monitorado
            HOSTNAME=\$(hostname -s)
            RESULT=\$(curl -s "http://\$PROM_IP:9090/api/v1/query?query=up{hostname=\\"\$HOSTNAME\\"}" | jq -r '.data.result[0].value[1]' 2>/dev/null || echo "0")
            
            if [ "\$RESULT" = "1" ]; then
                echo -e "\${GREEN}✓ Este servidor está sendo monitorado pelo Prometheus!\${NC}"
            else
                echo -e "\${YELLOW}⚠ Este servidor NÃO está sendo monitorado ainda\${NC}"
                echo ""
                echo "Adicione ao prometheus.yml do servidor central:"
                echo ""
                TAILSCALE_IP=\$(tailscale ip -4 2>/dev/null || echo "TAILSCALE_IP")
                echo "  - targets: ['\$TAILSCALE_IP:9091']"
                echo "    labels:"
                echo "      hostname: '\$HOSTNAME'"
            fi
        else
            echo -e "\${RED}✗ Não foi possível acessar o Prometheus\${NC}"
        fi
        ;;
    *)
        echo "Uso: glances-manage {start|stop|restart|status|logs|update|info|config|metrics|test}"
        echo ""
        echo "Comandos:"
        echo "  start    - Iniciar Glances"
        echo "  stop     - Parar Glances"
        echo "  restart  - Reiniciar Glances"
        echo "  status   - Ver status e testar endpoints"
        echo "  logs     - Ver logs em tempo real"
        echo "  update   - Atualizar imagem do Glances"
        echo "  info     - Mostrar informações e endpoints"
        echo "  config   - Editar configuração"
        echo "  metrics  - Ver métricas exportadas"
        echo "  test     - Testar conexão com Prometheus"
        exit 1
        ;;
esac
EOFSCRIPT

chmod +x /usr/local/bin/glances-manage

log_success "Script de gerenciamento criado!"

# Criar atalho
cat > /usr/local/bin/glances << 'EOF'
#!/bin/bash
glances-manage "$@"
EOF
chmod +x /usr/local/bin/glances

################################################################################
# CRIAR ARQUIVO DE INFORMAÇÕES
################################################################################

cat > $GLANCES_DIR/INFO.txt << EOF
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        GLANCES - INFORMAÇÕES DO SERVIDOR                     ║
║        Burger King Brasil                                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Instalação: $(date)

═════════════════════════════════════════════════════════════

📋 INFORMAÇÕES DO SERVIDOR

Hostname: $HOSTNAME
Store ID: BK$STORE_ID
Região: $REGION
Cidade: $CITY
Tipo: $SERVER_TYPE
Tailscale IP: $TAILSCALE_IP
Sistema: $OS_NAME $OS_VERSION
WSL: $IS_WSL
Docker Compose: $DOCKER_COMPOSE_CMD

═════════════════════════════════════════════════════════════

🌐 ENDPOINTS

Web UI:
  http://$TAILSCALE_IP:61208
  
API:
  http://$TAILSCALE_IP:61208/api/4
  
Prometheus Exporter:
  http://$TAILSCALE_IP:9091/metrics

═════════════════════════════════════════════════════════════

🛠️  COMANDOS DE GERENCIAMENTO

Ver status:         glances-manage status
Ver logs:           glances-manage logs
Reiniciar:          glances-manage restart
Parar:              glances-manage stop
Iniciar:            glances-manage start
Atualizar:          glances-manage update
Ver informações:    glances-manage info
Editar config:      glances-manage config
Ver métricas:       glances-manage metrics
Testar Prometheus:  glances-manage test $PROMETHEUS_IP

═════════════════════════════════════════════════════════════

📝 ADICIONAR AO PROMETHEUS (SERVIDOR CENTRAL)

Edite: /opt/monitoring/prometheus/config/prometheus.yml

Adicione:

  - targets: ['$TAILSCALE_IP:9091']
    labels:
      hostname: '$HOSTNAME_SHORT'
      store_id: 'BK$STORE_ID'
      region: '$REGION'
      city: '$CITY'
      type: '$SERVER_TYPE'
      os: 'linux'

Depois recarregue:
  monitoring reload-prometheus

═════════════════════════════════════════════════════════════
EOF

chmod 600 $GLANCES_DIR/INFO.txt

################################################################################
# RESUMO FINAL
################################################################################

clear
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║        INSTALAÇÃO CONCLUÍDA COM SUCESSO! ✅                 ║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

log_success "Glances instalado e funcionando!"
echo ""

echo -e "${CYAN}📊 INFORMAÇÕES DO SERVIDOR:${NC}"
echo ""
echo "  🏪 Store: BK$STORE_ID"
echo "  📍 Região: $REGION ($CITY)"
echo "  💻 Hostname: $HOSTNAME"
echo "  🌐 Tailscale IP: $TAILSCALE_IP"
echo ""

echo -e "${CYAN}🌐 ENDPOINTS:${NC}"
echo ""
echo -e "  ${GREEN}Web UI:${NC}     http://$TAILSCALE_IP:61208"
echo -e "  ${GREEN}API:${NC}        http://$TAILSCALE_IP:61208/api/4"
echo -e "  ${GREEN}Prometheus:${NC} http://$TAILSCALE_IP:9091/metrics"
echo ""

echo -e "${CYAN}🛠️  COMANDOS RÁPIDOS:${NC}"
echo ""
echo "  glances-manage status       # Ver status"
echo "  glances-manage logs         # Ver logs"
echo "  glances-manage restart      # Reiniciar"
echo "  glances-manage info         # Informações completas"
if [ ! -z "$PROMETHEUS_IP" ]; then
    echo "  glances-manage test $PROMETHEUS_IP  # Testar Prometheus"
fi
echo ""

echo -e "${YELLOW}📝 PRÓXIMO PASSO:${NC}"
echo ""
echo "  Adicione este servidor ao Prometheus (servidor central):"
echo ""
echo "  No servidor $PROMETHEUS_IP, edite:"
echo "    /opt/monitoring/prometheus/config/prometheus.yml"
echo ""
echo "  Adicione na seção 'glances-linux':"
echo ""
echo "    - targets: ['$TAILSCALE_IP:9091']"
echo "      labels:"
echo "        hostname: '$HOSTNAME_SHORT'"
echo "        store_id: 'BK$STORE_ID'"
echo "        region: '$REGION'"
echo "        city: '$CITY'"
echo "        type: '$SERVER_TYPE'"
echo "        os: 'linux'"
echo ""
echo "  Depois recarregue: monitoring reload-prometheus"
echo ""

if [ "$ENDPOINTS_OK" = true ]; then
    log_success "Todos os endpoints estão funcionando! 🎉"
else
    log_warning "Alguns endpoints não responderam. Execute:"
    echo "  glances-manage logs"
fi

echo ""
log_info "Instalação finalizada!"
echo ""

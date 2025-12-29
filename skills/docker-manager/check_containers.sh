#!/bin/bash

# Docker Manager Script
# Verifica e gerencia containers Docker com troubleshooting automático

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          DOCKER MANAGER - Gerenciamento de Containers         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Contadores
TOTAL_CONTAINERS=0
RUNNING_CONTAINERS=0
STOPPED_CONTAINERS=0
PROBLEM_CONTAINERS=0
FIXED_CONTAINERS=0
ACTIONS_TAKEN=()

# Verificar se Docker está instalado e rodando
check_docker() {
    echo -e "${BLUE}[*] Verificando Docker...${NC}"

    if ! command -v docker &> /dev/null; then
        echo -e "${RED}[✗] Docker não está instalado!${NC}"
        echo -e "${YELLOW}[!] Instale com: sudo apt install docker.io${NC}"
        exit 1
    fi

    echo -e "${GREEN}[✓] Docker instalado${NC}"

    # Verificar se está rodando
    if ! docker ps &> /dev/null; then
        echo -e "${RED}[✗] Docker daemon não está rodando!${NC}"
        echo -e "${YELLOW}[!] Tentando iniciar...${NC}"
        sudo systemctl start docker
        sleep 2
        if docker ps &> /dev/null; then
            echo -e "${GREEN}[✓] Docker iniciado com sucesso${NC}"
        else
            echo -e "${RED}[✗] Falha ao iniciar Docker${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}[✓] Docker daemon ativo${NC}"
    fi

    # Mostrar versão
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
    echo -e "${GREEN}[✓] Versão: $DOCKER_VERSION${NC}"
    echo ""
}

# Listar todos os containers
list_containers() {
    echo -e "${BLUE}[*] Listando containers...${NC}"
    echo ""

    # Contar containers
    TOTAL_CONTAINERS=$(docker ps -a --format "{{.ID}}" | wc -l)
    RUNNING_CONTAINERS=$(docker ps --format "{{.ID}}" | wc -l)
    STOPPED_CONTAINERS=$((TOTAL_CONTAINERS - RUNNING_CONTAINERS))

    if [ $TOTAL_CONTAINERS -eq 0 ]; then
        echo -e "${YELLOW}[!] Nenhum container encontrado${NC}"
        echo ""
        return
    fi

    # Mostrar tabela
    printf "%-12s %-20s %-20s %-25s %-15s\n" "ID" "Nome" "Status" "Imagem" "Portas"
    echo "────────────────────────────────────────────────────────────────────────────────────────────────"

    docker ps -a --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}\t{{.Ports}}" | tail -n +2 | while read line; do
        ID=$(echo $line | awk '{print $1}')
        NAME=$(echo $line | awk '{print $2}')
        STATUS=$(echo $line | awk '{print $3" "$4" "$5}')
        IMAGE=$(echo $line | awk '{print $6}')
        PORTS=$(echo $line | awk '{print $7}')

        printf "%-12s %-20s %-20s %-25s %-15s\n" "$ID" "$NAME" "$STATUS" "$IMAGE" "$PORTS"
    done

    echo ""
}

# Analisar e troubleshoot containers com problemas
troubleshoot_containers() {
    echo -e "${BLUE}[*] Analisando containers para problemas...${NC}"
    echo ""

    # Containers parados (Exited)
    EXITED_CONTAINERS=$(docker ps -a --filter "status=exited" --format "{{.Names}}")

    if [ -n "$EXITED_CONTAINERS" ]; then
        echo -e "${YELLOW}[!] Containers parados encontrados:${NC}"
        for container in $EXITED_CONTAINERS; do
            echo -e "${YELLOW}    • $container${NC}"
            PROBLEM_CONTAINERS=$((PROBLEM_CONTAINERS + 1))
        done
        echo ""

        # Tentar iniciar cada container parado
        for container in $EXITED_CONTAINERS; do
            echo -e "${BLUE}[*] Analisando: $container${NC}"

            # Verificar logs
            echo -e "${BLUE}    ├─ Verificando logs...${NC}"
            LAST_ERROR=$(docker logs --tail 5 $container 2>&1 | tail -1)
            if [ -n "$LAST_ERROR" ]; then
                echo -e "${YELLOW}    ├─ Último log: ${LAST_ERROR:0:60}...${NC}"
            fi

            # Verificar código de saída
            EXIT_CODE=$(docker inspect $container --format='{{.State.ExitCode}}')
            echo -e "${BLUE}    ├─ Código de saída: $EXIT_CODE${NC}"

            # Tentar iniciar
            echo -e "${BLUE}    ├─ Tentando iniciar...${NC}"
            if docker start $container &> /dev/null; then
                sleep 2
                # Verificar se ainda está rodando
                if docker ps --filter "name=$container" --format "{{.Names}}" | grep -q "$container"; then
                    echo -e "${GREEN}    └─ ✓ Iniciado com sucesso!${NC}"
                    FIXED_CONTAINERS=$((FIXED_CONTAINERS + 1))
                    ACTIONS_TAKEN+=("Iniciado: $container")
                else
                    echo -e "${RED}    └─ ✗ Container parou imediatamente após iniciar${NC}"
                    echo -e "${YELLOW}       Verifique os logs: docker logs $container${NC}"
                    ACTIONS_TAKEN+=("Falha ao iniciar: $container")
                fi
            else
                echo -e "${RED}    └─ ✗ Falha ao iniciar${NC}"
                ACTIONS_TAKEN+=("Falha ao iniciar: $container")
            fi
            echo ""
        done
    fi

    # Containers em restart contínuo
    RESTARTING_CONTAINERS=$(docker ps -a --filter "status=restarting" --format "{{.Names}}")

    if [ -n "$RESTARTING_CONTAINERS" ]; then
        echo -e "${RED}[!] Containers em crash loop encontrados:${NC}"
        for container in $RESTARTING_CONTAINERS; do
            echo -e "${RED}    • $container${NC}"
            PROBLEM_CONTAINERS=$((PROBLEM_CONTAINERS + 1))
        done
        echo ""

        for container in $RESTARTING_CONTAINERS; do
            echo -e "${BLUE}[*] Analisando crash loop: $container${NC}"
            echo -e "${BLUE}    ├─ Últimos logs:${NC}"
            docker logs --tail 10 $container 2>&1 | sed 's/^/    │  /'
            echo -e "${YELLOW}    ├─ Recomendação: Parar e analisar manualmente${NC}"
            echo -e "${YELLOW}    └─ Comando: docker stop $container && docker logs $container${NC}"
            ACTIONS_TAKEN+=("Detectado crash loop: $container")
            echo ""
        done
    fi

    # Verificar containers unhealthy
    UNHEALTHY_CONTAINERS=$(docker ps --filter "health=unhealthy" --format "{{.Names}}")

    if [ -n "$UNHEALTHY_CONTAINERS" ]; then
        echo -e "${YELLOW}[!] Containers com health check failed:${NC}"
        for container in $UNHEALTHY_CONTAINERS; do
            echo -e "${YELLOW}    • $container${NC}"
            PROBLEM_CONTAINERS=$((PROBLEM_CONTAINERS + 1))
        done
        echo ""

        for container in $UNHEALTHY_CONTAINERS; do
            echo -e "${BLUE}[*] Tentando resolver: $container${NC}"
            echo -e "${BLUE}    ├─ Reiniciando container...${NC}"
            if docker restart $container &> /dev/null; then
                echo -e "${GREEN}    └─ ✓ Reiniciado${NC}"
                FIXED_CONTAINERS=$((FIXED_CONTAINERS + 1))
                ACTIONS_TAKEN+=("Reiniciado (unhealthy): $container")
            else
                echo -e "${RED}    └─ ✗ Falha ao reiniciar${NC}"
                ACTIONS_TAKEN+=("Falha ao reiniciar: $container")
            fi
            echo ""
        done
    fi
}

# Verificar uso de recursos
check_resources() {
    echo -e "${BLUE}[*] Verificando uso de recursos...${NC}"
    echo ""

    if [ $RUNNING_CONTAINERS -eq 0 ]; then
        echo -e "${YELLOW}[!] Nenhum container rodando${NC}"
        echo ""
        return
    fi

    printf "%-20s %-15s %-15s %-15s %-15s\n" "Container" "CPU %" "Memória" "Mem %" "NET I/O"
    echo "────────────────────────────────────────────────────────────────────────────────"

    docker stats --no-stream --format "{{.Name}}	{{.CPUPerc}}	{{.MemPerc}}	{{.NetIO}}" 2>/dev/null

    echo ""
}

# Verificar dependências (redes, volumes)
check_dependencies() {
    echo -e "${BLUE}[*] Verificando dependências...${NC}"
    echo ""

    # Redes
    NETWORKS_COUNT=$(docker network ls --format "{{.Name}}" | grep -v "bridge\|host\|none" | wc -l)
    echo -e "${GREEN}[✓] Redes customizadas: $NETWORKS_COUNT${NC}"

    # Volumes
    VOLUMES_COUNT=$(docker volume ls --format "{{.Name}}" | wc -l)
    echo -e "${GREEN}[✓] Volumes: $VOLUMES_COUNT${NC}"

    echo ""
}

# Mostrar resumo final
show_summary() {
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                      RESUMO FINAL                              ║"
    echo "╚════════════════════════════════════════════════════════════════╝"

    echo -e "${GREEN}[✓] Total de containers: $TOTAL_CONTAINERS${NC}"
    echo -e "${GREEN}[✓] Containers rodando: $RUNNING_CONTAINERS${NC}"

    if [ $STOPPED_CONTAINERS -gt 0 ]; then
        echo -e "${YELLOW}[!] Containers parados: $STOPPED_CONTAINERS${NC}"
    fi

    if [ $PROBLEM_CONTAINERS -gt 0 ]; then
        echo -e "${RED}[!] Containers com problemas detectados: $PROBLEM_CONTAINERS${NC}"
    fi

    if [ $FIXED_CONTAINERS -gt 0 ]; then
        echo -e "${GREEN}[✓] Containers corrigidos: $FIXED_CONTAINERS${NC}"
    fi

    echo ""

    if [ ${#ACTIONS_TAKEN[@]} -gt 0 ]; then
        echo -e "${BLUE}📋 Ações executadas:${NC}"
        for action in "${ACTIONS_TAKEN[@]}"; do
            echo -e "${BLUE}   • $action${NC}"
        done
        echo ""
    fi

    # Sugestões
    echo -e "${BLUE}💡 Próximos passos sugeridos:${NC}"
    echo "   • Ver logs de um container: docker logs <nome>"
    echo "   • Executar comando em container: docker exec -it <nome> /bin/bash"
    echo "   • Reiniciar container: docker restart <nome>"
    echo "   • Ver recursos em tempo real: docker stats"
    echo ""

    # Status final
    if [ $PROBLEM_CONTAINERS -eq 0 ]; then
        echo -e "${GREEN}✅ Todos os containers estão funcionando corretamente!${NC}"
    elif [ $FIXED_CONTAINERS -eq $PROBLEM_CONTAINERS ]; then
        echo -e "${GREEN}✅ Todos os problemas foram resolvidos!${NC}"
    else
        echo -e "${YELLOW}⚠️  Alguns containers ainda precisam de atenção manual${NC}"
    fi
    echo ""
}

# Main
check_docker
list_containers
troubleshoot_containers
check_resources
check_dependencies
show_summary

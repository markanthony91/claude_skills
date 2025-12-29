#!/bin/bash

# Network Scanner Script
# Escaneia a rede local e mostra dispositivos conectados

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          NETWORK SCANNER - Varredura de Rede Local            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para detectar a rede local
detect_network() {
    echo -e "${BLUE}[*] Detectando configuração de rede...${NC}"

    # Pegar o IP e subnet da interface padrão
    INTERFACE=$(ip route | grep default | awk '{print $5}' | head -n1)
    LOCAL_IP=$(ip -4 addr show $INTERFACE | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
    SUBNET=$(ip -4 addr show $INTERFACE | grep -oP '(?<=inet\s)\d+(\.\d+){3}/\d+')

    echo -e "${GREEN}[✓] Interface: $INTERFACE${NC}"
    echo -e "${GREEN}[✓] IP Local: $LOCAL_IP${NC}"
    echo -e "${GREEN}[✓] Subnet: $SUBNET${NC}"
    echo ""
}

# Função para verificar ferramentas
check_tools() {
    echo -e "${BLUE}[*] Verificando ferramentas disponíveis...${NC}"

    NMAP_AVAILABLE=false
    ARP_SCAN_AVAILABLE=false

    if command -v nmap &> /dev/null; then
        echo -e "${GREEN}[✓] nmap: disponível${NC}"
        NMAP_AVAILABLE=true
    else
        echo -e "${YELLOW}[!] nmap: não instalado${NC}"
    fi

    if command -v arp-scan &> /dev/null; then
        echo -e "${GREEN}[✓] arp-scan: disponível${NC}"
        ARP_SCAN_AVAILABLE=true
    else
        echo -e "${YELLOW}[!] arp-scan: não instalado${NC}"
    fi

    echo ""
}

# Função para escanear com arp-scan
scan_with_arp() {
    echo -e "${BLUE}[*] Escaneando com arp-scan...${NC}"
    echo ""

    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}[!] Este método requer sudo. Execute: sudo $0${NC}"
        return 1
    fi

    arp-scan --localnet --interface=$INTERFACE | grep -v "^Interface\|^Starting\|^Ending\|^$"
    echo ""
}

# Função para escanear com nmap
scan_with_nmap() {
    echo -e "${BLUE}[*] Escaneando com nmap...${NC}"
    echo ""

    if [ "$EUID" -ne 0 ]; then
        echo -e "${YELLOW}[!] Para melhores resultados, execute com sudo${NC}"
    fi

    nmap -sn $SUBNET
    echo ""
}

# Função para escanear com métodos básicos (sem ferramentas extras)
scan_basic() {
    echo -e "${BLUE}[*] Método sem sudo (Ping Sweep + ARP Cache)${NC}"
    echo ""

    # Extrair network base
    NETWORK_BASE=$(echo $SUBNET | cut -d'/' -f1 | cut -d'.' -f1-3)

    echo -e "${YELLOW}[*] Ping sweep em $NETWORK_BASE.0/24 (leva ~5 segundos)${NC}"

    # Ping sweep silencioso e rápido
    for i in {1..254}; do
        ping -c 1 -W 1 $NETWORK_BASE.$i &> /dev/null &
    done
    wait

    echo -e "${GREEN}[✓] Ping sweep completo!${NC}"
    echo ""
    echo -e "${BLUE}[*] Dispositivos encontrados:${NC}"
    echo ""

    # Mostrar cache ARP formatado (apenas dispositivos com MAC válido)
    printf "%-16s %-20s %-12s\n" "IP Address" "MAC Address" "Status"
    echo "────────────────────────────────────────────────────────"

    ip neigh show | grep -v FAILED | grep -v INCOMPLETE | while read line; do
        IP=$(echo $line | awk '{print $1}')
        MAC=$(echo $line | awk '{print $5}')
        STATE=$(echo $line | awk '{print $NF}')
        # Apenas mostrar se tiver MAC address (não IPv6 sem escopo)
        if [[ $MAC =~ ^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$ ]]; then
            printf "%-16s %-20s %-12s\n" "$IP" "$MAC" "$STATE"
        fi
    done

    echo ""
}

# Main
detect_network
check_tools

# SEMPRE usar método básico primeiro (sem sudo)
echo -e "${GREEN}[✓] Usando método sem sudo (Ping Sweep + ARP)${NC}"
scan_basic

# Se tiver nmap E for root, fazer scan adicional
if [ "$NMAP_AVAILABLE" = true ] && [ "$EUID" -eq 0 ]; then
    echo -e "${BLUE}[*] Executando scan adicional com nmap...${NC}"
    scan_with_nmap
fi

# Estatísticas finais
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                      RESUMO DO SCAN                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
DEVICE_COUNT=$(ip neigh show | grep -v FAILED | grep -v INCOMPLETE | grep -E '([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}' | wc -l)
echo -e "${GREEN}[✓] Total de dispositivos encontrados: $DEVICE_COUNT${NC}"
echo -e "${GREEN}[✓] Timestamp: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${GREEN}[✓] Interface: $INTERFACE${NC}"
echo -e "${GREEN}[✓] Subnet: $SUBNET${NC}"
echo ""

# Sugestões
echo -e "${BLUE}💡 Próximos passos sugeridos:${NC}"
echo "   • Para scan detalhado de um IP: nmap -sV <IP>"
echo "   • Para ver portas abertas: nmap -p- <IP>"
echo "   • Para monitoramento: watch -n 30 'bash $0'"
echo ""

# Dica sobre bypass do sudo no nmap
if [ "$NMAP_AVAILABLE" = true ]; then
    echo -e "${YELLOW}🔓 Bypass do sudo para nmap (configuração única):${NC}"
    echo "   sudo setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip \$(which nmap)"
    echo "   Depois disso, nmap funciona sem sudo!"
    echo ""
fi

# Nota sobre instalação de ferramentas
if [ "$NMAP_AVAILABLE" = false ] || [ "$ARP_SCAN_AVAILABLE" = false ]; then
    echo -e "${YELLOW}📦 Para instalar as ferramentas completas:${NC}"
    echo "   Ubuntu/Debian: sudo apt install nmap arp-scan"
    echo "   Fedora/RHEL:   sudo dnf install nmap arp-scan"
    echo "   Arch:          sudo pacman -S nmap arp-scan"
    echo ""
fi

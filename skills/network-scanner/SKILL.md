---
name: network-scanner
description: Escaneia a rede local para descobrir dispositivos conectados e seus IPs, MACs e hostnames. Use quando o usuário pedir para varrer a rede, mostrar dispositivos conectados, listar IPs na rede, ou descobrir quem está conectado.
allowed-tools: Bash, Read, Write
---

# Network Scanner - Varredura de Rede

Esta skill ajuda a escanear a rede local e identificar todos os dispositivos conectados, mostrando seus endereços IP, endereços MAC e nomes de host quando disponíveis.

## Instruções

Quando esta skill for ativada, siga estes passos:

### 1. Identificar a Interface de Rede e Subnet

Primeiro, descubra a interface de rede ativa e o range de IPs da rede local:

```bash
ip route | grep default
ip addr show
```

Ou de forma mais direta:
```bash
ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}/\d+'
```

### 2. Métodos de Escaneamento

**IMPORTANTE: PRIORIZE MÉTODOS SEM SUDO!** Use esta ordem de preferência:

#### Método 1: Ping Sweep + ARP (RECOMENDADO - sem sudo)
Este é o método principal que deve ser usado sempre. Não requer permissões especiais:

```bash
# Descobrir a subnet
SUBNET=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v 127.0.0.1 | head -n1)
NETWORK_BASE=$(echo $SUBNET | cut -d'.' -f1-3)

# Ping sweep rápido em paralelo (apenas ~5 segundos)
for i in {1..254}; do
    ping -c 1 -W 1 $NETWORK_BASE.$i &> /dev/null &
done
wait

# Mostrar todos os dispositivos descobertos
ip neigh show | grep -v FAILED
```

#### Método 2: Script Auxiliar (sem sudo)
Use o script já incluído na skill:

```bash
bash /home/marcelo/.claude/skills/network-scanner/scan_network.sh
```

O script automaticamente escolhe o melhor método disponível sem sudo.

#### Método 3: ARP Cache (instantâneo - sem sudo)
Mostra apenas dispositivos já conhecidos, mas é instantâneo:

```bash
ip neigh show
# ou
arp -a
```

#### Método 4: Nmap sem sudo (usando capabilities)
Configure nmap uma única vez para funcionar sem sudo:

```bash
# Configuração única (requer sudo apenas uma vez)
sudo setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap)
```

Depois disso, use nmap normalmente sem sudo:
```bash
nmap -sn 192.168.1.0/24
```

#### Método 5: ARP-Scan (última opção - requer sudo)
Use apenas se outros métodos falharem:

```bash
sudo arp-scan --localnet --interface=<interface>
```

### 3. Formato de Apresentação

Sempre apresente os resultados em formato de tabela clara:

```
╔════════════════╦═══════════════════╦═══════════════════════════╦══════════════╗
║ IP Address     ║ MAC Address       ║ Hostname/Vendor           ║ Status       ║
╠════════════════╬═══════════════════╬═══════════════════════════╬══════════════╣
║ 192.168.1.1    ║ aa:bb:cc:dd:ee:ff ║ Router (TP-Link)          ║ ONLINE       ║
║ 192.168.1.10   ║ 11:22:33:44:55:66 ║ Desktop-PC                ║ ONLINE       ║
║ 192.168.1.25   ║ 77:88:99:aa:bb:cc ║ Smartphone (Samsung)      ║ ONLINE       ║
╚════════════════╩═══════════════════╩═══════════════════════════╩══════════════╝
```

### 4. Informações Adicionais Úteis

Depois de mostrar a tabela principal, forneça:

- **Total de dispositivos encontrados**
- **Range de IPs escaneado**
- **Interface de rede utilizada**
- **Horário do scan**
- **Sugestões de próximos passos** (ex: scan de portas em um IP específico)

### 5. Verificação de Ferramentas

Antes de executar, verifique quais ferramentas estão disponíveis:

```bash
command -v nmap &> /dev/null && echo "nmap: disponível" || echo "nmap: não instalado"
command -v arp-scan &> /dev/null && echo "arp-scan: disponível" || echo "arp-scan: não instalado"
```

Se as ferramentas não estiverem instaladas, sugira a instalação:
- **Ubuntu/Debian**: `sudo apt install nmap arp-scan`
- **Fedora/RHEL**: `sudo dnf install nmap arp-scan`
- **Arch**: `sudo pacman -S nmap arp-scan`

### 6. Resolução de Nomes de Host

Para tentar resolver os nomes de host dos dispositivos:

```bash
# Para cada IP encontrado
nslookup <IP>
# ou
host <IP>
# ou
dig -x <IP>
```

### 7. Identificação de Vendor (Fabricante)

Os primeiros 3 bytes do MAC address identificam o fabricante. Use bases de dados online ou ferramentas como `arp-scan` que já incluem esta informação.

## Exemplo Completo de Uso (SEM SUDO)

```bash
# 1. Identificar a rede
echo "=== Identificando configuração de rede ==="
SUBNET=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v 127.0.0.1 | head -n1)
NETWORK_BASE=$(echo $SUBNET | cut -d'.' -f1-3)
echo "Subnet base: $NETWORK_BASE.0/24"

# 2. Ping sweep rápido (método principal - sem sudo)
echo -e "\n=== Executando ping sweep ==="
for i in {1..254}; do
    ping -c 1 -W 1 $NETWORK_BASE.$i &> /dev/null &
done
wait
echo "Ping sweep completo!"

# 3. Mostrar dispositivos descobertos
echo -e "\n=== Dispositivos encontrados ==="
ip neigh show | grep -v FAILED

# 4. (Alternativa) Usar o script auxiliar
echo -e "\n=== Ou use o script auxiliar ==="
bash /home/marcelo/.claude/skills/network-scanner/scan_network.sh
```

## Configuração de Bypass para Nmap (Uma Única Vez)

Se você quer usar nmap sem sudo permanentemente, configure as capabilities:

```bash
# Execute este comando uma única vez
sudo setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap)

# Verificar se foi aplicado
getcap $(which nmap)

# Agora você pode usar nmap sem sudo:
nmap -sn 192.168.240.0/24
```

Para remover as capabilities (se necessário):
```bash
sudo setcap -r $(which nmap)
```

## Opções Avançadas

### Scan Contínuo (Monitoramento)
```bash
watch -n 30 'sudo arp-scan --localnet'
```

### Scan de Portas em Dispositivo Específico
```bash
sudo nmap -p- -sV <IP>
```

### Detectar Sistema Operacional
```bash
sudo nmap -O <IP>
```

### Salvar Resultados
```bash
sudo nmap -sn 192.168.1.0/24 -oN scan_results.txt
```

## Notas de Segurança

- **Permissões**: Alguns comandos requerem `sudo` para acesso raw socket
- **Ética**: Apenas escaneie redes que você tem permissão para escanear
- **Firewall**: Alguns dispositivos podem não responder a pings (stealth mode)
- **Legal**: Certifique-se de estar em conformidade com as políticas da rede

## Troubleshooting

### Problema: "Operation not permitted" com nmap
**Solução**: Use o método de ping sweep (sem sudo) ou configure capabilities:
```bash
sudo setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap)
```

### Problema: Poucos dispositivos encontrados
**Solução**:
- Execute o ping sweep (Método 1) que descobre todos os dispositivos ativos
- Aguarde alguns segundos após o ping sweep e verifique novamente o cache ARP
- Alguns dispositivos podem ter firewall bloqueando ICMP (ping)
- Verifique se está na interface de rede correta

### Problema: Interface de rede incorreta
**Solução**: Liste todas as interfaces com `ip link show` e escolha a correta

### Problema: Ping sweep está lento
**Solução**: O ping sweep em paralelo deve levar apenas 5-10 segundos. Se estiver mais lento, verifique sua conexão de rede.

## Informações Sempre Incluir

Ao finalizar um scan, sempre mostre:
1. ✅ Quantidade total de dispositivos ativos
2. 📡 Range de IPs escaneado
3. 🔌 Interface de rede utilizada
4. ⏰ Timestamp do scan
5. 🛠️ Ferramenta(s) utilizada(s)
6. 💡 Sugestões de próximos passos

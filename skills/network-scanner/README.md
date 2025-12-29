# Network Scanner Skill

Esta skill permite escanear a rede local para descobrir dispositivos conectados, seus endereços IP, MACs e informações adicionais.

## Instalação

A skill já está instalada em: `~/.claude/skills/network-scanner/`

Para ativar a skill, **reinicie o Claude Code**.

## Como Usar

Depois de reiniciar o Claude Code, você pode usar a skill simplesmente pedindo:

- "Escaneie a rede"
- "Mostre os dispositivos conectados"
- "Quais IPs estão na minha rede?"
- "Liste os dispositivos na rede local"
- "Varrer a rede"

O Claude automaticamente ativará esta skill e escaneará sua rede.

## Ferramentas Opcionais

A skill funciona **SEM PRECISAR DE SUDO** usando ping sweep + ARP cache!

Para recursos avançados (opcional), instale:

```bash
# Ubuntu/Debian
sudo apt install nmap arp-scan

# Fedora/RHEL
sudo dnf install nmap arp-scan

# Arch Linux
sudo pacman -S nmap arp-scan
```

## Script Auxiliar

A skill inclui um script auxiliar que você pode executar diretamente:

```bash
# Executar sem sudo (MÉTODO PADRÃO - funciona sempre!)
~/.claude/skills/network-scanner/scan_network.sh

# Executar com sudo (apenas se quiser scan adicional com nmap)
sudo ~/.claude/skills/network-scanner/scan_network.sh
```

## Métodos de Escaneamento (Ordem de Prioridade)

A skill agora **PRIORIZA MÉTODOS SEM SUDO**:

1. **Ping Sweep + ARP Cache** (PADRÃO - rápido, sem sudo, descobre todos os dispositivos)
2. **Nmap sem sudo** (após configurar capabilities - ver abaixo)
3. **ARP-Scan** (última opção - requer sudo)

## Bypass do Sudo para Nmap (Configuração Única)

Para usar nmap sem precisar de senha toda vez, configure uma única vez:

```bash
# Execute este comando UMA VEZ (requer sudo apenas nessa vez)
sudo setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap)

# Verificar se foi aplicado
getcap $(which nmap)

# Agora você pode usar nmap sem sudo para sempre!
nmap -sn 192.168.240.0/24
```

Para reverter (remover o bypass):
```bash
sudo setcap -r $(which nmap)
```

## Exemplos de Uso

### Scan Básico
```bash
Claude: "Por favor, escaneie a rede e mostre os dispositivos conectados"
```

### Scan com Detalhes de Porta
```bash
Claude: "Escaneie o IP 192.168.1.100 e mostre as portas abertas"
```

### Monitoramento Contínuo
```bash
Claude: "Configure um monitoramento contínuo da rede"
```

## Saída Esperada

A skill retornará uma tabela formatada com:

- 🌐 Endereço IP
- 🔧 Endereço MAC
- 🏷️ Hostname/Vendor (quando disponível)
- ✅ Status (ONLINE/OFFLINE)

Além de estatísticas como:
- Total de dispositivos
- Range de IPs escaneado
- Interface utilizada
- Timestamp do scan

## Notas de Segurança

- ⚠️ Apenas escaneie redes que você tem permissão para escanear
- 🔒 Alguns comandos requerem privilégios de superusuário (sudo)
- 🛡️ Alguns dispositivos podem ter firewall que bloqueia detecção

## Troubleshooting

**Problema**: Poucos dispositivos encontrados
- **Solução**: O ping sweep deve encontrar todos os dispositivos ativos! Aguarde alguns segundos após o scan e verifique novamente. Alguns dispositivos podem ter firewall bloqueando ICMP.

**Problema**: "Operation not permitted" com nmap
- **Solução**: Use o método padrão (ping sweep) que não precisa de sudo, OU configure o bypass com `setcap` (ver seção acima)

**Problema**: Ferramentas não instaladas
- **Solução**: A skill funciona sem nenhuma ferramenta extra! Mas se quiser recursos avançados, instale nmap e arp-scan conforme instruções acima

**Problema**: Ping sweep está lento
- **Solução**: O ping sweep roda em paralelo e deve levar apenas 5-10 segundos. Verifique sua conexão de rede.

## Arquivos da Skill

- `SKILL.md` - Instruções principais da skill
- `scan_network.sh` - Script auxiliar para escaneamento
- `README.md` - Este arquivo de documentação

## Autor

Criado para uso pessoal - Network Discovery Automation

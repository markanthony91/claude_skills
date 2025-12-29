# Docker Manager Skill

Esta skill permite gerenciar, monitorar e resolver problemas com containers Docker automaticamente, incluindo troubleshooting inteligente e ações corretivas.

## Instalação

A skill já está instalada em: `~/.claude/skills/docker-manager/`

Para ativar a skill, **reinicie o Claude Code**.

## Como Usar

Depois de reiniciar o Claude Code, você pode usar a skill simplesmente pedindo:

- "Verifique meus containers"
- "Mostre o status dos containers Docker"
- "Tem algum container parado?"
- "Conserte os containers com problema"
- "Monitore o Docker"
- "Inicie os containers parados"

O Claude automaticamente ativará esta skill e verificará seus containers.

## Funcionalidades

### ✅ Monitoramento
- Lista todos os containers (rodando e parados)
- Mostra uso de recursos (CPU, memória, rede)
- Verifica status de saúde (health checks)
- Monitora dependências (redes, volumes)

### 🔧 Troubleshooting Automático
A skill detecta e tenta resolver automaticamente:

1. **Containers Parados (Exited)**
   - Verifica logs para identificar erro
   - Verifica código de saída
   - Tenta iniciar automaticamente
   - Reporta se a ação funcionou

2. **Containers em Crash Loop (Restarting)**
   - Analisa logs para identificar causa
   - Mostra últimos erros
   - Sugere ações corretivas

3. **Containers Não Saudáveis (Unhealthy)**
   - Verifica health checks
   - Tenta reiniciar container
   - Monitora recuperação

4. **Alto Uso de Recursos**
   - Identifica containers com CPU/memória alta
   - Sugere otimizações

### 🚀 Ações Corretivas Automáticas
- Inicia containers parados
- Reinicia containers com problemas
- Verifica dependências entre containers
- Sugere recriar containers se necessário

## Script Auxiliar

A skill inclui um script auxiliar que você pode executar diretamente:

```bash
# Executar verificação completa
~/.claude/skills/docker-manager/check_containers.sh

# Com sudo (se necessário)
sudo ~/.claude/skills/docker-manager/check_containers.sh
```

## Pré-requisitos

### Docker Instalado
```bash
# Ubuntu/Debian
sudo apt install docker.io

# Fedora/RHEL
sudo dnf install docker

# Arch Linux
sudo pacman -S docker
```

### Permissões Docker

Para executar comandos Docker sem sudo, adicione seu usuário ao grupo docker:

```bash
sudo usermod -aG docker $USER
# Depois, faça logout e login novamente
```

### Iniciar Docker na Inicialização

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

## Exemplos de Uso

### Verificação Básica
```bash
Claude: "Verifique meus containers Docker"
```

A skill irá:
1. Listar todos os containers
2. Identificar problemas
3. Tentar corrigir automaticamente
4. Mostrar resumo com ações tomadas

### Container Específico
```bash
Claude: "O container 'webapp' não está rodando, pode verificar?"
```

A skill irá:
1. Verificar status do container 'webapp'
2. Analisar logs se estiver parado
3. Tentar iniciar
4. Reportar resultado

### Monitoramento Contínuo
```bash
Claude: "Monitore os recursos dos containers"
```

A skill irá mostrar:
- CPU e memória de cada container
- I/O de rede
- Containers com uso elevado

## Saída Esperada

A skill retornará informações formatadas incluindo:

### Tabela de Containers
```
╔════════════╦═══════════════════╦════════════════╦═══════════════════╦═════════════╗
║ ID         ║ Nome              ║ Status         ║ Imagem            ║ Portas      ║
╠════════════╬═══════════════════╬════════════════╬═══════════════════╬═════════════╣
║ abc123     ║ webapp            ║ Up 2 hours     ║ nginx:latest      ║ 80->80      ║
║ def456     ║ database          ║ Up 3 days      ║ postgres:15       ║ 5432->5432  ║
║ ghi789     ║ cache             ║ Exited (1)     ║ redis:7           ║             ║
╚════════════╩═══════════════════╩════════════════╩═══════════════════╩═════════════╝
```

### Resumo de Ações
- ✅ Total de containers
- 🔄 Containers rodando vs parados
- ⚠️ Problemas detectados
- 🔧 Ações corretivas executadas
- 💡 Sugestões de próximos passos

## Troubleshooting da Skill

### Problema: "Permission denied" ao acessar Docker
**Solução**:
```bash
sudo usermod -aG docker $USER
# Fazer logout e login novamente
```

### Problema: "Cannot connect to Docker daemon"
**Solução**:
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Problema: Container não inicia mesmo após troubleshooting
**Solução**:
A skill irá:
1. Mostrar logs detalhados
2. Verificar portas em conflito
3. Verificar volumes e redes
4. Sugerir recriar o container

## Docker Compose

A skill também suporta Docker Compose se estiver disponível:

```bash
# Instalar docker-compose
sudo apt install docker-compose

# A skill detectará automaticamente e oferecerá:
# - docker-compose ps
# - docker-compose up -d
# - docker-compose restart
```

## Comandos Úteis Incluídos

A skill conhece e pode executar:

```bash
# Gerenciamento
docker start <nome>      # Iniciar container
docker stop <nome>       # Parar container
docker restart <nome>    # Reiniciar container
docker rm <nome>         # Remover container

# Diagnóstico
docker logs <nome>       # Ver logs
docker inspect <nome>    # Ver configuração completa
docker stats             # Ver recursos em tempo real
docker top <nome>        # Ver processos do container

# Limpeza
docker system prune      # Limpar recursos não utilizados
docker container prune   # Remover containers parados
docker image prune       # Remover imagens não utilizadas
```

## Notas de Segurança

- ⚠️ A skill nunca remove containers sem pedir confirmação
- 🔒 Sempre verifica logs antes de tomar ações
- 📋 Mantém registro de todas as ações executadas
- 💾 Sugere backup antes de mudanças destrutivas

## Arquivos da Skill

- `SKILL.md` - Instruções principais da skill para o Claude
- `check_containers.sh` - Script auxiliar para verificação automática
- `README.md` - Este arquivo de documentação

## Integração com Outras Skills

Esta skill pode ser usada em conjunto com:
- **network-scanner**: Para verificar conectividade de containers na rede
- Outras skills de DevOps e infraestrutura

## Próximos Passos Após Instalação

1. Reinicie o Claude Code
2. Teste a skill: "Verifique meus containers"
3. Configure permissões Docker se necessário
4. Use o script auxiliar para verificações rápidas

## Autor

Criado para gerenciamento automatizado de containers Docker com troubleshooting inteligente.

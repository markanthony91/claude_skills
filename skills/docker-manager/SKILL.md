---
name: docker-manager
description: Gerencia e monitora containers Docker com troubleshooting automático. Use quando o usuário pedir para verificar containers, checar status do Docker, iniciar/parar containers, ou resolver problemas com containers.
allowed-tools: Bash, Read, Write
---

# Docker Manager - Gerenciamento de Containers

Esta skill ajuda a gerenciar, monitorar e solucionar problemas com containers Docker automaticamente.

## Instruções

Quando esta skill for ativada, siga estes passos:

### 1. Verificar Status do Docker

Primeiro, verifique se o Docker está instalado e rodando:

```bash
# Verificar se Docker está instalado
command -v docker &> /dev/null && echo "Docker: instalado" || echo "Docker: não instalado"

# Verificar se Docker está rodando
sudo systemctl is-active docker || docker ps &> /dev/null && echo "Docker: ativo" || echo "Docker: inativo"

# Versão do Docker
docker --version
```

### 2. Listar Containers

Use estes comandos para listar containers:

```bash
# Listar apenas containers rodando
docker ps

# Listar TODOS os containers (incluindo parados)
docker ps -a

# Formato customizado com mais informações
docker ps -a --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}\t{{.Ports}}"
```

### 3. Verificar Status de Containers Específicos

Para verificar containers específicos:

```bash
# Verificar se um container está rodando
docker ps --filter "name=<nome_container>" --format "{{.Names}}: {{.Status}}"

# Obter detalhes completos de um container
docker inspect <nome_ou_id>

# Ver estatísticas de recursos (CPU, memória)
docker stats <nome_ou_id> --no-stream
```

### 4. Troubleshooting Automático

**IMPORTANTE:** Sempre execute troubleshooting quando detectar containers parados ou com problemas!

#### 4.1. Container Parado (Status: Exited)

```bash
# 1. Verificar logs para identificar o erro
docker logs --tail 50 <nome_container>

# 2. Verificar quando parou
docker inspect <nome_container> --format='{{.State.FinishedAt}}'

# 3. Verificar código de saída
docker inspect <nome_container> --format='{{.State.ExitCode}}'

# 4. Tentar iniciar o container
docker start <nome_container>

# 5. Se falhar, verificar logs novamente
docker logs --tail 50 <nome_container>
```

#### 4.2. Container com Restart Contínuo (Status: Restarting)

```bash
# 1. Ver logs para identificar crash loop
docker logs --tail 100 <nome_container>

# 2. Parar o container para análise
docker stop <nome_container>

# 3. Verificar configuração
docker inspect <nome_container> | grep -A 10 "RestartPolicy"

# 4. Verificar volumes e portas
docker inspect <nome_container> | grep -A 5 "Mounts"
docker inspect <nome_container> | grep -A 5 "Ports"
```

#### 4.3. Container com Alto Uso de Recursos

```bash
# Verificar uso de recursos
docker stats --no-stream

# Se CPU ou memória alta, investigar:
docker top <nome_container>
docker logs --tail 100 <nome_container>
```

#### 4.4. Container não responde (Unhealthy)

```bash
# Ver health check
docker inspect <nome_container> --format='{{.State.Health.Status}}'

# Ver logs de health check
docker inspect <nome_container> | grep -A 20 "Health"

# Reiniciar container
docker restart <nome_container>
```

### 5. Ações Corretivas Automáticas

Quando detectar problemas, execute estas ações em ordem:

**Para containers parados:**
1. Verificar logs
2. Tentar iniciar: `docker start <nome>`
3. Se falhar, verificar dependências (outros containers, redes, volumes)
4. Se ainda falhar, sugerir recriar o container

**Para containers com problemas:**
1. Verificar logs: `docker logs --tail 100 <nome>`
2. Verificar recursos: `docker stats --no-stream <nome>`
3. Reiniciar: `docker restart <nome>`
4. Se persistir, parar e iniciar: `docker stop <nome> && docker start <nome>`

**Para containers em crash loop:**
1. Parar o container: `docker stop <nome>`
2. Analisar logs
3. Verificar variáveis de ambiente: `docker inspect <nome> | grep -A 20 "Env"`
4. Verificar comando de inicialização: `docker inspect <nome> | grep -A 5 "Cmd"`
5. Sugerir correções ou recriar

### 6. Comandos de Gerenciamento

```bash
# Iniciar container
docker start <nome_ou_id>

# Parar container
docker stop <nome_ou_id>

# Reiniciar container
docker restart <nome_ou_id>

# Remover container (apenas se parado)
docker rm <nome_ou_id>

# Forçar remoção
docker rm -f <nome_ou_id>

# Ver logs em tempo real
docker logs -f <nome_ou_id>

# Executar comando dentro do container
docker exec -it <nome_ou_id> /bin/bash
# ou
docker exec -it <nome_ou_id> /bin/sh
```

### 7. Formato de Apresentação

Sempre apresente os resultados em formato de tabela clara:

```
╔══════════════╦═══════════════════╦════════════════╦═══════════════════╦═════════════╗
║ ID           ║ Nome              ║ Status         ║ Imagem            ║ Portas      ║
╠══════════════╬═══════════════════╬════════════════╬═══════════════════╬═════════════╣
║ abc123def456 ║ webapp            ║ Up 2 hours     ║ nginx:latest      ║ 80->80      ║
║ def456ghi789 ║ database          ║ Up 3 days      ║ postgres:15       ║ 5432->5432  ║
║ ghi789jkl012 ║ cache             ║ Exited (1)     ║ redis:7           ║             ║
╚══════════════╩═══════════════════╩════════════════╩═══════════════════╩═════════════╝
```

### 8. Informações Sempre Incluir

Ao finalizar a verificação, sempre mostre:

1. ✅ **Total de containers** (rodando / total)
2. 🔄 **Containers com problemas** (parados, restarting, unhealthy)
3. 📊 **Uso de recursos** (CPU, memória total)
4. ⚠️ **Ações tomadas** (containers iniciados, reiniciados, etc.)
5. 💡 **Sugestões** (próximos passos, otimizações)

### 9. Verificação de Dependências

Sempre verificar dependências entre containers:

```bash
# Ver redes Docker
docker network ls

# Ver containers em uma rede específica
docker network inspect <rede_nome> | grep -A 5 "Containers"

# Ver volumes
docker volume ls

# Ver quais containers usam um volume
docker ps -a --filter volume=<volume_nome>
```

### 10. Docker Compose (se disponível)

Se detectar docker-compose.yml, oferecer suporte:

```bash
# Verificar se docker-compose está instalado
command -v docker-compose &> /dev/null && echo "docker-compose: disponível"

# Ver status de todos os serviços
docker-compose ps

# Iniciar todos os serviços
docker-compose up -d

# Parar todos os serviços
docker-compose down

# Ver logs
docker-compose logs --tail=100

# Reiniciar um serviço específico
docker-compose restart <nome_serviço>
```

## Fluxo de Troubleshooting Automático

Quando a skill for ativada, siga este fluxo:

1. **Listar todos os containers** e identificar problemas
2. **Para cada container com problema:**
   - Classificar o tipo de problema (parado, restarting, unhealthy, etc.)
   - Executar troubleshooting específico
   - Tentar ação corretiva
   - Verificar se a ação resolveu
   - Reportar resultado
3. **Apresentar resumo** com todas as ações tomadas
4. **Sugerir próximos passos** se houver problemas não resolvidos

## Exemplo Completo de Uso

```bash
# 1. Verificar Docker
docker --version && echo "Docker OK"

# 2. Listar todos os containers
docker ps -a --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}"

# 3. Identificar containers parados
STOPPED=$(docker ps -a --filter "status=exited" --format "{{.Names}}")

# 4. Para cada container parado, tentar iniciar
for container in $STOPPED; do
    echo "Tentando iniciar: $container"
    docker logs --tail 20 $container
    docker start $container
    if [ $? -eq 0 ]; then
        echo "✓ $container iniciado com sucesso"
    else
        echo "✗ Falha ao iniciar $container"
    fi
done

# 5. Verificar status final
docker ps --format "table {{.Names}}\t{{.Status}}"
```

## Notas de Segurança

- **Permissões**: Comandos Docker podem requerer sudo ou que o usuário esteja no grupo `docker`
- **Cuidado**: Não remova containers sem confirmar com o usuário
- **Logs**: Sempre verifique logs antes de tomar ações
- **Backup**: Sugira backup de volumes antes de remover containers

## Troubleshooting da Skill

### Problema: "Permission denied" ao executar docker
**Solução**:
```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
# Depois, fazer logout e login novamente
```

### Problema: Docker daemon não está rodando
**Solução**:
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Problema: Container não inicia após múltiplas tentativas
**Solução**:
- Verificar logs detalhadamente
- Verificar se portas estão em uso: `sudo netstat -tulpn | grep <porta>`
- Verificar se volumes existem
- Considerar recriar o container com docker-compose ou docker run

## Comandos Úteis para Diagnóstico

```bash
# Ver todos os recursos Docker
docker system df

# Limpar recursos não utilizados
docker system prune

# Ver eventos do Docker em tempo real
docker events

# Inspecionar imagem
docker image inspect <imagem>

# Ver histórico de uma imagem
docker history <imagem>
```

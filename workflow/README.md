# N8N Workflows Collection

Coleção de workflows do n8n para automação e integração com IA.

## Sobre

Esta pasta contém **43 workflows validados** exportados do n8n, incluindo agentes de IA, integrações com APIs e automações diversas.

**Data de importação:** 06/01/2026
**Origem:** `/home/marcelo/Downloads/teste_backup_workflow_n8n/`

## Categorias de Workflows

### 🤖 Agentes de IA e RAG
- **Agent CLS** - Agente CLS
- **AGENTE DE IA RAG v0.1 - LEONARDO CANDIANI** - Sistema RAG completo
- **Agent Conversacional Travel** - Agente conversacional para viagens
- **Agent see, speak** - Agente com capacidades visuais e de fala
- **Ultimate_Agentic_RAG_AI_Agent_Template** - Template completo de agente RAG
- **Meu exemplo de agent a ser melhorado** - Agente personalizado
- **Agent_query_test** - Testes de queries
- **agent test** - Agente de testes
- **[Estudo] Agente completo** - Estudo de agente completo
- **[TEST] Knowledge Agent Puket** - Agente de conhecimento

### 💬 WhatsApp / Comunicação
- **Disparador de mensagem Whatsapp Evo-API** - Envio de mensagens via Evo-API
- **Envio de imagem Fisheye para Whatsapp** - Envio de imagens
- **Agent Evo API para testes** - Testes com Evo-API

### 📧 Email e SMS
- **[TEST]Envio de emails em massa** - Automação de emails
- **[TEST]Envio de sms em massa** - Automação de SMS
- **LAB teste de envio email pelo mailsender** - Testes de email
- **[TEST]Envio de relatorio mensal custos BK** - Relatórios automáticos
- **[TEST]Laboratório de envio de SMS Dev** - Desenvolvimento SMS
- **[TEST]Laboratório de envio de SMS Marktel** - Testes Marktel
- **Receber email e extrair informações** - Processamento de emails

### 💬 Telegram
- **Self Learning Telegram** - Bot Telegram com aprendizado
- **Only telegram** - Integração Telegram

### 📊 Dados e Integrações
- **RAG Ingestion - Google Drive to Open WebUI (Melhorado)** - Pipeline RAG com Google Drive
- **Exemplo de preparação de arquivo excel em google planilha** - Processamento de planilhas
- **Tool consultar CNPJ** - Consulta de dados CNPJ
- **CNPJ** - Automação CNPJ
- **cat homelab** - Gestão homelab

### 🛠️ Utilitários e DevOps
- **CSL MCP Server** - Servidor MCP
- **Atualizador de Evo-API via portainer** - Atualização automática
- **Heatmap Dahua** - Análise de heatmaps
- **lab print post** - Laboratório de posts
- **Relatório teste** - Geração de relatórios

### 🧪 Testes e Desenvolvimento
- **Disparador Test** - Testes de disparadores
- **Disparo_** - Testes de disparo
- **My workflow** (2, 4, 5) - Workflows de teste
- **My Sub-Workflow 1** - Sub-workflow
- **teste_work** - Workflow de teste
- **Renegociação AlphavilleOLD** - Sistema de renegociação
- **saiu - Grupo** - Gestão de grupos
- **Vendedor de iPhone v0.1 - YouTube** - Bot vendedor

## 🚀 Importação

### Script de Importação Automática

Execute o script `import_workflow.sh` para importar todos os workflows para sua instância n8n:

```bash
chmod +x import_workflow.sh
./import_workflow.sh
```

### Configuração do Script

Antes de executar, edite as variáveis no início do script:

```bash
WORKFLOW_DIR="/caminho/para/workflows/"
API_KEY="sua_api_key_aqui"
N8N_URL="https://seu-n8n.domain.com"
```

### Importação Manual

Para importar workflows individualmente via n8n UI:
1. Acesse seu n8n
2. Clique em **Workflows** > **Import from File**
3. Selecione o arquivo JSON desejado
4. Configure as credenciais necessárias

## 📋 Requisitos

Alguns workflows podem necessitar de:
- **Credenciais configuradas:** WhatsApp API, Telegram, OpenAI, Google Drive, etc.
- **Extensões n8n:** Verifique se possui os nodes necessários instalados
- **APIs externas:** Evo-API, OpenWebUI, etc.

## 🔧 Manutenção

### Backup
Os workflows originais estão preservados em:
```
/home/marcelo/Downloads/teste_backup_workflow_n8n/
```

### Atualização
Para adicionar novos workflows:
1. Exporte do n8n em formato JSON
2. Copie para esta pasta
3. Atualize este README

### Versionamento
- Workflows estão versionados via git
- Commit format: `feat(workflow): adiciona [nome do workflow]`

## 📝 Notas

- Arquivos com menos de 1KB foram excluídos (provavelmente corrompidos ou vazios)
- Total de workflows válidos: **43**
- Todos os metadados pessoais (IDs, timestamps) são removidos na importação
- O script detecta automaticamente o header de autenticação correto

## 🔗 Referências

- [N8N Documentation](https://docs.n8n.io/)
- [Evo-API](https://github.com/EvolutionAPI/evolution-api)
- [OpenWebUI](https://github.com/open-webui/open-webui)

---

**Última atualização:** 06/01/2026
**Mantido por:** Marcelo

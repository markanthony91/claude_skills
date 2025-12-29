# 🚀 Guia Rápido: Extrair Metadados para TODAS as Câmeras

## 📋 O que você vai conseguir

Extrair automaticamente as informações do site AIVisual para **TODAS as câmeras** (P1, P2 e P3):

- ✅ **P1**: Todos os metadados completos (extraídos do site)
- ✅ **P2**: Dados compartilhados (Lugar, IP internet, Versão)
- ✅ **P3**: Dados compartilhados (Lugar, IP internet, Versão)

---

## ⚡ Método Rápido (Recomendado)

```bash
./extrair_metadados.sh
```

Isso vai:
1. ✓ Fazer login no AIVisual
2. ✓ Extrair metadados de todas as P1
3. ✓ Copiar dados para P2 e P3
4. ✓ Salvar em `data/camera_metadata.json`

**Tempo estimado**: 2-5 minutos (dependendo do número de câmeras)

---

## 🔍 Passo a Passo Detalhado

### **1. Executar Extração**

```bash
cd /home/marcelo/sistemas/captura_cameras
./extrair_metadados.sh
```

O script vai mostrar:
```
════════════════════════════════════════════════════════════════
       EXTRATOR DE METADADOS - AIVISUAL DASHBOARD
════════════════════════════════════════════════════════════════

📋 O que este script faz:

  1. 🔐 Faz login no dashboard AIVisual
  2. 📡 Extrai metadados de TODAS as câmeras P1
  3. 📦 Copia dados compartilhados para P2 e P3
  4. 💾 Salva tudo em: data/camera_metadata.json

Deseja continuar? (s/N):
```

Digite `s` e pressione Enter.

---

### **2. Aguardar Extração**

O script vai processar cada câmera:

```
🎥 Processando câmera 1/115...
  ✓ Salvador_Av_ACM_P1
    Campos extraídos: 10

🎥 Processando câmera 2/115...
  ✓ Aracaju_Av_Augusto_Franco_P1
    Campos extraídos: 10

...

📦 Copiando dados compartilhados para P2 e P3...
  + Salvador_Av_ACM_P2
  + Salvador_Av_ACM_P3
  + Aracaju_Av_Augusto_Franco_P2
  + Aracaju_Av_Augusto_Franco_P3

✓ 230 câmeras P2/P3 adicionadas
💾 Metadados salvos em: data/camera_metadata.json
📊 Total de câmeras: 345
```

---

### **3. Verificar Resultado**

```bash
# Ver quantas câmeras foram extraídas
cat data/camera_metadata.json | python3 -m json.tool | grep "_P1\|_P2\|_P3" | wc -l

# Ver exemplo de uma câmera
cat data/camera_metadata.json | python3 -m json.tool | grep -A 15 "Salvador_Av_ACM_P1"
```

---

### **4. Reiniciar Dashboard**

```bash
./start_dashboard.sh
```

Acesse: http://localhost:5000

**IMPORTANTE**: Limpe o cache do navegador:
- Chrome/Edge: `Ctrl + Shift + R`
- Firefox: `Ctrl + F5`

---

## 📊 Exemplo de Resultado

### **Arquivo gerado: `data/camera_metadata.json`**

```json
{
  "Salvador_Av_ACM_P1": {
    "nome_completo": "BK - Salvador Av ACM_P1",
    "lugar": "Drive_Thru",
    "area": "Pedido",
    "ultima_resposta": "2025-12-22 07:09:54",
    "ip_local": "172.18.0.4",
    "ip_internet": "187.29.40.134",
    "mac_address": "02:42:ac:12:00:04",
    "temperatura_cpu": "0,00",
    "uuid": "1161727969480FABKHMVBAXZ",
    "versao_sistema": "DTRHU-3.7.1"
  },
  "Salvador_Av_ACM_P2": {
    "nome_completo": "BK - Salvador Av ACM_P2",
    "lugar": "Drive_Thru",
    "ip_internet": "187.29.40.134",
    "versao_sistema": "DTRHU-3.7.1"
  },
  "Salvador_Av_ACM_P3": {
    "nome_completo": "BK - Salvador Av ACM_P3",
    "lugar": "Drive_Thru",
    "ip_internet": "187.29.40.134",
    "versao_sistema": "DTRHU-3.7.1"
  }
}
```

---

## 🎨 Visualização no Dashboard

### **Câmera P1 (Dados Completos)**
```
┌─────────────────────────────────────┐
│ [Imagem]                            │
│ Salvador Av ACM                     │
│ Câmera P1                           │
│                                     │
│ ┌─ Metadados ─────────────────────┐ │
│ │ Lugar: Drive_Thru               │ │
│ │ Área: Pedido                    │ │
│ │ IP Local: 172.18.0.4            │ │
│ │ IP Internet: 187.29.40.134      │ │
│ │ Versão: DTRHU-3.7.1             │ │
│ │ CPU: 0,00°C                     │ │
│ │ UUID: 1161727969480FABKHMVBAXZ  │ │
│ └─────────────────────────────────┘ │
│ Atualizada: 27/12/2025 16:21:54     │
└─────────────────────────────────────┘
```

### **Câmeras P2 e P3 (Dados Compartilhados)**
```
┌─────────────────────────────────────┐
│ [Imagem]                            │
│ Salvador Av ACM                     │
│ Câmera P2                           │
│                                     │
│ ┌─ Metadados ─────────────────────┐ │
│ │ Lugar: Drive_Thru               │ │
│ │ IP Internet: 187.29.40.134      │ │
│ │ Versão: DTRHU-3.7.1             │ │
│ └─────────────────────────────────┘ │
│ Atualizada: 27/12/2025 16:21:54     │
└─────────────────────────────────────┘
```

---

## 🔄 Atualizar Metadados

Para atualizar os metadados (executar novamente):

```bash
./extrair_metadados.sh
```

O script vai:
- ✓ Sobrescrever o arquivo `camera_metadata.json`
- ✓ Extrair dados atualizados do site
- ✓ Aplicar para todas as câmeras

---

## 🛠️ Resolução de Problemas

### **Erro: "Login falhou"**
- Verifique as credenciais em `extrair_metadados_aivisual.py`
- Linhas 15-16: `USERNAME` e `PASSWORD`

### **Erro: "Nenhum metadado extraído"**
- O site pode ter mudado a estrutura HTML
- Verifique se o site está acessível
- Tente executar sem `--headless` para debug

### **Metadados não aparecem no dashboard**
1. Limpe o cache: `Ctrl + Shift + R`
2. Verifique o arquivo: `cat data/camera_metadata.json`
3. Reinicie o dashboard: `./start_dashboard.sh`

---

## 📝 Scripts Disponíveis

| Script | Função |
|--------|--------|
| `extrair_metadados.sh` | Extrai metadados do site (recomendado) |
| `extrair_metadados_aivisual.py` | Script Python de extração |
| `update_metadata.py` | Gerenciar metadados manualmente |
| `copiar_metadados_p1_para_p2_p3.py` | Copiar P1 → P2/P3 |

---

## ⚡ Automatização (Opcional)

Para extrair metadados automaticamente toda vez que baixar as imagens:

```bash
# Editar o script executar_melhorado.sh
nano executar_melhorado.sh

# Adicionar no final:
# ./extrair_metadados.sh
```

Ou criar um script combinado:

```bash
#!/bin/bash
# baixar_tudo.sh

echo "📸 Baixando imagens..."
./executar_melhorado.sh

echo "📋 Extraindo metadados..."
./extrair_metadados.sh

echo "🚀 Iniciando dashboard..."
./start_dashboard.sh
```

---

## 🎯 Checklist Final

- [ ] Executei `./extrair_metadados.sh`
- [ ] Confirmei a extração (digitei 's')
- [ ] Aguardei até ver "CONCLUÍDO COM SUCESSO"
- [ ] Verifiquei o arquivo `data/camera_metadata.json`
- [ ] Reiniciei o dashboard `./start_dashboard.sh`
- [ ] Limpei cache do navegador `Ctrl + Shift + R`
- [ ] Visualizei os metadados nos cards das câmeras

---

**Pronto!** 🎉 Agora todas as suas 345 câmeras (P1, P2, P3) terão metadados no dashboard!

Se tiver problemas, verifique:
- `METADADOS_README.md` - Documentação completa
- `extrair_metadados_aivisual.py` - Código do extrator
- Logs de erro no terminal

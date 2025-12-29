# 📋 Sistema de Metadados de Câmeras

Este sistema permite adicionar informações extras às câmeras do dashboard, como **Lugar**, **Área**, **UUID**, **IPs**, **Temperatura**, etc.

## ✨ Funcionalidades

- **100% Backward Compatible**: Funciona mesmo sem metadados cadastrados
- **Opcional**: Câmeras sem metadados continuam funcionando normalmente
- **Fácil Atualização**: Script auxiliar para gerenciar metadados
- **Visualização no Dashboard**: Informações aparecem automaticamente nos cards

---

## 📁 Estrutura de Arquivos

```
captura_cameras/
├── data/
│   └── camera_metadata.json      # Arquivo com metadados extras
├── update_metadata.py             # Script para gerenciar metadados
├── app.py                         # Backend (modificado)
├── static/
│   ├── js/app.js                  # Frontend (modificado)
│   └── css/style.css              # Estilos (modificado)
└── METADADOS_README.md            # Este arquivo
```

---

## 🎯 Formato dos Metadados

### Arquivo: `data/camera_metadata.json`

```json
{
  "Nome_da_Loja_P1": {
    "nome_completo": "BK - Salvador Av ACM_P1",
    "lugar": "Drive_Thru",
    "area": "Pedido",
    "ultima_resposta": "2025-12-22 07:09:54",
    "ip_local": "172.18.0.4",
    "ip_internet": "187.29.40.134",
    "mac_address": "02:42:ac:12:00:04",
    "temperatura_cpu": "45,2",
    "uuid": "1161727969480FABKHMVBAXZ",
    "versao_sistema": "DTRHU-3.7.1"
  }
}
```

### Campos Disponíveis (todos opcionais):

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `nome_completo` | Nome completo da câmera | "BK - Salvador Av ACM_P1" |
| `lugar` | Localização física | "Drive_Thru", "Salão", "Cozinha" |
| `area` | Área específica | "Pedido", "Caixa", "Entrega" |
| `ultima_resposta` | Timestamp da última resposta | "2025-12-22 07:09:54" |
| `ip_local` | IP da rede local | "172.18.0.4" |
| `ip_internet` | IP de internet | "187.29.40.134" |
| `mac_address` | Endereço MAC | "02:42:ac:12:00:04" |
| `temperatura_cpu` | Temperatura da CPU | "45,2" |
| `uuid` | UUID único | "1161727969480FABKHMVBAXZ" |
| `versao_sistema` | Versão do sistema | "DTRHU-3.7.1" |

---

## 🛠️ Como Usar

### **Método 1: Menu Interativo (Recomendado)**

```bash
python3 update_metadata.py
```

Você verá um menu com opções:
1. Listar todos os metadados
2. Adicionar/Atualizar metadados de uma câmera
3. Remover metadados de uma câmera
4. Ver exemplo de estrutura
5. Importação em massa (JSON)

### **Método 2: Editar JSON Manualmente**

1. Abra o arquivo:
   ```bash
   nano data/camera_metadata.json
   ```

2. Adicione os metadados no formato correto

3. Salve e recarregue o dashboard

### **Método 3: Via Python Script**

```python
from update_metadata import add_camera_metadata

# Adicionar metadados de uma câmera
add_camera_metadata("Salvador_Av_ACM_P1", {
    "lugar": "Drive_Thru",
    "area": "Pedido",
    "ip_local": "172.18.0.4",
    "uuid": "1161727969480FABKHMVBAXZ"
})
```

---

## 🔍 Como Encontrar o ID da Câmera

O **ID da câmera** segue o padrão: `Nome_da_Loja_P{1,2,3}`

### Exemplos:
- `Aguas_Claras_Castaneiras_P1`
- `Salvador_Av_ACM_P1`
- `Aracaju_Av_Augusto_Franco_P2`

### Como descobrir:
1. Abra o dashboard
2. Veja o nome da loja no card
3. Substitua espaços por `_` e adicione `_P1`, `_P2` ou `_P3`

---

## 📊 Visualização no Dashboard

Quando você adiciona metadados, eles aparecem automaticamente no card da câmera:

```
┌─────────────────────────────────────┐
│ [Imagem da Câmera]                  │
│                                     │
│ Salvador Av ACM                     │
│ Câmera P1                           │
│                                     │
│ ┌─ Metadados ─────────────────────┐ │
│ │ Lugar: Drive_Thru               │ │
│ │ Área: Pedido                    │ │
│ │ IP Local: 172.18.0.4            │ │
│ │ IP Internet: 187.29.40.134      │ │
│ │ Versão: DTRHU-3.7.1             │ │
│ │ CPU: 45,2°C                     │ │
│ │ UUID: 1161727969480FABKHMVBAXZ  │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Atualizada: 27/12/2025 16:21:54     │
└─────────────────────────────────────┘
```

---

## 🚀 Importação em Massa

Se você tem muitas câmeras para cadastrar:

1. Execute: `python3 update_metadata.py`
2. Escolha opção **5** (Importação em massa)
3. Cole o JSON completo:

```json
{
  "Salvador_Av_ACM_P1": {
    "lugar": "Drive_Thru",
    "area": "Pedido"
  },
  "Salvador_Av_ACM_P2": {
    "lugar": "Salão",
    "area": "Caixa"
  }
}
```

4. Pressione **Ctrl+D** para finalizar
5. Dados serão importados automaticamente

---

## 🔄 Como Extrair do Site da AIVisual

Se você quer automatizar a extração dos metadados do site:

### **Estrutura HTML do Site:**
```html
<div class="card-body">
  <h4>Nome: <b>BK - Salvador Av ACM_P1</b></h4>
  <h5>Lugar: <b>Drive_Thru</b></h5>
  <h5>Área: <b>Pedido</b></h5>
  <small id="1161727969480FABKHMVBAXZ">
    Última resposta: <b class="response">2025-12-22 07:09:54</b><br>
    IP da rede local: <b class="ethernet">172.18.0.4</b><br>
    IP de internet: <b class="internet">187.29.40.134</b><br>
    Endereço MAC: <b class="mac">02:42:ac:12:00:04</b><br>
    Temperatura da CPU: <b class="cpu">0,00</b><br>
    UUID: <b>1161727969480FABKHMVBAXZ</b><br>
    Versão do Sistema: <b class="version">DTRHU-3.7.1</b>
  </small>
</div>
```

### **Script de Extração (exemplo):**

Você pode modificar o `camera_downloader_complete.py` para extrair essas informações durante o download. Exemplo:

```python
# Extrair metadados do HTML
lugar = driver.find_element(By.XPATH, "//h5[contains(text(), 'Lugar:')]/b").text
area = driver.find_element(By.XPATH, "//h5[contains(text(), 'Área:')]/b").text
ip_local = driver.find_element(By.CSS_SELECTOR, "b.ethernet").text
uuid = driver.find_element(By.XPATH, "//small/@id").get_attribute("id")

# Salvar metadados
metadata = {
    "lugar": lugar,
    "area": area,
    "ip_local": ip_local,
    "uuid": uuid
}

# Adicionar ao arquivo JSON
from update_metadata import add_camera_metadata
add_camera_metadata(f"{loja_name}_{position}", metadata)
```

---

## ✅ Testes de Compatibilidade

Sistema testado e 100% compatível:

✓ **Câmeras com metadados**: Exibe informações extras
✓ **Câmeras sem metadados**: Funciona normalmente
✓ **Arquivo não existe**: Cria automaticamente
✓ **JSON vazio**: Não quebra o sistema
✓ **Campos opcionais**: Qualquer campo pode ser omitido

---

## 🎨 Personalização

### Adicionar Novos Campos

1. **No JSON** (`data/camera_metadata.json`):
   ```json
   {
     "Loja_P1": {
       "meu_novo_campo": "valor"
     }
   }
   ```

2. **No Frontend** (`static/js/app.js` linha ~298):
   ```javascript
   ${meta.meu_novo_campo ?
     `<div class="metadata-item"><strong>Novo Campo:</strong> ${escapeHtml(meta.meu_novo_campo)}</div>`
     : ''
   }
   ```

3. **Recarregue o dashboard**: `Ctrl + Shift + R`

---

## 🐛 Troubleshooting

### Metadados não aparecem no dashboard?

1. **Verifique o JSON**:
   ```bash
   python3 -c "import json; print(json.load(open('data/camera_metadata.json')))"
   ```

2. **Teste a API**:
   ```bash
   curl http://localhost:5000/api/cameras | grep metadata
   ```

3. **Limpe o cache do navegador**:
   - Chrome/Edge: `Ctrl + Shift + R`
   - Firefox: `Ctrl + F5`

### ID da câmera incorreto?

- Verifique se o ID no JSON corresponde ao `base_id` da câmera
- Formato: `Nome_da_Loja_P1` (sem espaços, com underscores)

---

## 📝 Exemplos Práticos

### Adicionar metadados de uma câmera:

```bash
python3 update_metadata.py
# Escolher opção 2
# Preencher os dados interativamente
```

### Listar todas as câmeras com metadados:

```bash
python3 update_metadata.py
# Escolher opção 1
```

### Remover metadados:

```bash
python3 update_metadata.py
# Escolher opção 3
# Informar ID da câmera
```

---

## 📞 Suporte

Se tiver dúvidas ou problemas:

1. Verifique este README
2. Execute testes de compatibilidade
3. Consulte os logs do dashboard
4. Teste com dados de exemplo

---

**Última atualização**: 2025-12-27
**Versão**: 1.0

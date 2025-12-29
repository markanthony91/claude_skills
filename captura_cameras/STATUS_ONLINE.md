# 🔴🟢 Status Online/Offline de Câmeras

## 🎯 O que é?

Sistema de monitoramento em tempo real que mostra se cada câmera está **online** ou **offline** baseado no campo **"última_resposta"** dos metadados.

---

## 📊 Como Funciona

### **Lógica de Detecção**

```
🟢 ONLINE:  última_resposta ≤ 15 minutos atrás
🔴 OFFLINE: última_resposta > 15 minutos atrás
⚪ SEM INFO: câmera sem metadados
```

### **Exemplo Prático**

```json
{
  "Salvador_Av_ACM_P1": {
    "nome_completo": "BK - Salvador Av ACM_P1",
    "lugar": "Drive_Thru",
    "ultima_resposta": "2025-12-27 16:45:30",  ← Usado para calcular status
    "ip_internet": "187.29.40.134",
    ...
  }
}
```

**Se agora são 16:50:**
- Diferença: 16:50 - 16:45 = **5 minutos**
- Status: 🟢 **ONLINE** (≤ 15 minutos)

**Se agora são 17:05:**
- Diferença: 17:05 - 16:45 = **20 minutos**
- Status: 🔴 **OFFLINE** (> 15 minutos)

---

## 🎨 Visualização no Dashboard

### **Antes (Sem Status):**
```
┌────────────────────────────────────┐
│ Salvador_Av_ACM                    │
│ Câmera P1                          │
│ Lugar: Drive_Thru                  │
└────────────────────────────────────┘
```

### **Agora (Com Status):** ⭐
```
┌────────────────────────────────────┐
│ Salvador_Av_ACM  🟢 Online         │ ← Badge de status
│ Câmera P1                          │
│ Lugar: Drive_Thru                  │
└────────────────────────────────────┘
```

**Câmera Offline:**
```
┌────────────────────────────────────┐
│ Aracaju_Centro  🔴 Offline         │ ← Badge vermelho
│ Câmera P2                          │
│ Lugar: Salão                       │
└────────────────────────────────────┘
```

---

## 🛠️ Implementação Técnica

### **1. Backend (app.py)**

**Função de Verificação:**
```python
def is_camera_online(metadata):
    """Verifica se câmera está online baseado em 'última_resposta'"""
    if not metadata or 'ultima_resposta' not in metadata:
        return None

    try:
        # Parse: "2025-12-22 07:09:54"
        ultima_resposta = datetime.strptime(
            metadata['ultima_resposta'],
            '%Y-%m-%d %H:%M:%S'
        )

        # Calcular diferença
        agora = datetime.now()
        diferenca = agora - ultima_resposta

        # Online se ≤ 15 minutos
        TIMEOUT_MINUTOS = 15
        return diferenca <= timedelta(minutes=TIMEOUT_MINUTOS)

    except Exception as e:
        return None
```

**Endpoint `/api/cameras`:**
```python
for camera in cameras:
    if base_id in metadata:
        camera['metadata'] = metadata[base_id]
        camera['online'] = is_camera_online(metadata[base_id])  ← Novo campo
    else:
        camera['metadata'] = None
        camera['online'] = None
```

---

### **2. Frontend (app.js)**

**Badge Gerado:**
```javascript
let onlineStatusBadge = '';
if (camera.online !== null) {
    if (camera.online) {
        onlineStatusBadge = '<span class="online-badge online">🟢 Online</span>';
    } else {
        onlineStatusBadge = '<span class="online-badge offline">🔴 Offline</span>';
    }
}
```

**Inserido no HTML:**
```javascript
<div class="camera-title">
    ${escapeHtml(camera.loja)}
    ${onlineStatusBadge}  ← Badge ao lado do nome
</div>
```

---

### **3. Estilos (style.css)**

```css
.online-badge.online {
    background-color: #dcfce7;  /* Verde claro */
    color: #16a34a;             /* Verde escuro */
    border: 1px solid #86efac;
}

.online-badge.offline {
    background-color: #fee2e2;  /* Vermelho claro */
    color: #dc2626;             /* Vermelho escuro */
    border: 1px solid #fecaca;
}
```

---

## 🔧 Configuração

### **Ajustar Timeout (padrão: 15 minutos)**

Edite `app.py`, função `is_camera_online()`:

```python
# Alterar de 15 para outro valor
TIMEOUT_MINUTOS = 15  ← Mudar aqui (ex: 10, 20, 30)
```

**Exemplos:**
- `TIMEOUT_MINUTOS = 10` → Mais rigoroso (offline após 10 min)
- `TIMEOUT_MINUTOS = 30` → Mais tolerante (offline após 30 min)

---

## 📋 Casos de Uso

### **1. Identificar Câmeras Fora do Ar**

Ao abrir o dashboard:
- ✅ **Verdes**: Câmeras funcionando normalmente
- ❌ **Vermelhas**: Câmeras com problemas de comunicação

### **2. Monitoramento Visual Rápido**

```
┌─────────────────────────────────────────┐
│ Loja A                                  │
├─────────┬─────────┬──────────┐
│ P1      │ P2      │ P3       │
├─────────┼─────────┼──────────┤
│ 🟢 Online│ 🟢 Online│ 🔴 Offline│ ← P3 com problema!
└─────────┴─────────┴──────────┘
```

### **3. Verificação Pós-Download**

Após executar `./executar_paralelo_com_metadados.sh`:
- Todas as câmeras devem mostrar **🟢 Online**
- Se alguma estiver **🔴 Offline**, investigar

---

## ⚙️ Como Usar

### **1. Baixar Imagens + Metadados**

```bash
./executar_paralelo_com_metadados.sh
```

Isso irá:
- ✅ Baixar imagens de todas as câmeras
- ✅ Extrair metadados (incluindo `ultima_resposta`)
- ✅ Salvar em `data/camera_metadata.json`

### **2. Iniciar Dashboard**

```bash
./start_dashboard.sh
```

### **3. Verificar Status**

Abra o navegador em `http://localhost:5000` e:
- 🟢 **Verde** = Câmera online (última resposta < 15 min)
- 🔴 **Vermelho** = Câmera offline (última resposta > 15 min)

---

## 📊 Estrutura de Dados

### **Metadados (camera_metadata.json)**

```json
{
  "Salvador_Av_ACM_P1": {
    "nome_completo": "BK - Salvador Av ACM_P1",
    "lugar": "Drive_Thru",
    "area": "Pedido",
    "ultima_resposta": "2025-12-27 16:21:45",  ← CAMPO CRÍTICO
    "ip_local": "172.18.0.4",
    "ip_internet": "187.29.40.134",
    "mac_address": "02:42:ac:12:00:04",
    "temperatura_cpu": "0,00",
    "uuid": "1161727969480FABKHMVBAXZ",
    "versao_sistema": "DTRHU-3.7.1"
  }
}
```

### **API Response (/api/cameras)**

```json
{
  "id": "Salvador_Av_ACM_P1_1735320105",
  "base_id": "Salvador_Av_ACM_P1",
  "loja": "Salvador_Av_ACM",
  "position": "P1",
  "metadata": { ... },
  "online": true  ← NOVO CAMPO (true/false/null)
}
```

---

## 🎯 Vantagens

| Característica | Antes | Agora ⭐ |
|----------------|-------|----------|
| **Monitoramento em Tempo Real** | ❌ | ✅ |
| **Identificação Visual de Problemas** | ❌ | ✅ |
| **Validação Pós-Download** | Manual | Automática ✅ |
| **Badge na Interface** | ❌ | 🟢🔴 ✅ |
| **Baseado em Metadados Reais** | ❌ | ✅ |

---

## 🚨 Troubleshooting

### **Problema: Nenhuma câmera mostra status**

**Causa:** Metadados não foram extraídos

**Solução:**
```bash
./executar_paralelo_com_metadados.sh
```

---

### **Problema: Todas offline mesmo após download**

**Possíveis Causas:**

1. **Fuso horário do servidor diferente:**
   - Verificar: `date` no terminal
   - Ajustar se necessário

2. **Formato de data incorreto em `ultima_resposta`:**
   - Verificar: `cat data/camera_metadata.json | grep ultima_resposta | head -1`
   - Formato esperado: `"2025-12-27 16:21:45"`

3. **Timeout muito curto:**
   - Aumentar `TIMEOUT_MINUTOS` em `app.py`

---

### **Problema: Badge não aparece**

**Verificar:**

1. Metadados estão carregados:
   ```bash
   curl http://localhost:5000/api/cameras | grep -o '"online":[^,]*' | head
   ```
   Deve mostrar: `"online":true` ou `"online":false`

2. CSS foi carregado corretamente:
   - Ctrl+Shift+R para limpar cache do navegador

3. Console do navegador (F12) para erros JavaScript

---

## 📈 Melhorias Futuras (Opcionais)

- [ ] **Filtro de Status**: Mostrar apenas câmeras online ou offline
- [ ] **Alertas**: Notificar quando câmera ficar offline
- [ ] **Histórico**: Registrar quando câmera ficou offline
- [ ] **Tempo Real**: Atualização automática sem refresh
- [ ] **Dashboard de Monitoramento**: Painel dedicado para status
- [ ] **Notificações**: Email/SMS quando câmera ficar offline

---

## ✅ Checklist de Testes

Teste o novo recurso:

- [ ] Executar `./executar_paralelo_com_metadados.sh`
- [ ] Iniciar dashboard: `./start_dashboard.sh`
- [ ] Verificar badges 🟢 Online / 🔴 Offline
- [ ] Câmeras com última resposta recente mostram **🟢 Online**
- [ ] Câmeras com última resposta antiga (>15 min) mostram **🔴 Offline**
- [ ] Badge aparece ao lado do nome da loja
- [ ] Cores corretas (verde/vermelho)
- [ ] Funciona em todas as lojas e posições (P1, P2, P3)

---

## 🎉 Resultado Final

```
═══════════════════════════════════════════════════════════
🎥 Dashboard de Câmeras AIVisual - Status em Tempo Real
═══════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────┐
│ Salvador_Av_ACM  🟢 Online                              │
├─────────────┬─────────────┬─────────────────────────────┤
│ P1          │ P2          │ P3                          │
├─────────────┼─────────────┼─────────────────────────────┤
│ [Imagem]    │ [Imagem]    │ [Imagem]                    │
│ 🟢 Online    │ 🟢 Online    │ 🟢 Online                    │
│ Drive_Thru  │ Drive_Thru  │ Drive_Thru                  │
└─────────────┴─────────────┴─────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Aracaju_Centro  🔴 Offline                              │
├─────────────┬─────────────┬─────────────────────────────┤
│ P1          │ P2          │ P3                          │
├─────────────┼─────────────┼─────────────────────────────┤
│ [Imagem]    │ Sem câmera  │ [Imagem]                    │
│ 🔴 Offline   │             │ 🔴 Offline                   │
│ Salão       │             │ Salão                       │
└─────────────┴─────────────┴─────────────────────────────┘
```

---

**Conclusão:** Agora você pode monitorar visualmente o status de todas as câmeras em tempo real! 🎉

---

**Última atualização**: 2025-12-27
**Versão**: 1.0

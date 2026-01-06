# Reinforcement Learning POC - ORAMIND

Proof of Concept (POC) progressiva de Reinforcement Learning para otimização de estratégias no projeto ORAMIND.

## Sobre

Este projeto contém **3 níveis progressivos** de implementação de RL, do mais simples ao mais complexo, permitindo escolher a abordagem adequada baseada na maturidade dos dados e complexidade do problema.

**Data de criação:** 12/12/2024
**Projeto:** ORAMIND
**Objetivo:** Otimização de estratégias usando aprendizado por reforço

## Arquivos

### 📘 Guia de Decisão
- **`guia_decisao_rl.py`** (16KB) - Comparação detalhada das 3 abordagens
  - Tabela comparativa de complexidade, tempo, dados necessários
  - Árvore de decisão para escolher a melhor abordagem
  - Recomendações baseadas em cenários reais
  - Calculadora de viabilidade

### 🎰 Nível 1: Multi-Armed Bandit
- **`rl_poc_nivel1_bandit.py`** (12KB)
  - **Complexidade:** ⭐☆☆☆☆ (Muito Fácil)
  - **Tempo de desenvolvimento:** 2-4 horas
  - **Dados necessários:** 100-500 tentativas
  - **Quando usar:** Teste A/B de estratégias simples
  - **Limitações:** Não personaliza, não otimiza sequências

### 🎯 Nível 2: Contextual Bandit
- **`rl_poc_nivel2_contextual.py`** (20KB)
  - **Complexidade:** ⭐⭐⭐☆☆ (Médio)
  - **Tempo de desenvolvimento:** 1-2 semanas
  - **Dados necessários:** 1.000-5.000 tentativas
  - **Quando usar:** Personalização por perfil de cliente
  - **Vantagens:** Personaliza ações por contexto
  - **Limitações:** Não otimiza sequências longas

### 🧠 Nível 3: Q-Learning
- **`rl_poc_nivel3_qlearning.py`** (23KB)
  - **Complexidade:** ⭐⭐⭐⭐⭐ (Difícil)
  - **Tempo de desenvolvimento:** 3-4 semanas
  - **Dados necessários:** 5.000-20.000 tentativas
  - **Quando usar:** Otimização de jornadas completas
  - **Vantagens:** Otimiza sequências, personalização avançada
  - **Desafios:** Alta complexidade, requer muito dado

## Comparação Rápida

| Critério | Nível 1 (Bandit) | Nível 2 (Contextual) | Nível 3 (Q-Learning) |
|----------|------------------|----------------------|----------------------|
| **Implementação** | 2-4 horas | 1-2 semanas | 3-4 semanas |
| **Dados Mínimos** | 100-500 | 1.000-5.000 | 5.000-20.000 |
| **Personalização** | ❌ Não | ✅ Por perfil | ✅✅ Avançada |
| **Otimização Sequencial** | ❌ Não | ❌ Não | ✅ Sim |
| **Explicabilidade** | ✅✅✅ Alta | ✅✅ Média | ⚠️ Baixa |
| **Manutenção** | ✅✅✅ Fácil | ✅✅ Média | ⚠️ Complexa |

## Como Usar

### 1. Avalie seu cenário
```bash
python3 guia_decisao_rl.py
```

O guia irá:
- Comparar as 3 abordagens em tabela detalhada
- Fornecer árvore de decisão
- Sugerir a melhor abordagem para seu caso
- Calcular viabilidade baseada em suas respostas

### 2. Execute a POC escolhida

#### Nível 1 - Multi-Armed Bandit
```bash
python3 rl_poc_nivel1_bandit.py
```
**Use quando:**
- Precisa de resultado rápido (2-4 horas)
- Tem poucos dados (100-500 tentativas)
- Quer testar A/B de estratégias
- Não precisa de personalização

#### Nível 2 - Contextual Bandit
```bash
python3 rl_poc_nivel2_contextual.py
```
**Use quando:**
- Tem dados de contexto (perfil, histórico)
- Quer personalizar por tipo de cliente
- Tem 1.000-5.000 tentativas
- Tempo de 1-2 semanas disponível

#### Nível 3 - Q-Learning
```bash
python3 rl_poc_nivel3_qlearning.py
```
**Use quando:**
- Precisa otimizar jornadas completas
- Tem muitos dados (5.000-20.000 tentativas)
- Timeline de 3-4 semanas
- Precisa de personalização avançada

## Estrutura dos Scripts

Todos os scripts seguem a mesma estrutura:

```python
# 1. Configuração e Imports
# 2. Geração de Dados Sintéticos (para demonstração)
# 3. Implementação do Algoritmo RL
# 4. Treinamento e Otimização
# 5. Visualização de Resultados
# 6. Análise de Performance
```

## Dependências

```bash
pip install numpy pandas matplotlib scikit-learn
```

**Versões testadas:**
- Python 3.8+
- NumPy 1.21+
- Pandas 1.3+
- Matplotlib 3.4+
- Scikit-learn 1.0+

## Resultados Esperados

Cada script gera:
- **Gráficos de convergência** - Como o algoritmo aprende ao longo do tempo
- **Métricas de performance** - Taxa de sucesso, recompensa acumulada
- **Análise comparativa** - Performance vs baseline
- **Recomendações** - Melhores ações por contexto (nível 2 e 3)

## Projeto ORAMIND

### Contexto
ORAMIND é um sistema de otimização de estratégias que precisa:
- Aprender as melhores ações baseado em feedback
- Personalizar recomendações por perfil
- Otimizar jornadas completas do usuário
- Balancear exploração vs exploração

### Aplicações
- **Nível 1:** Teste A/B de mensagens/ofertas
- **Nível 2:** Personalização de estratégias por segmento
- **Nível 3:** Otimização de jornadas multicanal

## Árvore de Decisão Simplificada

```
Tem dados de sequências/jornadas?
├── SIM: Nível 3 (Q-Learning)
└── NÃO: Tem dados de contexto/perfil?
    ├── SIM: Nível 2 (Contextual Bandit)
    └── NÃO: Nível 1 (Multi-Armed Bandit)
```

## Próximos Passos

1. **Avaliação:** Execute `guia_decisao_rl.py` para escolher abordagem
2. **Prototipagem:** Teste com dados sintéticos
3. **Validação:** Adapte para dados reais do ORAMIND
4. **Deploy:** Integre com sistema de produção
5. **Monitoramento:** Acompanhe performance e ajuste

## Limitações

### Nível 1 (Bandit)
- ❌ Não considera contexto do usuário
- ❌ Não otimiza sequências
- ✅ Rápido e fácil de implementar

### Nível 2 (Contextual)
- ❌ Não otimiza sequências longas
- ⚠️ Requer engenharia de features
- ✅ Personaliza por perfil

### Nível 3 (Q-Learning)
- ❌ Complexo de debugar
- ❌ Requer muito dado
- ⚠️ Pode demorar para convergir
- ✅ Otimização completa de jornadas

## Referências

- **Multi-Armed Bandit:** Sutton & Barto (2018) - Reinforcement Learning: An Introduction
- **Contextual Bandit:** Li et al. (2010) - Contextual Bandits Approach
- **Q-Learning:** Watkins & Dayan (1992) - Q-Learning Algorithm

## Manutenção

**Criado em:** 12/12/2024
**Última atualização:** 06/01/2026
**Mantido por:** Marcelo
**Status:** ✅ POC Completa

---

**Dúvidas?** Consulte o `guia_decisao_rl.py` para escolher a melhor abordagem!

"""
POC NÍVEL 3: Q-LEARNING (Avançado - RL Completo)
=================================================

QUANDO USAR: Quando você quer otimizar SEQUÊNCIAS de ações ao longo
de uma conversa de negociação, não só a escolha inicial.

EXEMPLO: 
- Turno 1: Cliente diz "não posso pagar" → Agente pergunta "quanto pode?"
- Turno 2: Cliente diz "R$100" → Agente oferece parcelamento
- Turno 3: Cliente aceita → Fechou negócio

COMPLEXIDADE: ⭐⭐⭐⭐☆
TEMPO IMPLEMENTAÇÃO: 3-5 dias
DADOS NECESSÁRIOS: 5000-20000 conversas completas
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import json
from collections import defaultdict, deque
import pickle


@dataclass
class ConversationState:
    """
    Estado da conversa de negociação
    
    Representa onde estamos na negociação e contexto do cliente
    """
    # Contexto do cliente
    valor_divida: float
    tempo_inadimplente: int
    tentativas_anteriores: int
    faixa_renda: str  # 'baixa', 'media', 'alta'
    
    # Estado da conversa
    turno_atual: int
    cliente_interesse: str  # 'nenhum', 'baixo', 'medio', 'alto'
    mencinou_dificuldade: bool
    pediu_desconto: bool
    aceitou_parcelamento: bool
    
    # Histórico de ações
    ofertas_feitas: int
    descontos_oferecidos: int
    
    def to_state_key(self) -> str:
        """
        Converte estado em chave única para Q-table
        
        Discretiza valores contínuos para reduzir espaço de estados
        """
        # Discretiza dívida em faixas
        if self.valor_divida < 500:
            divida_bucket = 'pequena'
        elif self.valor_divida < 2000:
            divida_bucket = 'media'
        else:
            divida_bucket = 'grande'
        
        # Discretiza tempo
        if self.tempo_inadimplente < 30:
            tempo_bucket = 'recente'
        elif self.tempo_inadimplente < 90:
            tempo_bucket = 'medio'
        else:
            tempo_bucket = 'antigo'
        
        # Constrói chave
        key = (
            divida_bucket,
            tempo_bucket,
            self.faixa_renda,
            min(self.turno_atual, 5),  # Limita turnos
            self.cliente_interesse,
            self.mencinou_dificuldade,
            self.pediu_desconto,
            min(self.ofertas_feitas, 3)
        )
        
        return str(key)


@dataclass
class Action:
    """Ação que o agente pode tomar"""
    tipo: str  # 'oferta_integral', 'oferta_desconto', 'oferta_parcelamento', 
               # 'perguntar_capacidade', 'reforcar_urgencia', 'finalizar'
    
    def __hash__(self):
        return hash(self.tipo)
    
    def __eq__(self, other):
        return self.tipo == other.tipo


class QLearningAgent:
    """
    Q-Learning Agent para negociação de dívidas
    
    CONCEITO:
    - Q(s, a) = Valor esperado de tomar ação 'a' no estado 's'
    - Aprende através de experiência: tenta ações, recebe rewards, atualiza Q
    - Equação de atualização:
      Q(s,a) ← Q(s,a) + α[r + γ max_a' Q(s',a') - Q(s,a)]
    
    PARÂMETROS:
    - alpha (α): Learning rate (0.1 = aprende devagar, 0.9 = aprende rápido)
    - gamma (γ): Discount factor (0.9 = valoriza recompensas futuras)
    - epsilon (ε): Exploration rate (0.1 = 10% explora, 90% explora melhor)
    """
    
    def __init__(
        self, 
        actions: List[Action],
        alpha: float = 0.1,
        gamma: float = 0.9,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01
    ):
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Q-table: Q[state][action] = valor
        self.Q = defaultdict(lambda: defaultdict(float))
        
        # Estatísticas
        self.episodes = 0
        self.total_reward = 0
        self.conversions = 0
        
        # Replay buffer para treinar em batch
        self.replay_buffer = deque(maxlen=10000)
        
        self.history = []
        
    def select_action(self, state: ConversationState) -> Action:
        """
        Seleciona ação usando ε-greedy
        
        Args:
            state: Estado atual da conversa
            
        Returns:
            Ação a tomar
        """
        state_key = state.to_state_key()
        
        # ε-greedy
        if np.random.random() < self.epsilon:
            # EXPLORE: Ação aleatória
            action = np.random.choice(self.actions)
            exploration = True
        else:
            # EXPLOIT: Melhor ação conhecida
            q_values = {a: self.Q[state_key][a] for a in self.actions}
            max_q = max(q_values.values()) if q_values else 0
            
            # Se há empate, escolhe aleatório entre os melhores
            best_actions = [a for a, q in q_values.items() if q == max_q]
            action = np.random.choice(best_actions) if best_actions else np.random.choice(self.actions)
            exploration = False
        
        return action
    
    def update(
        self, 
        state: ConversationState,
        action: Action,
        reward: float,
        next_state: Optional[ConversationState],
        done: bool
    ):
        """
        Atualiza Q-value após experiência
        
        Args:
            state: Estado antes da ação
            action: Ação tomada
            reward: Recompensa recebida
            next_state: Estado depois da ação (None se terminou)
            done: Se a conversa terminou
        """
        state_key = state.to_state_key()
        
        # Q-value atual
        current_q = self.Q[state_key][action]
        
        # Q-value do próximo estado
        if done or next_state is None:
            # Se terminou, não há valor futuro
            max_next_q = 0
        else:
            next_state_key = next_state.to_state_key()
            next_q_values = [self.Q[next_state_key][a] for a in self.actions]
            max_next_q = max(next_q_values) if next_q_values else 0
        
        # Q-learning update
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.Q[state_key][action] = new_q
        
        # Salva experiência no replay buffer
        self.replay_buffer.append({
            'state': state_key,
            'action': action,
            'reward': reward,
            'next_state': next_state.to_state_key() if next_state else None,
            'done': done
        })
        
        # Atualiza epsilon (decai exploração)
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def train_on_episode(self, episode_trajectory: List[Dict]):
        """
        Treina em um episódio completo (uma conversa inteira)
        
        Args:
            episode_trajectory: Lista de (state, action, reward, next_state, done)
        """
        self.episodes += 1
        episode_reward = 0
        
        for step in episode_trajectory:
            self.update(
                state=step['state'],
                action=step['action'],
                reward=step['reward'],
                next_state=step.get('next_state'),
                done=step['done']
            )
            episode_reward += step['reward']
        
        self.total_reward += episode_reward
        
        # Marca conversão se reward final foi positivo
        if episode_trajectory[-1]['reward'] > 0:
            self.conversions += 1
        
        # Log
        self.history.append({
            'episode': self.episodes,
            'reward': episode_reward,
            'steps': len(episode_trajectory),
            'epsilon': self.epsilon,
            'conversion': episode_trajectory[-1]['reward'] > 0
        })
    
    def get_policy(self, state: ConversationState) -> Dict[str, float]:
        """
        Retorna política (distribuição de ações) para um estado
        
        Returns:
            Dict com ação -> probabilidade
        """
        state_key = state.to_state_key()
        q_values = {a.tipo: self.Q[state_key][a] for a in self.actions}
        
        return q_values
    
    def get_best_action(self, state: ConversationState) -> Action:
        """
        Retorna melhor ação para um estado (modo produção, sem exploração)
        """
        state_key = state.to_state_key()
        q_values = {a: self.Q[state_key][a] for a in self.actions}
        
        if not q_values:
            return np.random.choice(self.actions)
        
        best_action = max(q_values.items(), key=lambda x: x[1])[0]
        return best_action
    
    def get_stats(self) -> Dict:
        """Estatísticas de treinamento"""
        if self.episodes == 0:
            return {}
        
        return {
            'episodes': self.episodes,
            'avg_reward': self.total_reward / self.episodes,
            'conversion_rate': self.conversions / self.episodes,
            'epsilon': self.epsilon,
            'q_table_size': len(self.Q),
            'unique_states': len(self.Q)
        }
    
    def save_model(self, filepath: str):
        """Salva Q-table e parâmetros"""
        model_data = {
            'Q': dict(self.Q),  # Converte defaultdict para dict
            'alpha': self.alpha,
            'gamma': self.gamma,
            'epsilon': self.epsilon,
            'episodes': self.episodes,
            'stats': self.get_stats()
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Modelo Q-Learning salvo em: {filepath}")


# =============================================================================
# SIMULADOR DE CONVERSAS
# =============================================================================

def simular_conversa_negociacao(
    agent: QLearningAgent,
    cliente_profile: Dict,
    max_turnos: int = 10
) -> List[Dict]:
    """
    Simula uma conversa completa de negociação
    
    Returns:
        Trajetória do episódio (lista de transições)
    """
    # Estado inicial
    state = ConversationState(
        valor_divida=cliente_profile['valor_divida'],
        tempo_inadimplente=cliente_profile['tempo_inadimplente'],
        tentativas_anteriores=cliente_profile['tentativas_anteriores'],
        faixa_renda=cliente_profile['faixa_renda'],
        turno_atual=0,
        cliente_interesse='baixo',  # Começa com baixo interesse
        mencinou_dificuldade=False,
        pediu_desconto=False,
        aceitou_parcelamento=False,
        ofertas_feitas=0,
        descontos_oferecidos=0
    )
    
    trajectory = []
    done = False
    
    for turno in range(max_turnos):
        if done:
            break
        
        # Agente escolhe ação
        action = agent.select_action(state)
        
        # Simula resposta do cliente e novo estado
        next_state, reward, done, info = simular_resposta_cliente(
            state, action, cliente_profile
        )
        
        # Salva transição
        trajectory.append({
            'state': state,
            'action': action,
            'reward': reward,
            'next_state': next_state if not done else None,
            'done': done,
            'info': info
        })
        
        state = next_state
        
        if done:
            break
    
    return trajectory


def simular_resposta_cliente(
    state: ConversationState,
    action: Action,
    cliente_profile: Dict
) -> Tuple[ConversationState, float, bool, Dict]:
    """
    Simula como o cliente responde à ação do agente
    
    Returns:
        (próximo_estado, recompensa, conversa_terminou, info_adicional)
    """
    # Copia estado atual para modificar
    import copy
    next_state = copy.deepcopy(state)
    next_state.turno_atual += 1
    
    reward = 0
    done = False
    info = {}
    
    # Simula resposta baseado na ação
    if action.tipo == 'oferta_integral':
        next_state.ofertas_feitas += 1
        
        # Probabilidade de aceitar integral é baixa
        prob_aceitar = 0.05
        
        # Aumenta se cliente tem alta renda
        if cliente_profile['faixa_renda'] == 'alta':
            prob_aceitar = 0.15
        
        # Reduz se dívida é grande
        if state.valor_divida > 2000:
            prob_aceitar *= 0.5
        
        if np.random.random() < prob_aceitar:
            # SUCESSO!
            reward = 10.0  # Recompensa alta (pagou integral)
            done = True
            info['resultado'] = 'aceitou_integral'
        else:
            # Rejeitou, mas pode ter interesse
            reward = -0.5  # Penalidade pequena por oferta rejeitada
            next_state.cliente_interesse = 'medio'
            next_state.mencinou_dificuldade = True
            info['resultado'] = 'rejeitou_oferta'
    
    elif action.tipo == 'oferta_desconto':
        next_state.ofertas_feitas += 1
        next_state.descontos_oferecidos += 1
        
        # Desconto aumenta chance de aceitação
        prob_aceitar = 0.25
        
        # Se já pediu desconto, chance maior
        if state.pediu_desconto:
            prob_aceitar = 0.45
        
        # Se dívida pequena, chance maior
        if state.valor_divida < 500:
            prob_aceitar = 0.50
        
        if np.random.random() < prob_aceitar:
            # SUCESSO com desconto
            reward = 7.0  # Recompensa boa (mas menos que integral)
            done = True
            info['resultado'] = 'aceitou_desconto'
        else:
            reward = -0.3
            next_state.cliente_interesse = 'medio'
            info['resultado'] = 'rejeitou_desconto'
    
    elif action.tipo == 'oferta_parcelamento':
        next_state.ofertas_feitas += 1
        next_state.aceitou_parcelamento = True
        
        # Parcelamento é bem aceito
        prob_aceitar = 0.35
        
        # Melhor para dívidas grandes
        if state.valor_divida > 2000:
            prob_aceitar = 0.50
        
        # Se renda baixa, prefere parcelar
        if cliente_profile['faixa_renda'] == 'baixa':
            prob_aceitar = 0.55
        
        if np.random.random() < prob_aceitar:
            # SUCESSO parcelado
            reward = 8.0  # Recompensa boa
            done = True
            info['resultado'] = 'aceitou_parcelamento'
        else:
            reward = -0.2
            next_state.cliente_interesse = 'alto'  # Pelo menos está negociando
            info['resultado'] = 'rejeitou_parcelamento'
    
    elif action.tipo == 'perguntar_capacidade':
        # Ação de discovery, sem oferta
        reward = 0.1  # Pequena recompensa por coletar informação
        
        # Cliente revela informação
        next_state.cliente_interesse = 'alto'
        
        # Pode pedir desconto
        if np.random.random() < 0.3:
            next_state.pediu_desconto = True
        
        info['resultado'] = 'cliente_respondeu'
    
    elif action.tipo == 'reforcar_urgencia':
        # Tenta criar senso de urgência
        
        # Pode funcionar ou irritar
        if np.random.random() < 0.6:
            reward = 0.2
            next_state.cliente_interesse = 'medio'
            info['resultado'] = 'urgencia_funcionou'
        else:
            reward = -1.0  # Penalidade por irritar cliente
            next_state.cliente_interesse = 'nenhum'
            done = True  # Cliente desistiu
            info['resultado'] = 'cliente_irritado'
    
    elif action.tipo == 'finalizar':
        # Agente decide encerrar sem acordo
        reward = -2.0  # Penalidade por desistir
        done = True
        info['resultado'] = 'sem_acordo'
    
    # Penalidades por gastar muito tempo
    if next_state.turno_atual > 7:
        reward -= 0.5  # Conversa muito longa
    
    # Se fez muitas ofertas sem sucesso, perde valor
    if next_state.ofertas_feitas > 4:
        reward -= 1.0
    
    return next_state, reward, done, info


# =============================================================================
# TREINAMENTO
# =============================================================================

def main():
    """Treina o Q-Learning agent"""
    
    print("="*80)
    print("POC NÍVEL 3: Q-LEARNING - Agente de Negociação Oramind")
    print("="*80)
    print()
    
    # Define ações disponíveis
    actions = [
        Action('oferta_integral'),
        Action('oferta_desconto'),
        Action('oferta_parcelamento'),
        Action('perguntar_capacidade'),
        Action('reforcar_urgencia'),
        Action('finalizar')
    ]
    
    # Inicializa agente
    agent = QLearningAgent(
        actions=actions,
        alpha=0.1,      # Learning rate
        gamma=0.9,      # Discount factor
        epsilon=0.3,    # Exploração inicial alta
        epsilon_decay=0.995
    )
    
    print(f"🤖 Q-Learning Agent inicializado")
    print(f"   • Ações disponíveis: {len(actions)}")
    print(f"   • Alpha (learning rate): {agent.alpha}")
    print(f"   • Gamma (discount): {agent.gamma}")
    print(f"   • Epsilon inicial: {agent.epsilon}")
    print()
    
    # Treina com conversas simuladas
    NUM_EPISODIOS = 3000
    
    print(f"🚀 Treinando com {NUM_EPISODIOS} conversas simuladas...")
    print()
    
    for episodio in range(NUM_EPISODIOS):
        # Gera perfil de cliente aleatório
        cliente = {
            'valor_divida': float(np.random.lognormal(6, 1)),
            'tempo_inadimplente': int(np.random.exponential(90)),
            'tentativas_anteriores': int(np.random.poisson(2)),
            'faixa_renda': np.random.choice(['baixa', 'media', 'alta'])
        }
        
        # Simula conversa completa
        trajectory = simular_conversa_negociacao(agent, cliente, max_turnos=10)
        
        # Treina com essa experiência
        agent.train_on_episode(trajectory)
        
        # Progress
        if (episodio + 1) % 300 == 0:
            stats = agent.get_stats()
            print(f"Episódio {episodio+1:4d} | "
                  f"Taxa Conversão: {stats['conversion_rate']*100:.1f}% | "
                  f"Reward Médio: {stats['avg_reward']:.2f} | "
                  f"Epsilon: {stats['epsilon']:.3f}")
    
    print()
    print("="*80)
    print("📊 RESULTADOS DO TREINAMENTO")
    print("="*80)
    print()
    
    stats = agent.get_stats()
    print(f"✅ Episódios treinados: {stats['episodes']}")
    print(f"✅ Taxa de conversão: {stats['conversion_rate']*100:.1f}%")
    print(f"✅ Reward médio: {stats['avg_reward']:.2f}")
    print(f"✅ Estados únicos descobertos: {stats['unique_states']}")
    print(f"✅ Epsilon final: {stats['epsilon']:.3f}")
    print()
    
    # Testa política aprendida
    print("="*80)
    print("🧪 TESTANDO POLÍTICA APRENDIDA")
    print("="*80)
    print()
    
    # Cenário de teste 1
    test_state1 = ConversationState(
        valor_divida=800,
        tempo_inadimplente=60,
        tentativas_anteriores=2,
        faixa_renda='media',
        turno_atual=1,
        cliente_interesse='medio',
        mencinou_dificuldade=True,
        pediu_desconto=False,
        aceitou_parcelamento=False,
        ofertas_feitas=0,
        descontos_oferecidos=0
    )
    
    policy1 = agent.get_policy(test_state1)
    best_action1 = agent.get_best_action(test_state1)
    
    print("📋 Cenário 1: Dívida média (R$800), cliente com dificuldade")
    print(f"   ✅ Melhor ação: {best_action1.tipo}")
    print(f"   📊 Q-values:")
    for acao, q in sorted(policy1.items(), key=lambda x: x[1], reverse=True):
        print(f"      • {acao:25s}: {q:6.3f}")
    print()
    
    # Salva modelo
    agent.save_model('qlearning_model.pkl')
    
    # Análise de convergência
    history_df = pd.DataFrame(agent.history)
    
    print("="*80)
    print("📈 ANÁLISE DE CONVERGÊNCIA")
    print("="*80)
    print()
    
    # Últimos 500 episódios
    recent = history_df.tail(500)
    print(f"🎯 Performance nos últimos 500 episódios:")
    print(f"   • Taxa de conversão: {recent['conversion'].mean()*100:.1f}%")
    print(f"   • Reward médio: {recent['reward'].mean():.2f}")
    print(f"   • Passos médios por conversa: {recent['steps'].mean():.1f}")
    print()
    
    print("="*80)
    print("💡 INSIGHTS")
    print("="*80)
    print()
    print("✅ Q-Learning aprende SEQUÊNCIAS ótimas de ações")
    print("✅ Otimiza não só conversão, mas também eficiência (menos turnos)")
    print("✅ Descobre estratégias complexas (ex: perguntar antes de oferecer)")
    print("✅ Balanceia exploração/exploitação automaticamente")
    print()
    print("⚠️  ATENÇÃO: Espaço de estados pode explodir com muitas features")
    print("⚠️  Solução: Deep Q-Learning (DQN) para espaços muito grandes")
    print()


if __name__ == "__main__":
    main()


# =============================================================================
# INTEGRAÇÃO COM ORAMIND
# =============================================================================

"""
USO EM PRODUÇÃO:

1. Treina offline com dados históricos de conversas:

    agent = QLearningAgent(actions=ACTIONS)
    
    for conversa_historica in dataset:
        trajectory = processar_conversa(conversa_historica)
        agent.train_on_episode(trajectory)
    
    agent.save_model('models/qlearning_production.pkl')


2. Em tempo real, no Agente de Negociação:

    from rl_poc_nivel3_qlearning import QLearningAgent
    
    # Carrega modelo treinado
    agent = QLearningAgent.load_model('models/qlearning_production.pkl')
    
    # Mantém estado da conversa
    state = ConversationState(...)
    
    # Loop de conversa
    while not done:
        # Decide próxima ação
        action = agent.get_best_action(state)  # Sem exploração em prod
        
        # Executa ação
        response = executar_acao(action, cliente)
        
        # Atualiza estado baseado em resposta do cliente
        next_state, reward, done = processar_resposta(response)
        
        # Aprende online (opcional)
        agent.update(state, action, reward, next_state, done)
        
        state = next_state


3. Re-treina periodicamente:

    # Diariamente, re-treina com novas conversas
    novas_conversas = load_today_conversations()
    for conversa in novas_conversas:
        agent.train_on_episode(processar_conversa(conversa))
    
    agent.save_model('models/qlearning_latest.pkl')
"""

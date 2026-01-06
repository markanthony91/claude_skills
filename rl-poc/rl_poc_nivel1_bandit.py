"""
POC NÍVEL 1: MULTI-ARMED BANDIT (Mais Simples)
===============================================

QUANDO USAR: Quando você tem poucas variáveis de decisão e quer
testar qual estratégia funciona melhor SEM considerar o perfil do cliente.

EXEMPLO: Testar qual dos 5 templates de mensagem tem melhor conversão.

COMPLEXIDADE: ⭐☆☆☆☆
TEMPO IMPLEMENTAÇÃO: 2-4 horas
DADOS NECESSÁRIOS: 100-500 tentativas por braço
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict
import json


@dataclass
class BanditArm:
    """Representa uma estratégia de cobrança"""
    name: str
    total_pulls: int = 0
    total_reward: float = 0.0
    conversions: int = 0
    
    @property
    def win_rate(self) -> float:
        """Taxa de conversão"""
        return self.conversions / self.total_pulls if self.total_pulls > 0 else 0.0
    
    @property
    def average_reward(self) -> float:
        """Recompensa média"""
        return self.total_reward / self.total_pulls if self.total_pulls > 0 else 0.0


class EpsilonGreedyBandit:
    """
    Multi-Armed Bandit com estratégia Epsilon-Greedy
    
    CONCEITO:
    - Com probabilidade (1-epsilon): Escolhe a melhor estratégia conhecida (exploit)
    - Com probabilidade epsilon: Escolhe estratégia aleatória (explore)
    
    PARÂMETROS:
    - epsilon: Taxa de exploração (0.1 = 10% explora, 90% explora melhor)
    - decay_rate: Quanto epsilon diminui ao longo do tempo
    """
    
    def __init__(self, strategies: List[str], epsilon: float = 0.1, decay_rate: float = 0.995):
        self.arms = {name: BanditArm(name) for name in strategies}
        self.epsilon = epsilon
        self.initial_epsilon = epsilon
        self.decay_rate = decay_rate
        self.total_pulls = 0
        self.history = []
        
    def select_strategy(self) -> str:
        """
        Seleciona qual estratégia usar
        
        Returns:
            Nome da estratégia selecionada
        """
        # Explora (aleatório) ou Explota (melhor)
        if np.random.random() < self.epsilon:
            # EXPLORE: Escolhe aleatório
            strategy = np.random.choice(list(self.arms.keys()))
            exploration = True
        else:
            # EXPLOIT: Escolhe a melhor
            strategy = max(self.arms.items(), key=lambda x: x[1].average_reward)[0]
            exploration = False
        
        self.total_pulls += 1
        
        # Log da decisão
        self.history.append({
            'pull': self.total_pulls,
            'strategy': strategy,
            'exploration': exploration,
            'epsilon': self.epsilon
        })
        
        return strategy
    
    def update(self, strategy: str, cliente_pagou: bool, valor_pago: float = 0.0):
        """
        Atualiza as estatísticas após receber feedback
        
        Args:
            strategy: Estratégia que foi usada
            cliente_pagou: Se o cliente pagou ou não
            valor_pago: Valor que o cliente pagou (opcional)
        """
        arm = self.arms[strategy]
        
        # Recompensa: 1 se pagou, 0 se não pagou
        # Ou pode usar o valor_pago diretamente
        reward = 1.0 if cliente_pagou else 0.0
        # reward = valor_pago / 1000.0  # Normaliza valor para 0-1
        
        arm.total_pulls += 1
        arm.total_reward += reward
        if cliente_pagou:
            arm.conversions += 1
        
        # Decay do epsilon (explora menos com o tempo)
        self.epsilon = max(0.01, self.epsilon * self.decay_rate)
        
        # Log do resultado
        self.history[-1].update({
            'cliente_pagou': cliente_pagou,
            'valor_pago': valor_pago,
            'reward': reward,
            'arm_pulls': arm.total_pulls,
            'arm_win_rate': arm.win_rate
        })
    
    def get_best_strategy(self) -> str:
        """Retorna a estratégia com melhor performance"""
        return max(self.arms.items(), key=lambda x: x[1].average_reward)[0]
    
    def get_stats(self) -> pd.DataFrame:
        """Retorna estatísticas de todas as estratégias"""
        data = []
        for name, arm in self.arms.items():
            data.append({
                'Estratégia': name,
                'Tentativas': arm.total_pulls,
                'Conversões': arm.conversions,
                'Taxa Conversão': f"{arm.win_rate*100:.1f}%",
                'Reward Médio': f"{arm.average_reward:.3f}",
                'Reward Total': f"{arm.total_reward:.2f}"
            })
        return pd.DataFrame(data).sort_values('Reward Médio', ascending=False)
    
    def save_model(self, filepath: str):
        """Salva o modelo treinado"""
        model_data = {
            'epsilon': self.epsilon,
            'initial_epsilon': self.initial_epsilon,
            'decay_rate': self.decay_rate,
            'total_pulls': self.total_pulls,
            'arms': {
                name: {
                    'total_pulls': arm.total_pulls,
                    'total_reward': arm.total_reward,
                    'conversions': arm.conversions
                }
                for name, arm in self.arms.items()
            },
            'history': self.history
        }
        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=2)
        print(f"✅ Modelo salvo em: {filepath}")


# =============================================================================
# EXEMPLO DE USO: Sistema de Cobrança
# =============================================================================

def simular_cliente_responde(estrategia: str) -> tuple[bool, float]:
    """
    Simula se o cliente paga baseado na estratégia
    
    Na vida real, isso viria do sistema de cobrança
    Aqui simulamos com probabilidades diferentes por estratégia
    """
    # Probabilidades reais de conversão por estratégia (desconhecidas a priori)
    PROBABILIDADES = {
        'formal_rigido': 0.15,      # Estratégia muito formal
        'empático_flexível': 0.32,   # Estratégia empática (melhor)
        'agressivo': 0.08,           # Estratégia agressiva (pior)
        'desconto_imediato': 0.28,   # Oferece desconto logo
        'parcelamento': 0.25         # Foca em parcelamento
    }
    
    # Valores médios pagos quando converte
    VALORES_MEDIOS = {
        'formal_rigido': 500,
        'empático_flexível': 450,
        'agressivo': 400,
        'desconto_imediato': 350,  # Desconto reduz valor
        'parcelamento': 480
    }
    
    prob = PROBABILIDADES[estrategia]
    cliente_pagou = np.random.random() < prob
    
    if cliente_pagou:
        # Adiciona variação no valor pago
        valor_base = VALORES_MEDIOS[estrategia]
        valor_pago = valor_base * np.random.uniform(0.8, 1.2)
    else:
        valor_pago = 0.0
    
    return cliente_pagou, valor_pago


def main():
    """Executa a simulação completa"""
    
    print("="*70)
    print("POC NÍVEL 1: MULTI-ARMED BANDIT - Sistema de Cobrança Oramind")
    print("="*70)
    print()
    
    # Define as estratégias disponíveis
    estrategias = [
        'formal_rigido',
        'empático_flexível',
        'agressivo',
        'desconto_imediato',
        'parcelamento'
    ]
    
    # Inicializa o bandit
    bandit = EpsilonGreedyBandit(
        strategies=estrategias,
        epsilon=0.2,        # 20% de exploração inicial
        decay_rate=0.995    # Decai lentamente
    )
    
    print(f"📊 Iniciando com {len(estrategias)} estratégias")
    print(f"🔍 Epsilon inicial: {bandit.epsilon} (taxa de exploração)")
    print()
    
    # Simula 1000 tentativas de cobrança
    NUM_TENTATIVAS = 1000
    
    print(f"🚀 Simulando {NUM_TENTATIVAS} tentativas de cobrança...")
    print()
    
    for i in range(NUM_TENTATIVAS):
        # 1. Bandit escolhe qual estratégia usar
        estrategia_escolhida = bandit.select_strategy()
        
        # 2. Sistema executa a cobrança com essa estratégia
        cliente_pagou, valor_pago = simular_cliente_responde(estrategia_escolhida)
        
        # 3. Bandit aprende com o resultado
        bandit.update(estrategia_escolhida, cliente_pagou, valor_pago)
        
        # Mostra progresso a cada 100 tentativas
        if (i + 1) % 100 == 0:
            melhor = bandit.get_best_strategy()
            print(f"Tentativa {i+1:4d} | Melhor estratégia até agora: {melhor} | Epsilon: {bandit.epsilon:.3f}")
    
    print()
    print("="*70)
    print("📊 RESULTADOS FINAIS")
    print("="*70)
    print()
    
    # Mostra estatísticas
    stats = bandit.get_stats()
    print(stats.to_string(index=False))
    print()
    
    # Mostra a melhor estratégia
    melhor_estrategia = bandit.get_best_strategy()
    print(f"🏆 MELHOR ESTRATÉGIA: {melhor_estrategia}")
    print()
    
    # Detalhes da melhor
    melhor_arm = bandit.arms[melhor_estrategia]
    print(f"   • Taxa de Conversão: {melhor_arm.win_rate*100:.1f}%")
    print(f"   • Tentativas: {melhor_arm.total_pulls}")
    print(f"   • Conversões: {melhor_arm.conversions}")
    print(f"   • Reward Médio: {melhor_arm.average_reward:.3f}")
    print()
    
    # Salva o modelo
    bandit.save_model('bandit_model.json')
    
    # Análise de exploração vs exploitação
    history_df = pd.DataFrame(bandit.history)
    exploration_rate = history_df['exploration'].mean()
    print(f"📈 Taxa de exploração durante treinamento: {exploration_rate*100:.1f}%")
    print(f"📈 Epsilon final: {bandit.epsilon:.3f}")
    print()
    
    print("="*70)
    print("💡 PRÓXIMOS PASSOS")
    print("="*70)
    print()
    print("1. Integre com seu sistema real de cobrança")
    print("2. Substitua simular_cliente_responde() com dados reais")
    print("3. Ajuste epsilon e decay_rate baseado em dados reais")
    print("4. Adicione mais estratégias conforme testar")
    print("5. Considere evoluir para Contextual Bandit (Nível 2)")
    print()


if __name__ == "__main__":
    main()


# =============================================================================
# COMO USAR NO SISTEMA REAL
# =============================================================================

"""
INTEGRAÇÃO COM ORAMIND:

1. No Agente de Estratégia:
   
   # Inicializa o bandit uma vez
   bandit = EpsilonGreedyBandit(strategies=ESTRATEGIAS_DISPONIVEIS)
   
   # Para cada novo cliente
   estrategia = bandit.select_strategy()
   
   # Usa a estratégia selecionada
   mensagem = gerar_mensagem(cliente, estrategia)
   enviar_mensagem(cliente, mensagem)
   
   # Armazena: cliente_id, estrategia, timestamp

2. No Callback de Pagamento:
   
   # Quando cliente paga (ou não paga após X dias)
   bandit.update(
       strategy=estrategia_usada,
       cliente_pagou=True,
       valor_pago=500.00
   )
   
3. Persistência:
   
   # A cada 100 updates ou fim do dia
   bandit.save_model('models/bandit_latest.json')
   
   # Para carregar
   # TODO: Implementar load_model()

4. Monitoring:
   
   # Dashboard diário
   stats = bandit.get_stats()
   enviar_para_dashboard(stats)
   
   # Alerta se alguma estratégia está muito ruim
   if any(arm.win_rate < 0.05 for arm in bandit.arms.values()):
       alertar_time()
"""

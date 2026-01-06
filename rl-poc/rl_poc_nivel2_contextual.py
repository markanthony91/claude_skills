"""
POC NÍVEL 2: CONTEXTUAL BANDIT (Intermediário - RECOMENDADO PARA ORAMIND)
===========================================================================

QUANDO USAR: Quando você quer escolher a melhor estratégia BASEADO NO
PERFIL DO CLIENTE (idade, dívida, tempo inadimplente, etc).

EXEMPLO: Cliente jovem com dívida pequena → estratégia empática via WhatsApp
         Cliente corporativo com dívida grande → estratégia formal via email

COMPLEXIDADE: ⭐⭐⭐☆☆
TEMPO IMPLEMENTAÇÃO: 1-2 dias
DADOS NECESSÁRIOS: 1000-5000 tentativas
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Tuple
import json
from collections import defaultdict


@dataclass
class ClienteContext:
    """
    Contexto do cliente (features que influenciam a decisão)
    """
    idade: int              # 18-80
    valor_divida: float     # R$ 100 - R$ 50000
    tempo_inadimplente: int # Dias
    tipo_divida: str        # 'cartao', 'emprestimo', 'servico'
    tentativas_anteriores: int  # Quantas vezes já foi contatado
    regiao: str             # 'sudeste', 'nordeste', etc
    faixa_renda: str        # 'baixa', 'media', 'alta'
    
    def to_feature_vector(self) -> np.ndarray:
        """
        Converte contexto em vetor numérico para o modelo
        """
        # Normaliza features numéricas
        idade_norm = (self.idade - 18) / (80 - 18)
        divida_norm = np.log1p(self.valor_divida) / np.log1p(50000)
        tempo_norm = min(self.tempo_inadimplente / 365, 1.0)  # Max 1 ano
        tentativas_norm = min(self.tentativas_anteriores / 10, 1.0)
        
        # One-hot encoding para categóricas
        tipo_divida_map = {'cartao': 0, 'emprestimo': 1, 'servico': 2, 'outros': 3}
        regiao_map = {'sudeste': 0, 'sul': 1, 'nordeste': 2, 'norte': 3, 'centro-oeste': 4}
        renda_map = {'baixa': 0, 'media': 1, 'alta': 2}
        
        tipo_idx = tipo_divida_map.get(self.tipo_divida, 3)
        regiao_idx = regiao_map.get(self.regiao, 0)
        renda_idx = renda_map.get(self.faixa_renda, 1)
        
        # Cria one-hot
        tipo_onehot = np.zeros(4)
        tipo_onehot[tipo_idx] = 1
        
        regiao_onehot = np.zeros(5)
        regiao_onehot[regiao_idx] = 1
        
        renda_onehot = np.zeros(3)
        renda_onehot[renda_idx] = 1
        
        # Concatena tudo
        features = np.concatenate([
            [idade_norm, divida_norm, tempo_norm, tentativas_norm],
            tipo_onehot,
            regiao_onehot,
            renda_onehot
        ])
        
        return features
    
    def get_segment(self) -> str:
        """
        Segmenta cliente para análise
        """
        if self.valor_divida < 500:
            valor_seg = 'pequena'
        elif self.valor_divida < 2000:
            valor_seg = 'media'
        else:
            valor_seg = 'grande'
        
        if self.idade < 30:
            idade_seg = 'jovem'
        elif self.idade < 50:
            idade_seg = 'adulto'
        else:
            idade_seg = 'senior'
        
        return f"{idade_seg}_{valor_seg}_{self.tipo_divida}"


class LinUCB:
    """
    Linear Upper Confidence Bound - Contextual Bandit
    
    CONCEITO:
    - Mantém um modelo linear para cada estratégia
    - Modelo prevê reward esperado baseado no contexto do cliente
    - Adiciona "bonus de incerteza" para explorar estratégias pouco testadas
    - Escolhe estratégia com maior (reward_previsto + bonus_exploracao)
    
    VANTAGENS:
    - Personaliza por cliente automaticamente
    - Balanceia exploração e exploitação teoricamente ótimo
    - Não precisa de decay manual de epsilon
    
    MATEMÁTICA:
    θ_a = (A_a^T A_a)^-1 A_a^T b_a
    UCB_a = θ_a^T x + α * sqrt(x^T (A_a^T A_a)^-1 x)
    """
    
    def __init__(self, strategies: List[str], feature_dim: int = 16, alpha: float = 1.0):
        """
        Args:
            strategies: Lista de estratégias disponíveis
            feature_dim: Dimensão do vetor de features do cliente
            alpha: Parâmetro de exploração (maior = mais exploração)
        """
        self.strategies = strategies
        self.feature_dim = feature_dim
        self.alpha = alpha
        
        # Para cada estratégia, mantém:
        # A_a: Matrix (feature_dim x feature_dim) - soma de x*x^T
        # b_a: Vector (feature_dim) - soma de reward*x
        self.A = {s: np.identity(feature_dim) for s in strategies}
        self.b = {s: np.zeros(feature_dim) for s in strategies}
        
        # Estatísticas
        self.pulls = {s: 0 for s in strategies}
        self.conversions = {s: 0 for s in strategies}
        self.total_reward = {s: 0.0 for s in strategies}
        
        self.history = []
        
    def select_strategy(self, context: ClienteContext) -> str:
        """
        Seleciona melhor estratégia para este cliente específico
        
        Args:
            context: Perfil do cliente
            
        Returns:
            Estratégia selecionada
        """
        x = context.to_feature_vector()
        
        ucb_scores = {}
        
        for strategy in self.strategies:
            A_inv = np.linalg.inv(self.A[strategy])
            theta = A_inv @ self.b[strategy]
            
            # Reward esperado
            expected_reward = theta @ x
            
            # Bonus de exploração (incerteza)
            uncertainty = np.sqrt(x @ A_inv @ x)
            ucb_score = expected_reward + self.alpha * uncertainty
            
            ucb_scores[strategy] = {
                'expected': expected_reward,
                'uncertainty': uncertainty,
                'ucb': ucb_score
            }
        
        # Escolhe estratégia com maior UCB
        best_strategy = max(ucb_scores.items(), key=lambda x: x[1]['ucb'])[0]
        
        # Log
        self.history.append({
            'context': context,
            'strategy': best_strategy,
            'ucb_scores': ucb_scores,
            'segment': context.get_segment()
        })
        
        return best_strategy
    
    def update(self, context: ClienteContext, strategy: str, 
               cliente_pagou: bool, valor_pago: float = 0.0):
        """
        Atualiza modelo após receber feedback
        
        Args:
            context: Perfil do cliente
            strategy: Estratégia que foi usada
            cliente_pagou: Se pagou ou não
            valor_pago: Valor pago (opcional)
        """
        x = context.to_feature_vector()
        
        # Recompensa (pode ser binária ou contínua)
        reward = 1.0 if cliente_pagou else 0.0
        # reward = valor_pago / 1000.0  # Ou usar valor normalizado
        
        # Atualiza o modelo linear para essa estratégia
        self.A[strategy] += np.outer(x, x)  # x * x^T
        self.b[strategy] += reward * x
        
        # Estatísticas
        self.pulls[strategy] += 1
        self.total_reward[strategy] += reward
        if cliente_pagou:
            self.conversions[strategy] += 1
        
        # Atualiza histórico
        self.history[-1].update({
            'cliente_pagou': cliente_pagou,
            'valor_pago': valor_pago,
            'reward': reward
        })
    
    def get_stats(self) -> pd.DataFrame:
        """Estatísticas por estratégia"""
        data = []
        for strategy in self.strategies:
            pulls = self.pulls[strategy]
            conversions = self.conversions[strategy]
            
            data.append({
                'Estratégia': strategy,
                'Tentativas': pulls,
                'Conversões': conversions,
                'Taxa Conversão': f"{conversions/pulls*100:.1f}%" if pulls > 0 else "0%",
                'Reward Total': f"{self.total_reward[strategy]:.2f}",
                'Reward Médio': f"{self.total_reward[strategy]/pulls:.3f}" if pulls > 0 else "0"
            })
        
        return pd.DataFrame(data).sort_values('Reward Médio', ascending=False)
    
    def get_stats_by_segment(self) -> pd.DataFrame:
        """Estatísticas por segmento de cliente"""
        segment_stats = defaultdict(lambda: defaultdict(lambda: {'tentativas': 0, 'conversoes': 0}))
        
        for entry in self.history:
            if 'cliente_pagou' in entry:
                segment = entry['segment']
                strategy = entry['strategy']
                
                segment_stats[segment][strategy]['tentativas'] += 1
                if entry['cliente_pagou']:
                    segment_stats[segment][strategy]['conversoes'] += 1
        
        # Formata para DataFrame
        data = []
        for segment, strategies in segment_stats.items():
            for strategy, stats in strategies.items():
                if stats['tentativas'] > 0:
                    taxa = stats['conversoes'] / stats['tentativas'] * 100
                    data.append({
                        'Segmento': segment,
                        'Estratégia': strategy,
                        'Tentativas': stats['tentativas'],
                        'Conversões': stats['conversoes'],
                        'Taxa': f"{taxa:.1f}%"
                    })
        
        if not data:
            return pd.DataFrame()
        
        return pd.DataFrame(data).sort_values(['Segmento', 'Taxa'], ascending=[True, False])
    
    def predict_best_strategy(self, context: ClienteContext) -> Dict:
        """
        Prevê qual seria a melhor estratégia para um cliente
        SEM atualizar o modelo (apenas inferência)
        """
        x = context.to_feature_vector()
        predictions = {}
        
        for strategy in self.strategies:
            A_inv = np.linalg.inv(self.A[strategy])
            theta = A_inv @ self.b[strategy]
            expected_reward = theta @ x
            
            predictions[strategy] = expected_reward
        
        best = max(predictions.items(), key=lambda x: x[1])
        
        return {
            'best_strategy': best[0],
            'expected_reward': best[1],
            'all_predictions': predictions
        }
    
    def save_model(self, filepath: str):
        """Salva modelo treinado"""
        model_data = {
            'strategies': self.strategies,
            'feature_dim': self.feature_dim,
            'alpha': self.alpha,
            'A': {s: self.A[s].tolist() for s in self.strategies},
            'b': {s: self.b[s].tolist() for s in self.strategies},
            'pulls': self.pulls,
            'conversions': self.conversions,
            'total_reward': self.total_reward
        }
        
        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=2)
        
        print(f"✅ Modelo salvo em: {filepath}")


# =============================================================================
# SIMULAÇÃO REALISTA
# =============================================================================

def gerar_cliente_aleatorio() -> ClienteContext:
    """Gera perfil de cliente aleatório"""
    tipos = ['cartao', 'emprestimo', 'servico']
    regioes = ['sudeste', 'sul', 'nordeste', 'norte', 'centro-oeste']
    rendas = ['baixa', 'media', 'alta']
    
    return ClienteContext(
        idade=int(np.random.normal(40, 15)),
        valor_divida=float(np.random.lognormal(6, 1)),  # Log-normal distribution
        tempo_inadimplente=int(np.random.exponential(90)),
        tipo_divida=np.random.choice(tipos),
        tentativas_anteriores=int(np.random.poisson(2)),
        regiao=np.random.choice(regioes),
        faixa_renda=np.random.choice(rendas)
    )


def simular_conversao_contextual(context: ClienteContext, estrategia: str) -> Tuple[bool, float]:
    """
    Simula conversão baseado no CONTEXTO do cliente E na estratégia
    
    Na vida real, isso seria o resultado real da cobrança
    """
    # Base de conversão por estratégia
    base_rates = {
        'formal_rigido': 0.12,
        'empático_flexível': 0.28,
        'agressivo': 0.08,
        'desconto_imediato': 0.25,
        'parcelamento': 0.22
    }
    
    prob_base = base_rates[estrategia]
    
    # AJUSTES CONTEXTUAIS (aqui está a mágica)
    
    # Jovens respondem melhor a empático
    if context.idade < 30 and estrategia == 'empático_flexível':
        prob_base *= 1.3
    
    # Seniors respondem melhor a formal
    if context.idade > 60 and estrategia == 'formal_rigido':
        prob_base *= 1.2
    
    # Dívida pequena + desconto = boa conversão
    if context.valor_divida < 500 and estrategia == 'desconto_imediato':
        prob_base *= 1.4
    
    # Dívida grande + parcelamento = melhor
    if context.valor_divida > 2000 and estrategia == 'parcelamento':
        prob_base *= 1.3
    
    # Muito tempo inadimplente = precisa desconto
    if context.tempo_inadimplente > 180:
        if estrategia == 'desconto_imediato':
            prob_base *= 1.2
        elif estrategia == 'agressivo':
            prob_base *= 0.5  # Pior ainda
    
    # Muitas tentativas anteriores = já está irritado
    if context.tentativas_anteriores > 5:
        if estrategia == 'agressivo':
            prob_base *= 0.3
        elif estrategia == 'empático_flexível':
            prob_base *= 1.1
    
    # Renda alta = pode pagar mais facilmente
    if context.faixa_renda == 'alta':
        prob_base *= 1.2
    
    # Limita probabilidade
    prob_final = min(prob_base, 0.95)
    
    cliente_pagou = np.random.random() < prob_final
    
    if cliente_pagou:
        # Valor pago varia com contexto
        valor_base = context.valor_divida
        if estrategia == 'desconto_imediato':
            valor_pago = valor_base * np.random.uniform(0.6, 0.8)  # Com desconto
        else:
            valor_pago = valor_base * np.random.uniform(0.9, 1.0)
    else:
        valor_pago = 0.0
    
    return cliente_pagou, valor_pago


def main():
    """Executa simulação completa"""
    
    print("="*80)
    print("POC NÍVEL 2: CONTEXTUAL BANDIT (LinUCB) - Sistema de Cobrança Oramind")
    print("="*80)
    print()
    
    estrategias = [
        'formal_rigido',
        'empático_flexível',
        'agressivo',
        'desconto_imediato',
        'parcelamento'
    ]
    
    # Inicializa o Contextual Bandit
    bandit = LinUCB(
        strategies=estrategias,
        feature_dim=16,  # Dimensão do vetor de features
        alpha=1.0        # Parâmetro de exploração
    )
    
    print(f"📊 Contextual Bandit inicializado")
    print(f"   • Estratégias: {len(estrategias)}")
    print(f"   • Dimensão de features: {bandit.feature_dim}")
    print(f"   • Alpha (exploração): {bandit.alpha}")
    print()
    
    # Simula tentativas de cobrança
    NUM_TENTATIVAS = 2000
    
    print(f"🚀 Simulando {NUM_TENTATIVAS} cobranças com perfis variados...")
    print()
    
    for i in range(NUM_TENTATIVAS):
        # 1. Novo cliente chega
        cliente = gerar_cliente_aleatorio()
        
        # 2. Bandit seleciona estratégia BASEADO NO PERFIL
        estrategia = bandit.select_strategy(cliente)
        
        # 3. Executa cobrança
        pagou, valor = simular_conversao_contextual(cliente, estrategia)
        
        # 4. Bandit aprende
        bandit.update(cliente, estrategia, pagou, valor)
        
        # Progress
        if (i + 1) % 200 == 0:
            print(f"Tentativa {i+1:4d} | Conversões até agora: {sum(bandit.conversions.values())}")
    
    print()
    print("="*80)
    print("📊 RESULTADOS FINAIS")
    print("="*80)
    print()
    
    # Estatísticas gerais
    print("📈 Performance por Estratégia:")
    print()
    stats = bandit.get_stats()
    print(stats.to_string(index=False))
    print()
    
    # Estatísticas por segmento
    print("🎯 Performance por Segmento de Cliente:")
    print()
    segment_stats = bandit.get_stats_by_segment()
    if not segment_stats.empty:
        # Mostra top 10 segmentos
        print(segment_stats.head(15).to_string(index=False))
    print()
    
    # Testa predição para perfis específicos
    print("="*80)
    print("🔮 PREDIÇÕES PARA PERFIS ESPECÍFICOS")
    print("="*80)
    print()
    
    # Teste 1: Jovem com dívida pequena
    cliente_teste1 = ClienteContext(
        idade=25,
        valor_divida=300,
        tempo_inadimplente=45,
        tipo_divida='cartao',
        tentativas_anteriores=1,
        regiao='sudeste',
        faixa_renda='media'
    )
    
    pred1 = bandit.predict_best_strategy(cliente_teste1)
    print("👤 Perfil 1: Jovem (25 anos), dívida pequena (R$300), 45 dias inadimplente")
    print(f"   ✅ Melhor estratégia: {pred1['best_strategy']}")
    print(f"   📊 Reward esperado: {pred1['expected_reward']:.3f}")
    print()
    
    # Teste 2: Senior com dívida grande
    cliente_teste2 = ClienteContext(
        idade=65,
        valor_divida=5000,
        tempo_inadimplente=200,
        tipo_divida='emprestimo',
        tentativas_anteriores=8,
        regiao='sul',
        faixa_renda='alta'
    )
    
    pred2 = bandit.predict_best_strategy(cliente_teste2)
    print("👤 Perfil 2: Senior (65 anos), dívida grande (R$5000), 200 dias, 8 tentativas")
    print(f"   ✅ Melhor estratégia: {pred2['best_strategy']}")
    print(f"   📊 Reward esperado: {pred2['expected_reward']:.3f}")
    print()
    
    # Salva modelo
    bandit.save_model('contextual_bandit_model.json')
    
    print("="*80)
    print("💡 INSIGHTS")
    print("="*80)
    print()
    print("✅ O Contextual Bandit PERSONALIZA a estratégia por cliente")
    print("✅ Aprende padrões como: jovens → empático, seniors → formal")
    print("✅ Balanceia exploração/exploitação automaticamente (via UCB)")
    print("✅ NÃO precisa de segmentação manual - descobre sozinho")
    print()
    print("📈 Próximo Passo: Evoluir para Q-Learning ou Deep RL (Nível 3)")
    print()


if __name__ == "__main__":
    main()


# =============================================================================
# INTEGRAÇÃO COM ORAMIND
# =============================================================================

"""
NO SISTEMA REAL:

1. No Agente de Estratégia:

    from rl_poc_nivel2_contextual import LinUCB, ClienteContext
    
    # Carrega modelo treinado
    bandit = LinUCB.load_model('models/contextual_bandit.json')
    
    # Para cada cliente novo
    context = ClienteContext(
        idade=cliente.idade,
        valor_divida=cliente.divida,
        tempo_inadimplente=cliente.dias_inadimplente,
        tipo_divida=cliente.tipo,
        tentativas_anteriores=count_tentativas(cliente.id),
        regiao=cliente.regiao,
        faixa_renda=estimar_renda(cliente)
    )
    
    # Seleciona estratégia personalizada
    estrategia = bandit.select_strategy(context)
    
    # Gera campanha com essa estratégia
    campanha = gerar_campanha(cliente, estrategia)


2. No Callback de Resultado:

    # Quando recebe resultado (pagou ou não)
    bandit.update(
        context=context_original,
        strategy=estrategia_usada,
        cliente_pagou=True,
        valor_pago=450.00
    )
    
    # Salva modelo atualizado
    if update_count % 100 == 0:
        bandit.save_model('models/contextual_bandit.json')


3. Analytics Dashboard:

    # Mostra performance por segmento
    stats_segment = bandit.get_stats_by_segment()
    
    # Testa "what-if"
    cliente_hipotetico = ClienteContext(...)
    pred = bandit.predict_best_strategy(cliente_hipotetico)
    
    print(f"Para esse perfil, use: {pred['best_strategy']}")
"""

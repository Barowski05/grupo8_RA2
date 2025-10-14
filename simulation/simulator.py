"""
Módulo de Simulação e Análise de Desempenho de Algoritmos de Cache.

Este módulo fornece uma função centralizada (`run_simulation_for_algorithm`)
capaz de testar qualquer algoritmo de cache que siga a interface do projeto.
Ele gera diferentes padrões de acesso, mede as principais métricas de desempenho
(hits, misses, tempo) e, opcionalmente, plota os resultados para facilitar a análise.
"""
import random
import math
from typing import Dict, Optional, Iterator

# A biblioteca matplotlib é opcional. Se não estiver instalada, a simulação
# rodará normalmente e imprimirá os resultados, mas não gerará os gráficos.
try:
    import matplotlib.pyplot as plt
    _HAS_MPL = True
except ImportError:
    _HAS_MPL = False

def run_simulation_for_algorithm(algorithm,
                                 n_users: int = 3,
                                 n_requests_per_user: int = 200,
                                 seed: Optional[int] = None,
                                 show_plot: bool = True) -> Dict[str, dict]:
    """
    Roda uma simulação completa para um algoritmo de cache e retorna um sumário dos resultados.

    Args:
        algorithm: Uma instância de uma classe de cache (ex: FIFOCache, LFUCache).
        n_users (int): O número de usuários simulados.
        n_requests_per_user (int): O número de solicitações de texto por usuário.
        seed (Optional[int]): Uma semente para o gerador de números aleatórios, garantindo
                              reprodutibilidade. Se None, a simulação será diferente a cada execução.
        show_plot (bool): Se True, exibe gráficos comparativos no final da simulação.

    Returns:
        Dict[str, dict]: Um dicionário com as métricas de desempenho para cada padrão de acesso.
    """
    # Se nenhuma semente for fornecida, gera uma aleatória para garantir que cada
    # execução seja única. Se uma semente for passada, a simulação será determinística.
    if seed is None:
        seed = random.SystemRandom().randint(0, 2**32 - 1)
    random.seed(seed)

    # Define os padrões de acesso que serão testados na simulação.
    patterns = [
        ("Uniforme", gen_uniform),
        ("Poisson (λ=30)", gen_poisson),
        ("Ponderado (30-40)", gen_weighted_30_40)
    ]

    summary = {}
    print(f"\n--- Iniciando Simulação para '{algorithm.__class__.__name__}' (Seed: {seed}) ---")

    for name, gen_func in patterns:
        # Tenta resetar o estado do algoritmo de forma robusta.
        # Isso garante que cada padrão de teste comece com o cache limpo,
        # tornando a comparação entre os padrões justa.
        if hasattr(algorithm, 'reset_stats'):
            algorithm.reset_stats(keep_cache=False)
        else:
            # Se o método 'reset_stats' não existir, tenta limpar manualmente as estruturas
            # de dados mais comuns, como dicionários, filas e contadores.
            for attr in ('cache_data', 'queue', 'freq', 'time_stamp', 'per_text_miss'):
                if hasattr(algorithm, attr):
                    getattr(algorithm, attr).clear()
            # Zera as métricas básicas.
            algorithm.hits = 0
            algorithm.misses = 0
            if hasattr(algorithm, 'total_time'):
                algorithm.total_time = 0.0

        # Roda a simulação principal: N usuários fazem M requisições cada um.
        for _ in range(n_users):
            for text_id in gen_func(n_requests_per_user):
                algorithm.get_text(text_id)

        # Coleta as estatísticas do algoritmo após a simulação do padrão.
        # Usa getattr com valor padrão para evitar erros caso um algoritmo
        # não implemente alguma métrica opcional.
        hits = getattr(algorithm, 'hits', 0)
        misses = getattr(algorithm, 'misses', 0)
        total_time = getattr(algorithm, 'total_time', 0.0)
        per_text_miss = getattr(algorithm, 'per_text_miss', None)

        # Armazena os resultados no sumário.
        summary[name] = {
            'hits': hits,
            'misses': misses,
            'total_requests': hits + misses,
            'total_time': total_time,
            'top_miss_texts': per_text_miss.most_common(5) if per_text_miss else "N/A"
        }

        print(f"  > Padrão '{name}': {hits} hits, {misses} misses. Tempo total: {total_time:.4f}s")

    summary['_seed_used'] = seed

    # Plota o sumário se a opção estiver ativa e a biblioteca disponível.
    if show_plot:
        if _HAS_MPL:
            _plot_summary(algorithm.__class__.__name__, summary)
        else:
            print("\n[AVISO] Matplotlib não encontrado. Para visualizar os gráficos, instale com: pip install matplotlib")

    return summary

# --- Geradores de Padrões de Acesso ---

def gen_uniform(n: int) -> Iterator[int]:
    #Gera 'n' solicitações de texto com distribuição uniforme (0-99).
    for _ in range(n):
        yield random.randint(0, 99)

def gen_poisson(n: int, lam: float = 30.0) -> Iterator[int]:
    # Gera 'n' solicitações de texto com distribuição de Poisson. Isso concentra os acessos em torno de um valor médio (lambda).
    for _ in range(n):
        # Algoritmo de Knuth para gerar números de Poisson.
        L = math.exp(-lam)
        k = 0
        p = 1.0
        while p > L:
            k += 1
            p *= random.random()
        yield (k - 1) % 100

def gen_weighted_30_40(n: int) -> Iterator[int]:
    #Gera 'n' solicitações onde os textos 30-40 têm 43% de chance de serem escolhidos. Simula um cenário com um ponto de dados populares.

    favored = list(range(30, 41))
    others = [i for i in range(100) if i not in favored]
    for _ in range(n):
        if random.random() < 0.43:
            yield random.choice(favored)
        else:
            yield random.choice(others)

# --- Função Auxiliar de Plotagem ---

def _plot_summary(name: str, summary: Dict[str, dict]):
    #Função interna para gerar gráficos com os resultados da simulação.
    if not _HAS_MPL:
        return

    patterns = [k for k, v in summary.items() if isinstance(v, dict)]
    hits = [summary[p]['hits'] for p in patterns]
    misses = [summary[p]['misses'] for p in patterns]
    times = [summary[p].get('total_time', 0.0) for p in patterns]

    x_pos = range(len(patterns))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(f'Análise de Desempenho para: {name} (Seed: {summary["_seed_used"]})', fontsize=16)

    # Gráfico de Hits e Misses
    ax1.bar(x_pos, hits, label='Hits', color='tab:green')
    ax1.bar(x_pos, misses, bottom=hits, label='Misses', color='tab:red')
    ax1.set_ylabel('Número de Requisições')
    ax1.set_title('Hits vs. Misses por Padrão de Acesso')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(patterns, rotation=15)
    ax1.legend()

    # Gráfico de Tempo Total
    ax2.bar(x_pos, times, color='tab:blue')
    ax2.set_ylabel('Tempo (segundos)')
    ax2.set_title('Tempo Total de Leitura do Disco')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(patterns, rotation=15)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Ajusta para o título principal
    plt.show()
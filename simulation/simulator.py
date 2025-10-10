"""
Módulo de simulação
"""
import random
import math
from typing import Dict, Optional

# matplotlib é opcional para plot; se não instalado, a função ainda retorna os dados
try:
    import matplotlib.pyplot as plt
    _HAS_MPL = True
except Exception:
    _HAS_MPL = False


def run_simulation_for_algorithm(algorithm,
                                 n_users: int = 3,
                                 n_requests_per_user: int = 200,
                                 seed: int = 42,
                                 show_plot: bool = True) -> Dict[str, dict]:
    """Roda a simulação para QUALQUER algoritmo que implemente get_text(text_id).

    O algoritmo deve expor ao menos: hits, misses, cache_data. Opcional: total_time, per_text_miss.
    Retorna um dicionário resumo com estatísticas por padrão.
    """
    random.seed(seed)

    patterns = [
        ("uniforme", gen_uniform),
        ("poisson", gen_poisson),
        ("ponderado_30_40", gen_weighted_30_40)
    ]

    summary = {}

    for name, gen_func in patterns:
        # resetar estado do algoritmo para condições equivalentes
        if hasattr(algorithm, 'reset_stats'):
            algorithm.reset_stats(keep_cache=False)
        else:
            algorithm.hits = 0
            algorithm.misses = 0
            algorithm.cache_data.clear()
            if hasattr(algorithm, 'total_time'):
                algorithm.total_time = 0.0

        # simulação: n_users * n_requests_per_user
        for _ in range(n_users):
            for tid in gen_func(n_requests_per_user):
                algorithm.get_text(tid)

        hits = getattr(algorithm, 'hits', 0)
        misses = getattr(algorithm, 'misses', 0)
        total_time = getattr(algorithm, 'total_time', None)
        per_text_miss = getattr(algorithm, 'per_text_miss', None)

        summary[name] = {
            'hits': hits,
            'misses': misses,
            'total_requests': hits + misses,
            'total_time': total_time,
            'top_miss_texts': per_text_miss.most_common(10) if per_text_miss is not None else None
        }

        print(f"[{algorithm.__class__.__name__}] Padrão: {name} -> hits={hits}, misses={misses}, time={total_time}")

    if show_plot and _HAS_MPL:
        _plot_summary(algorithm.__class__.__name__, summary)
    elif show_plot and not _HAS_MPL:
        print("matplotlib não instalado: pulando plots")

    return summary


# ---------- geradores de padrões ----------
from typing import Iterator

def gen_uniform(n: int) -> Iterator[int]:
    for _ in range(n):
        yield random.randrange(0, 100)


def gen_poisson(n: int, lam: Optional[float] = 30.0) -> Iterator[int]:
    # algoritmo de Knuth
    for _ in range(n):
        L = math.exp(-lam)
        k = 0
        p = 1.0
        while p > L:
            k += 1
            p *= random.random()
        yield (k - 1) % 100


def gen_weighted_30_40(n: int) -> Iterator[int]:
    favored = list(range(30, 41))
    others = [i for i in range(100) if i not in favored]
    for _ in range(n):
        if random.random() < 0.43:
            yield random.choice(favored)
        else:
            yield random.choice(others)


# --------- plot ----------
def _plot_summary(name: str, summary: Dict[str, dict]):
    if not _HAS_MPL:
        return
    patterns = list(summary.keys())
    hits = [summary[p]['hits'] for p in patterns]
    misses = [summary[p]['misses'] for p in patterns]
    times = [summary[p]['total_time'] or 0.0 for p in patterns]

    x = range(len(patterns))

    import matplotlib.pyplot as plt
    plt.figure(figsize=(12,4))
    plt.subplot(1,2,1)
    plt.bar(x, hits, label='hits')
    plt.bar(x, misses, bottom=hits, label='misses')
    plt.xticks(x, patterns)
    plt.title(f"{name} - hits / misses")
    plt.legend()

    plt.subplot(1,2,2)
    plt.bar(patterns, times)
    plt.title(f"{name} - tempo total (s)")
    plt.tight_layout()
    plt.show()
#Módulo de simulação
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
                                 seed: Optional[int] = None,
                                 show_plot: bool = True) -> Dict[str, dict]:
    """Roda a simulação para QUALQUER algoritmo que implemente get_text(text_id).

    Se `seed` for None, uma seed aleatória forte será gerada para que execuções
    sucessivas produzam resultados diferentes. Se `seed` for um int, a simulação
    será determinística e reproduzível.
    """
    # gerar seed forte se não fornecida, e inicializar gerador pseudo-aleatório
    if seed is None:
        seed = random.SystemRandom().randint(0, 2**32 - 1)
    random.seed(seed)
   # Define os padrões de acesso que serão testados

    patterns = [
        ("uniforme", gen_uniform),
        ("poisson", gen_poisson),
        ("ponderado_30_40", gen_weighted_30_40)
    ]

    summary = {}

    for name, gen_func in patterns:
        # Bloco robusto para resetar o estado do algoritmo antes de cada teste de padrão.
        # Isso garante que as comparações sejam justas, começando sempre do zero.
        if hasattr(algorithm, 'reset_stats'):
            try:
                algorithm.reset_stats(keep_cache=False)
            except TypeError:
                try:
                    algorithm.reset_stats()
                except Exception:
                    pass
        else:
            # Se um método `reset_stats` não for encontrado, tenta limpar manualmente
            # atributos comuns de cache para garantir um estado limpo.
            for attr in ('cache_data', 'queue', 'usage_order', 'freq', 'time_stamp', 'per_text_miss', 'per_text_time'):
                if hasattr(algorithm, attr):
                    try:
                        val = getattr(algorithm, attr)
                        # tenta limpar containers suportados (dict, deque, Counter, list, set, OrderedDict)
                        try:
                            val.clear()
                            continue
                        except Exception:
                            pass
                        # Se não for possível, tenta reinstanciar o atributo.
                        try:
                            setattr(algorithm, attr, type(val)())
                        except Exception:
                            pass
                    except Exception:
                        pass
            # Reseta as métricas básicas de hits, misses e tempo.
            if hasattr(algorithm, 'hits'):
                try:
                    algorithm.hits = 0
                except Exception:
                    pass
            if hasattr(algorithm, 'misses'):
                try:
                    algorithm.misses = 0
                except Exception:
                    pass
            if hasattr(algorithm, 'total_time'):
                try:
                    algorithm.total_time = 0.0
                except Exception:
                    pass

        # Executa a simulação: N usuários fazem M requisições cada.
        for _ in range(n_users):
            for tid in gen_func(n_requests_per_user):
                algorithm.get_text(tid)

        # Coleta as estatísticas após a simulação.
        hits = getattr(algorithm, 'hits', 0)
        misses = getattr(algorithm, 'misses', 0)
        total_time = getattr(algorithm, 'total_time', None)
        per_text_miss = getattr(algorithm, 'per_text_miss', None)

        # Armazena os resultados no sumário.
        summary[name] = {
            'hits': hits,
            'misses': misses,
            'total_requests': hits + misses,
            'total_time': total_time,
            'top_miss_texts': per_text_miss.most_common(10) if per_text_miss is not None else None
        }

        print(f"[{algorithm.__class__.__name__}] Padrão: {name} -> hits={hits}, misses={misses}, time={total_time}")

    # Armazena a semente usada para fins de registro e reprodutibilidade.
    summary['_seed'] = seed

    if show_plot and _HAS_MPL:
        _plot_summary(algorithm.__class__.__name__, summary)
    elif show_plot and not _HAS_MPL:
        print("matplotlib não instalado: pulando plots")

    return summary


# ---------- geradores de padrões ----------
from typing import Iterator

def gen_uniform(n: int) -> Iterator[int]:
    #Gera 'n' solicitações de texto com distribuição uniforme (0-99).
    for _ in range(n):
        yield random.randrange(0, 100)


def gen_poisson(n: int, lam: Optional[float] = 30.0) -> Iterator[int]:
    # algoritmo de Knuth que gera 'n' solicitações de texto com distribuição de Poisson, concentrando acessos perto de lambda
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


#plot
def _plot_summary(name: str, summary: Dict[str, dict]):
     #Função interna para gerar gráficos com os resultados da simulação.
    if not _HAS_MPL:
        return
    patterns = [k for k, v in summary.items() if isinstance(v, dict)]
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
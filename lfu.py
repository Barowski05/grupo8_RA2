"""
- Contém a classe `LFUCache` que herda de CacheInterface (tenta importar de core.cache_interface e cache_interface)
- Implementa `get_text(text_id)` (LFU com desempate por timestamp)
- Implementa `run_simulation(...)` delegando para a função genérica `run_simulation_for_algorithm`
- Exporta `run_simulation_for_algorithm` e os geradores de padrões para que o Aluno A possa usar

Como usar no `ra2_main.py` do Aluno A ou em testes:

from algorithms.lfu import LFUCache, run_simulation_for_algorithm

lfu = LFUCache(capacity=10, disk_reader_func=disk_reader_real)
# rodar só o LFU
lfu.run_simulation()
# ou rodar usando função genérica (aceita qualquer instância que implemente get_text, cache_data, hits, misses)
run_simulation_for_algorithm(lfu)

"""
from collections import Counter
import time
import random
import math
from typing import Callable, Dict, Optional

# tentar duas localizações possíveis para a interface (depende de como o repo está organizado)
try:
    from core.cache_interface import CacheInterface
except Exception:
    try:
        from cache_interface import CacheInterface
    except Exception:
        raise ImportError("Não foi possível importar CacheInterface. Coloque cache_interface.py em core/ ou no mesmo diretório.")

# --------- Classe LFUCache (Aluno D) ---------
class LFUCache(CacheInterface):
    """LFU (Least Frequently Used) cache implementing the project's CacheInterface.

    - Frequência de acessos armazenada em `self.freq` (Counter)
    - Desempate por `self.time_stamp` (menor = mais antigo)
    - Estatísticas extras: per_text_miss, per_text_time, total_time

    Observações:
    - A leitura do "disco" deve ser feita via `self.disk_reader(text_id)` (fornecida na construção)
    - `run_simulation` é implementado aqui para cumprir a interface, mas delega para
      a função `run_simulation_for_algorithm`, preservando uma única fonte de verdade.
    """

    def __init__(self, capacity: int, disk_reader_func: Callable[[int], str]):
        super().__init__(capacity, disk_reader_func)
        self.freq: Counter = Counter()           # text_id -> frequency
        self.time_stamp: Dict[int, int] = {}     # text_id -> tick (para desempate)
        self._clk = 0

        # estatísticas detalhadas
        self.per_text_miss: Counter = Counter()
        self.per_text_time: Dict[int, float] = {}
        self.total_time: float = 0.0

    def _tick(self) -> int:
        self._clk += 1
        return self._clk

    def get_text(self, text_id: int) -> str:
        """Retorna o conteúdo do texto, atualiza hits/misses e faz evicção LFU quando necessário.

        Mede o tempo real gasto pela chamada self.disk_reader(text_id) (apenas em MISS).
        """
        tick = self._tick()

        # HIT
        if text_id in self.cache_data:
            self.hits += 1
            self.freq[text_id] += 1
            # atualiza timestamp para desempate por recência
            self.time_stamp[text_id] = tick
            return self.cache_data[text_id]

        # MISS
        self.misses += 1
        self.per_text_miss[text_id] += 1

        # medir tempo de leitura do disco
        t0 = time.perf_counter()
        content = self.disk_reader(text_id)
        t1 = time.perf_counter()
        elapsed = t1 - t0

        # estatísticas temporais
        self.total_time += elapsed
        self.per_text_time[text_id] = self.per_text_time.get(text_id, 0.0) + elapsed

        # evicção LFU se necessário
        if len(self.cache_data) >= self.capacity:
            if self.freq:
                min_freq = min(self.freq.values())
                candidates = [tid for tid, f in self.freq.items() if f == min_freq]
                victim = min(candidates, key=lambda t: self.time_stamp.get(t, 0))
            else:
                # fallback
                victim = next(iter(self.cache_data))

            # remover estruturas do victim
            try:
                del self.cache_data[victim]
            except KeyError:
                pass
            try:
                del self.freq[victim]
            except KeyError:
                pass
            try:
                del self.time_stamp[victim]
            except KeyError:
                pass

        # inserir novo
        self.cache_data[text_id] = content
        self.freq[text_id] = 1
        self.time_stamp[text_id] = tick

        return content

    def reset_stats(self, keep_cache: bool = False):
        """Zera estatísticas. Se keep_cache=False, também limpa o cache e estruturas LFU."""
        self.hits = 0
        self.misses = 0
        self.per_text_miss.clear()
        self.per_text_time.clear()
        self.total_time = 0.0
        self._clk = 0
        if not keep_cache:
            self.cache_data.clear()
            self.freq.clear()
            self.time_stamp.clear()

    def run_simulation(self,
                       n_users: int = 3,
                       n_requests_per_user: int = 200,
                       seed: int = 42,
                       show_plot: bool = True):
        """Implementa run_simulation para cumprir a interface.

        Este método apenas delega para a função genérica run_simulation_for_algorithm,
        garantindo compatibilidade com a interface abstrata exigida.
        """
        return run_simulation_for_algorithm(self,
                                            n_users=n_users,
                                            n_requests_per_user=n_requests_per_user,
                                            seed=seed,
                                            show_plot=show_plot)


# --------- Função de simulação genérica (reutilizável por FIFO/LRU/LFU) ---------
def run_simulation_for_algorithm(algorithm,
                                 n_users: int = 3,
                                 n_requests_per_user: int = 200,
                                 seed: int = 42,
                                 show_plot: bool = True):
    """Roda a simulação para QUALQUER algoritmo que siga a CacheInterface.

    O algoritmo precisa expor ao menos:
      - get_text(text_id)
      - cache_data (dict)
      - hits, misses
      - total_time (float) ou a função irá criar/atualizar

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
        # resetar estado do algoritmo pra cada padrão (condições iguais)
        # aqui assumimos que o algoritmo tem reset_stats; se não tiver, limpamos manualmente
        if hasattr(algorithm, 'reset_stats'):
            algorithm.reset_stats(keep_cache=False)
        else:
            # fallback: zera contadores e limpa cache
            algorithm.hits = 0
            algorithm.misses = 0
            algorithm.cache_data.clear()
            if hasattr(algorithm, 'total_time'):
                algorithm.total_time = 0.0

        # realizar acessos: cada usuário faz n_requests_per_user
        for user_idx in range(n_users):
            for tid in gen_func(n_requests_per_user):
                algorithm.get_text(tid)

        # coletar estatísticas
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

    if show_plot:
        try:
            _plot_summary(algorithm.__class__.__name__, summary)
        except Exception as e:
            print("Falha ao gerar plots:", e)

    return summary


# --------- Geradores de padrões ---------
def gen_uniform(n):
    for _ in range(n):
        yield random.randrange(0, 100)


def gen_poisson(n, lam: Optional[float] = 30.0):
    # algoritmo de Knuth
    for _ in range(n):
        L = math.exp(-lam)
        k = 0
        p = 1.0
        while p > L:
            k += 1
            p *= random.random()
        yield (k - 1) % 100


def gen_weighted_30_40(n):
    favored = list(range(30, 41))
    others = [i for i in range(100) if i not in favored]
    for _ in range(n):
        if random.random() < 0.43:
            yield random.choice(favored)
        else:
            yield random.choice(others)


# --------- Plot helper ---------
def _plot_summary(name: str, summary: Dict[str, dict]):
    import matplotlib.pyplot as plt

    patterns = list(summary.keys())
    hits = [summary[p]['hits'] for p in patterns]
    misses = [summary[p]['misses'] for p in patterns]
    times = [summary[p]['total_time'] or 0.0 for p in patterns]

    x = range(len(patterns))

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


# --------- teste rápido quando executado como script ---------
if __name__ == '__main__':
    # teste com dummy_disk_reader (simula latência de disco)
    def dummy_disk_reader(tid: int) -> str:
        time.sleep(0.01)
        return f"Dummy text {tid}"

    lfu = LFUCache(capacity=10, disk_reader_func=dummy_disk_reader)
    # roda simulação e exibe resumo
    run_simulation_for_algorithm(lfu, show_plot=False)

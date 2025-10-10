from collections import Counter
import time
from typing import Callable, Dict

# tenta importar CacheInterface em duas localizações comuns
try:
    from core.cache_interface import CacheInterface
except Exception:
    try:
        from cache_interface import CacheInterface
    except Exception as e:
        raise ImportError("Não foi possível importar CacheInterface. Coloque cache_interface.py em core/ ou no root.")

# tenta importar a função genérica de simulação (simulator.py em simulation/)
try:
    from simulation.simulator import run_simulation_for_algorithm
except Exception:
    # fallback: caso a pasta simulation não esteja no PYTHONPATH
    def run_simulation_for_algorithm(algorithm, *args, **kwargs):
        raise RuntimeError("Função run_simulation_for_algorithm não encontrada. Verifique se 'simulation/simulator.py' existe e o package 'simulation' tem __init__.py")


class LFUCache(CacheInterface):
    """LFU cache implementation.

    - freq: Counter dos acessos
    - time_stamp: desempate por tick (menor = mais antigo)
    - per_text_miss, per_text_time, total_time para relatórios
    """

    def __init__(self, capacity: int, disk_reader_func: Callable[[int], str]):
        super().__init__(capacity, disk_reader_func)
        self.freq: Counter = Counter()
        self.time_stamp: Dict[int, int] = {}
        self._clk = 0

        # estatísticas detalhadas
        self.per_text_miss: Counter = Counter()
        self.per_text_time: Dict[int, float] = {}
        self.total_time: float = 0.0

    def _tick(self) -> int:
        self._clk += 1
        return self._clk

    def get_text(self, text_id: int) -> str:
        """Retorna o conteúdo do texto. Atualiza hits/misses e faz evicção LFU quando necessário.

        Mede o tempo real gasto pela chamada self.disk_reader(text_id) (apenas em MISS).
        """
        tick = self._tick()

        # HIT
        if text_id in self.cache_data:
            self.hits += 1
            self.freq[text_id] += 1
            # atualiza desempate por recência
            self.time_stamp[text_id] = tick
            return self.cache_data[text_id]

        # MISS
        self.misses += 1
        self.per_text_miss[text_id] += 1

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
                victim = next(iter(self.cache_data))

            # remover victim de todas as estruturas (proteções)
            for d in (self.cache_data, self.freq, self.time_stamp):
                try:
                    del d[victim]
                except Exception:
                    pass

        # inserir novo
        self.cache_data[text_id] = content
        self.freq[text_id] = 1
        self.time_stamp[text_id] = tick

        return content

    def reset_stats(self, keep_cache: bool = False):
        """Zera estatísticas; se keep_cache=False, limpa também o cache e estruturas LFU."""
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

    def run_simulation(self, n_users: int = 3, n_requests_per_user: int = 200, seed: int = 42, show_plot: bool = True):
        """Implementa run_simulation delegando para a função genérica do package simulation."""
        return run_simulation_for_algorithm(self, n_users=n_users, n_requests_per_user=n_requests_per_user, seed=seed, show_plot=show_plot)


# teste rápido local
if __name__ == '__main__':
    def dummy_reader(tid: int) -> str:
        time.sleep(0.005)
        return f"Dummy text {tid}"

    cache = LFUCache(capacity=5, disk_reader_func=dummy_reader)
    try:
        cache.run_simulation(show_plot=False)
    except Exception as e:
        print("Teste local: simulador não disponível -> ok para checar LFU get_text():", e)
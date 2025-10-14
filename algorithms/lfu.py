from collections import Counter
import time
from typing import Callable, Dict

# Bloco de importação robusto para garantir que a interface seja encontrada,
# independentemente de como o projeto é executado.
try:
    from core.cache_interface import CacheInterface
except ImportError:
    try:
        from cache_interface import CacheInterface
    except ImportError as e:
        raise ImportError(
            " Não foi possível importar CacheInterface. "
            "Coloque cache_interface.py em 'core/' ou no diretório raiz."
        )


class LFUCache(CacheInterface):
     """
    Implementação do algoritmo de cache LFU (Least Frequently Used).

    - Estratégia: Remove o item menos acessado quando o cache está cheio.
    - Desempate: Se múltiplos itens têm a mesma frequência mínima, remove o que foi
      acessado há mais tempo (critério LRU - Least Recently Used).
    - Métricas: Mantém contadores detalhados para análise de desempenho.
    """
     def __init__(self, capacity: int, disk_reader_func: Callable[[int], str]):
        #Inicializa o cache e as estruturas de dados para o LFU.
        super().__init__(capacity, disk_reader_func)

        # Estruturas de dados principais do LFU
        self.freq: Counter = Counter()              # frequência de acessos
        self.time_stamp: Dict[int, int] = {}        # desempate pelo tempo de uso
        self._clk: int = 0                          # relógio lógico para desempate

        # Estruturas para coleta de estatísticas detalhadas
        self.per_text_miss: Counter = Counter()
        self.per_text_time: Dict[int, float] = {}
        self.total_time: float = 0.0

     def _tick(self) -> int:
        #Incrementa e retorna o relógio lógico.
        self._clk += 1
        return self._clk

     def get_text(self, text_id: int) -> str:

        #Obtém um texto, seja do cache (hit) ou do disco (miss) e aplica a lógica de LFU para atualização e remoção.
        tick = self._tick()

        # Caso 1: HIT, O texto já está no cache
        if text_id in self.cache_data:
            self.hits += 1
            self.freq[text_id] += 1
            self.time_stamp[text_id] = tick
            return self.cache_data[text_id]

        # Caso 2: MISS, O texto não está no cache e precisa ser lido do disco.
        self.misses += 1
        self.per_text_miss[text_id] += 1

        # Mede o tempo de leitura do disco, uma métrica chave do projeto.
        t0 = time.perf_counter()
        content = self.disk_reader(text_id)
        elapsed = time.perf_counter() - t0

        # Atualiza as estatísticas de tempo.
        self.total_time += elapsed
        self.per_text_time[text_id] = self.per_text_time.get(text_id, 0.0) + elapsed

        # Se o cache estiver cheio, remove um item antes de adicionar o novo.
        if len(self.cache_data) >= self.capacity:
            # 1. Encontra a frequência mínima entre todos os itens no cache.
            if self.freq:
                min_freq = min(self.freq.values())
                # 2. Identifica todos os itens que possuem essa frequência mínima (pode haver mais de um).
                candidates = [tid for tid, f in self.freq.items() if f == min_freq]
                # 3. Critério de desempate: entre os candidatos, escolhe o menos recentemente usado
                victim = min(candidates, key=lambda t: self.time_stamp.get(t, 0))
            else:
                victim = next(iter(self.cache_data))

            # remove da cache e metadados
            for d in (self.cache_data, self.freq, self.time_stamp):
                d.pop(victim, None)
            print(f"[LFU] Evictando item {victim}")

        # insere novo
        self.cache_data[text_id] = content
        self.freq[text_id] = 1
        self.time_stamp[text_id] = tick

        return content

     def reset_stats(self, keep_cache: bool = False):
        #Reseta estatísticas. Se keep_cache=False, limpa também o cache e estruturas auxiliares.
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

     def run_simulation(self):
        #Método obrigatório da interface. A lógica de simulação foi centralizada noutro módulo.
        pass


#Teste básico local
if __name__ == "__main__":
    def dummy_reader(tid: int) -> str:
        #Simula uma leitura de disco com uma pequena latência
        time.sleep(0.001)
        return f"Texto {tid}"

    # Cria uma instância do cache com capacidade 3.
    cache = LFUCache(capacity=3, disk_reader_func=dummy_reader)

    for i in [1, 2, 3, 1, 2, 4, 1, 5]:
        content = cache.get_text(i)
        print(f"Acessando {i} -> {content} | Cache atual: {list(cache.cache_data.keys())}")
        
    #Estatísticas finais
    print(f"\n Hits: {cache.hits}")
    print(f"Misses: {cache.misses}")
    print(f"Tempo total de leitura: {cache.total_time:.6f}s")
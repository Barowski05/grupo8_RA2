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
        """Inicializa o cache e as estruturas de dados para o LFU."""
        super().__init__(capacity, disk_reader_func)
        
        # Estruturas de dados principais do LFU
        self.freq: Counter = Counter()              # Mapeia text_id -> frequência de acesso
        self.time_stamp: Dict[int, int] = {}        # Mapeia text_id -> último "tick" de acesso (para desempate)
        self._clk: int = 0                          # Relógio lógico interno para registrar o tempo de acesso

        # Estruturas para coleta de estatísticas detalhadas
        self.per_text_miss: Counter = Counter()     # Contagem de misses por cada text_id
        self.per_text_time: Dict[int, float] = {}   # Soma do tempo de leitura do disco por cada text_id
        self.total_time: float = 0.0                # Tempo total gasto lendo do disco

    def _tick(self) -> int:
        #Incrementa e retorna o valor do relógio lógico.
        self._clk += 1
        return self._clk

    def get_text(self, text_id: int) -> str:
        #Obtém um texto, seja do cache (hit) ou do disco (miss) e aplica a lógica de LFU para atualização e remoção.
        
        current_tick = self._tick()

        # --- Caso 1: Cache HIT ---
        # O texto já está no cache.
        if text_id in self.cache_data:
            self.hits += 1
            # Atualiza a frequência e o timestamp do acesso.
            self.freq[text_id] += 1
            self.time_stamp[text_id] = current_tick
            return self.cache_data[text_id]

        # --- Caso 2: Cache MISS ---
        # O texto não está no cache e precisa ser lido do disco.
        self.misses += 1
        self.per_text_miss[text_id] += 1 # Registra o miss para este texto específico.

        # Mede o tempo de leitura do disco, uma métrica chave do projeto.
        t0 = time.perf_counter()
        content = self.disk_reader(text_id)
        elapsed = time.perf_counter() - t0

        # Atualiza as estatísticas de tempo.
        self.total_time += elapsed
        self.per_text_time[text_id] = self.per_text_time.get(text_id, 0.0) + elapsed

        # --- Lógica de Remoção (Eviction) ---
        # Se o cache estiver cheio, remove um item antes de adicionar o novo.
        if len(self.cache_data) >= self.capacity:
            # 1. Encontra a frequência mínima entre todos os itens no cache.
            min_freq = min(self.freq.values())
            
            # 2. Identifica todos os itens que possuem essa frequência mínima (pode haver mais de um).
            candidates = [tid for tid, f in self.freq.items() if f == min_freq]
            
            # 3. Critério de desempate: entre os candidatos, escolhe o menos recentemente usado
            #    (aquele com o menor timestamp).
            victim = min(candidates, key=lambda t: self.time_stamp.get(t, 0))

            # Remove o item "vítima" de todas as estruturas de dados.
            # O pop(key, None) é usado para evitar erros caso a chave não exista em alguma estrutura.
            for d in (self.cache_data, self.freq, self.time_stamp):
                d.pop(victim, None)
            print(f"[LFU] Cache cheio. Removendo item {victim} (freq={min_freq}).")

        # Adiciona o novo texto ao cache e inicializa sua frequência e timestamp.
        self.cache_data[text_id] = content
        self.freq[text_id] = 1
        self.time_stamp[text_id] = current_tick

        return content

    def reset_stats(self, keep_cache: bool = False):
        
        #Reseta as estatísticas de desempenho.
        
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
        #Método obrigatório da interface. A lógica de simulação deste projeto foi centralizada no módulo 'simulation' para ser reutilizada por todosos algoritmos.
        pass # A implementação real é feita por um módulo externo.


# Bloco de teste para validar a lógica do LFU de forma isolada.
if __name__ == "__main__":
    def dummy_reader(tid: int) -> str:
        """Simula uma leitura de disco com uma pequena latência."""
        time.sleep(0.001)
        return f"Texto {tid}"

    # Cria uma instância do cache com capacidade 3.
    cache = LFUCache(capacity=3, disk_reader_func=dummy_reader)

    # Sequência de acessos para testar a lógica de hit, miss e eviction.
    access_sequence = [1, 2, 3, 1, 2, 4, 1, 5]
    print(f"Testando a sequência de acesso: {access_sequence}\n")

    for i in access_sequence:
        content = cache.get_text(i)
        print(f"Acessando {i} -> '{content}' | Cache atual: {list(cache.cache_data.keys())}")

    # Exibe as estatísticas finais.
    print(f"\n--- Resultados Finais ---")
    print(f"Hits: {cache.hits}")
    print(f"Misses: {cache.misses}")
    print(f"Frequências finais: {dict(cache.freq)}")
    print(f"Tempo total de leitura: {cache.total_time:.6f}s")
from collections import deque
import time
try:
    # quando executado como parte de um package (python -m algorithms.FIFO)
    from .cache_interface import CacheBase
except Exception:
    # fallbacks para execução direta ou diferentes layouts de import
    try:
        from cache_interface import CacheBase
    except Exception:
        from algorithms.cache_interface import CacheBase


class FIFOCache(CacheBase):
    """
    Implementação do algoritmo de cache FIFO (First-In, First-Out).
    - Remove sempre o item mais antigo quando o cache atinge a capacidade máxima.
    - Conta hits e misses.
    """

    def __init__(self, capacity: int, disk_reader_func):
        # CacheBase.__init__ espera apenas 'capacity'
        super().__init__(capacity)
        # guarda o leitor de disco localmente para uso em get_text
        self.disk_reader = disk_reader_func
        # garante que os atributos usados por get_text existam,
        # sem sobrescrever possíveis inicializações da classe base
        if not hasattr(self, "cache_data"):
            self.cache_data = {}
        if not hasattr(self, "hits"):
            self.hits = 0
        if not hasattr(self, "misses"):
            self.misses = 0
        if not hasattr(self, "capacity"):
            self.capacity = capacity
        self.queue = deque()  # controla a ordem de chegada dos textos

    def get_text(self, text_id: int) -> str:
        """Lê o texto, usando o cache conforme a política FIFO."""
        start = time.time()

        # Se o texto já está no cache → HIT
        if text_id in self.cache_data:
            self.hits += 1
            content = self.cache_data[text_id]
            print(f"[HIT] Texto {text_id} encontrado no cache.")
        else:
            # MISS → busca no "disco lento"
            self.misses += 1
            print(f"[MISS] Texto {text_id} não está no cache. Lendo do disco...")
            content = self.disk_reader(text_id)

            # Se o cache estiver cheio, remove o mais antigo
            if len(self.cache_data) >= self.capacity:
                oldest_id = self.queue.popleft()
                self.cache_data.pop(oldest_id, None)
                print(f"[FIFO] Removendo texto {oldest_id} do cache (mais antigo).")

            # Adiciona o novo texto
            self.cache_data[text_id] = content
            self.queue.append(text_id)

        end = time.time()
        print(f"[INFO] Tempo de carregamento: {(end - start):.4f}s\n")
        return content
    
    # Implementa o método abstrato exigido pela CacheBase
    def get(self, text_id: int) -> str:
        return self.get_text(text_id)
    
if __name__ == "__main__":
    import os
    import time

    # Caminho da pasta texts (ajuste se estiver em outro local)
    TEXT_DIR = "texts"

    # Função que lê o texto real do disco (simulando disco lento)
    def slow_loader(text_id: int) -> str:
        file_path = os.path.join(TEXT_DIR, f"texto_{text_id}.txt")
        if not os.path.exists(file_path):
            return f"[ERRO] Texto {text_id} não encontrado!"
        time.sleep(0.5)  # simula lentidão do disco
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    # Cria uma instância do cache FIFO
    cache = FIFOCache(capacity=3, disk_reader_func=slow_loader)

    # Sequência de acessos para testar comportamento
    acessos = [1, 2, 3, 1, 4, 2, 1]
    for text_id in acessos:
        print(f"\n>>> Solicitando texto {text_id}")
        cache.get_text(text_id)

    # Mostra resultados finais
    print("\n--- RESULTADO FINAL ---")
    print(f"Hits: {cache.hits}")
    print(f"Misses: {cache.misses}")
    print(f"Conteúdo atual no cache: {list(cache.queue)}")

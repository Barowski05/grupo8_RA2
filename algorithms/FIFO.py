from collections import deque
from core.cache_interface import CacheInterface

class FIFOCache(CacheInterface):
    """
    Implementação do algoritmo de cache FIFO (First-In, First-Out).
    Versão corrigida e integrada ao projeto principal.
    """
    def __init__(self, capacity: int, disk_reader_func):
        """
        Construtor simplificado que utiliza a inicialização da classe pai.
        """
        # Chama o construtor da CacheInterface para inicializar todos os atributos comuns.
        super().__init__(capacity, disk_reader_func)
        
        # Inicializa o único atributo que é específico do algoritmo FIFO.
        self.queue = deque()

    def get_text(self, text_id: int) -> str:
        """Lê o texto, usando o cache conforme a política FIFO."""
        
        # Se o texto já está no cache → HIT
        if text_id in self.cache_data:
            self.hits += 1
            print(f"[HIT] Texto {text_id} encontrado no cache.")
            return self.cache_data[text_id]
        
        # Se não está no cache → MISS
        else:
            self.misses += 1
            print(f"[MISS] Texto {text_id} não está no cache. Lendo do disco...")
           

            # Se o cache estiver cheio, remove o mais antigo da fila e do dicionário
            if len(self.cache_data) >= self.capacity:
                oldest_id = self.queue.popleft()
                if oldest_id in self.cache_data:
                    del self.cache_data[oldest_id]
                print(f"[FIFO] Removendo texto {oldest_id} do cache (mais antigo).")

            content = self.disk_reader(text_id)

            # Adiciona o novo texto ao cache e à fila
            self.cache_data[text_id] = content
            self.queue.append(text_id)
            return content

    def run_simulation(self):
        """
        Implementação obrigatória do método de simulação.
        """
        print(f"\n[AVISO] O modo de simulação para o algoritmo {self.__class__.__name__} ainda não foi implementado.")
        print("Pressione Enter para retornar ao modo de leitura...")
        input()


# algorithms/mru_cache.py
from collections import OrderedDict
from core.cache_interface import CacheInterface
import time

class MRUCache(CacheInterface):
    """
    Implementação do algoritmo de cache MRU (Most Recently Used).
    Remove o item mais recentemente usado quando o cache está cheio.
    """
    def __init__(self, capacity: int, disk_reader_func):
        """
        Construtor seguindo o mesmo padrão do FIFO.
        """
        # Chama o construtor da CacheInterface para inicializar atributos comuns
        super().__init__(capacity, disk_reader_func)
        
        # OrderedDict para controlar a ordem de uso (do menos recente para o mais recente)
        self.usage_order = OrderedDict()
        self.total_time = 0.0

    def get_text(self, text_id: int) -> str:
        """Lê o texto, usando o cache conforme a política MRU."""
        
        # Se o texto já está no cache → HIT
        if text_id in self.cache_data:
            self.hits += 1
            print(f"[HIT] Texto {text_id} encontrado no cache.")
            
            # Atualiza a ordem de uso - move para o final (mais recente)
            self.usage_order.move_to_end(text_id)
            return self.cache_data[text_id]
        
        # Se não está no cache → MISS
        else:
            self.misses += 1
            print(f"[MISS] Texto {text_id} não está no cache. Lendo do disco...")
            
            # Se o cache estiver cheio, remove o MAIS RECENTEMENTE USADO
            if len(self.cache_data) >= self.capacity:
                # Remove o último item do OrderedDict (mais recente)
                most_recent_id, _ = self.usage_order.popitem(last=True)
                if most_recent_id in self.cache_data:
                    del self.cache_data[most_recent_id]
                print(f"[MRU] Removendo texto {most_recent_id} do cache (mais recentemente usado).")

            # Lê o conteúdo do disco
            start_time = time.perf_counter()
            content = self.disk_reader(text_id)
            self.total_time += time.perf_counter() - start_time

            # Adiciona o novo texto ao cache e à ordem de uso
            self.cache_data[text_id] = content
            self.usage_order[text_id] = True  # Valor não importa, só a chave
            return content

    def run_simulation(self):
        """
        Implementação obrigatória do método de simulação.
        Seguindo o mesmo padrão do FIFO.
        """
        print(f"\n[AVISO] O modo de simulação para o algoritmo {self.__class__.__name__} ainda não foi implementado.")
        print("Pressione Enter para retornar ao modo de leitura...")
        input()

if __name__ == '__main__':
    import time

    def dummy_disk_reader(text_id: int) -> str:
        """Simula leitura do disco e retorna conteúdo dummy."""
        time.sleep(0.05)
        return f"Conteúdo do texto {text_id}"

    # Teste do algoritmo MRU - APENAS UMA VEZ
    cache = MRUCache(capacity=3, disk_reader_func=dummy_disk_reader)
    
    # Padrão de acesso que demonstra a política MRU - APENAS ESTA LISTA
    accesses = [1, 2, 3, 1, 4, 2, 5, 1]

    print("=== TESTE DO ALGORITMO MRU ===")
    for tid in accesses:
        content = cache.get_text(tid)
        print(f"[READ] id={tid} -> {content}")
        print(f"Ordem atual do cache: {list(cache.usage_order.keys())}")

    print(f"\nEstatísticas finais:")
    print(f"Hits: {cache.hits}, Misses: {cache.misses}")
    print(f"Taxa de acerto: {(cache.hits/(cache.hits + cache.misses))*100:.1f}%")
    print(f"Conteúdo final do cache: {list(cache.cache_data.keys())}")
from collections import deque
from core.cache_interface import CacheInterface
import time

class FIFOCache(CacheInterface):
    """
    Cache que remove o item mais antigo quando cheio (First-In-First-Out).
    Implementa uma política simples onde o primeiro texto a entrar
    será o primeiro a sair quando o cache estiver cheio.
    """
    def __init__(self, capacity: int, disk_reader_func):
        """
        Inicializa o cache FIFO.
        capacity: tamanho máximo do cache
        disk_reader_func: função para ler textos do disco

        Usa deque para implementar a fila FIFO de forma eficiente,
        mantendo a ordem exata de entrada dos textos.
        """
        super().__init__(capacity, disk_reader_func)
        self.queue = deque()  # Fila para controle FIFO (ordem de entrada)
        self.total_time = 0.0  # Tempo total gasto em leituras do disco

    def get_text(self, text_id: int) -> str:
        """
        Obtém um texto do cache ou do disco.
        Se não estiver no cache, remove o item mais antigo se necessário.
        Mantém estatísticas de hits/misses e tempo de leitura.
        """
        # Verifica se está no cache (HIT)
        if text_id in self.cache_data:
            self.hits += 1  # Incrementa contador de acertos
            print(f"[HIT] Texto {text_id} encontrado no cache.")
            return self.cache_data[text_id]
        
        # Não está no cache (MISS) - precisa ler do disco
        self.misses += 1  # Incrementa contador de falhas
        print(f"[MISS] Texto {text_id} não está no cache. Lendo do disco...")
           
        # Se cache cheio, aplica política FIFO (remove o mais antigo)
        if len(self.cache_data) >= self.capacity:
            oldest_id = self.queue.popleft()  # Remove primeiro da fila
            if oldest_id in self.cache_data:
                del self.cache_data[oldest_id]  # Remove do dicionário
            print(f"[FIFO] Removendo texto {oldest_id} do cache (mais antigo).")

        # Lê do disco e contabiliza o tempo gasto
        start_time = time.perf_counter()
        content = self.disk_reader(text_id)
        self.total_time += time.perf_counter() - start_time

        # Atualiza estruturas do cache
        self.cache_data[text_id] = content  # Guarda o texto
        self.queue.append(text_id)  # Registra ordem de entrada
        return content

    def run_simulation(self):
        """
        Placeholder para simulação específica FIFO.
        Simulação real implementada em simulation/simulator.py
        """
        print(f"\n[AVISO] O modo de simulação para o algoritmo {self.__class__.__name__} ainda não foi implementado.")
        print("Pressione Enter para retornar ao modo de leitura...")
        input()


# Teste do algoritmo
if __name__ == '__main__':
    import time

    def dummy_disk_reader(text_id: int) -> str:
        """
        Simula leitura do disco com delay de 50ms.
        Usado apenas para testes do algoritmo FIFO.
        """
        time.sleep(0.05)  # Simula latência de leitura
        return f"Conteúdo do texto {text_id}"

    # Cria cache com 3 posições para demonstração
    cache = FIFOCache(capacity=3, disk_reader_func=dummy_disk_reader)
    
    accesses = [1, 2, 3, 4, 1, 2, 5, 1]
    
    # Executa os acessos e mostra resultados
    for tid in accesses:
        content = cache.get_text(tid)
        print(f"[READ] id={tid} -> {content}")

    # Exibe estatísticas finais do teste
    print("\nEstatísticas:", f"hits={cache.hits}, misses={cache.misses}")
    print("Conteúdo final do cache:", cache.cache_data)
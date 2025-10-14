from abc import ABC, abstractmethod
import time

class CacheInterface(ABC):
    """
    Interface base para implementação de algoritmos de cache.
    Define a estrutura comum e métodos que todo cache deve implementar.
    Fornece funcionalidades básicas de contagem de hits/misses e armazenamento.
    """

    def __init__(self, capacity: int, disk_reader_func):
        """
        Inicializa um novo cache com configurações básicas.
        
        Args:
            capacity: número máximo de itens no cache
            disk_reader_func: função para ler textos do disco
            
        """
        self.capacity = capacity          # Limite máximo de itens
        self.disk_reader = disk_reader_func  # Função para ler do disco
        self.hits = 0                     # Contador de acertos
        self.misses = 0                   # Contador de falhas
        self.cache_data = {}              # Dicionário principal do cache
    
    @abstractmethod
    def get_text(self, text_id: int) -> str:
        """
        Obtém um texto do cache ou do disco.
        
        Cada algoritmo deve implementar:
        - Verificação de hit/miss
        - Política de substituição quando cheio
        - Atualização de estatísticas
        - Gerenciamento do cache_data
        
        """
        pass

    @abstractmethod
    def run_simulation(self):
        """
        Executa simulação específica do algoritmo.
        
        Deve implementar:
        - Geração de padrões de acesso
        - Coleta de métricas
        - Análise de desempenho
        """
        pass

    def get_stats(self) -> dict: ##Retorna estatísticas básicas do cache.
        
        return {"hits": self.hits, "misses": self.misses}

    def get_cached_keys(self): ##Lista os IDs dos textos atualmente no cache.
        
        try:
            return list(self.cache_data.keys())
        except Exception:
            return []

# Código de teste da interface
if __name__ == '__main__':

    def dummy_disk_reader(text_id: int) -> str:
        """
        Simula leitura do disco para testes.
        """
        time.sleep(0.01)  # Simula latência de IO
        return f"Dummy content for id {text_id}"

    class DummyCache(CacheInterface):
        """
        Implementação simples para teste da interface.
        """
        def get_text(self, text_id: int) -> str:
            # Verifica se está no cache
            if text_id in self.cache_data:
                self.hits += 1
                return self.cache_data[text_id]

            # Não está no cache
            self.misses += 1
            content = self.disk_reader(text_id)

            # Se cheio, remove o primeiro item (política simples)
            if len(self.cache_data) >= self.capacity:
                oldest_key = next(iter(self.cache_data))
                del self.cache_data[oldest_key]

            # Adiciona novo item
            self.cache_data[text_id] = content
            return content

        def run_simulation(self):
            print("DummyCache: run_simulation não implementado (apenas teste).")

    # Testa implementação básica
    cache = DummyCache(capacity=2, disk_reader_func=dummy_disk_reader)
    
    accesses = [1, 2, 1, 3, 2]

    for tid in accesses:
        content = cache.get_text(tid)
        print(f"[READ] id={tid} -> {content}")

    # Mostra estatísticas finais
    print()
    print("Stats:", cache.get_stats())
    print("Final cache_data:", cache.cache_data)


from abc import ABC, abstractmethod

class CacheInterface(ABC):
    def __init__(self, capacity: int, disk_reader_func):
        self.capacity = capacity
        self.disk_reader = disk_reader_func
        # Dicionário para armazenar os textos em cache. Chave: text_id, Valor: conteúdo.
        self.cache_data = {}
        # Métricas de performance
        self.hits = 0
        self.misses = 0

    @abstractmethod
    def get_text(self, text_id: int):
        pass

    @abstractmethod
    def run_simulation(self):

        print(f"\n[AVISO] O modo de simulação para o algoritmo {self.__class__.__name__} ainda não foi implementado.")
        print("Pressione Enter para retornar ao modo de leitura...")
        input()
        
    def get_stats(self) -> dict:
        return {"hits": self.hits, "misses": self.misses}

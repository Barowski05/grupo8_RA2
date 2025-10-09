from abc import ABC, abstractmethod

class CacheInterface(ABC):
    """
    Classe Base Abstrata (Interface) que define o contrato para todos os algoritmos de cache.
    Qualquer classe de cache no projeto DEVE herdar desta classe e implementar
    seus métodos abstratos.
    """

    def __init__(self, capacity: int, disk_reader_func):
        """
        Construtor padrão para todos os caches.
        Inicializa os atributos essenciais que todo cache deve ter.
        """
        self.capacity = capacity
        self.disk_reader = disk_reader_func
        self.hits = 0
        self.misses = 0
        self.cache_data = {} 
    
    @abstractmethod
    def get_text(self, text_id: int) -> str:
        """
        Método obrigatório para obter um texto.
        A lógica de hit/miss e de substituição deve ser implementada aqui.
        """
        pass

    @abstractmethod
    def run_simulation(self):
        """
        Método obrigatório para rodar o modo de simulação.
        A ser implementado pelo Aluno D.
        """
        pass


    def get_stats(self) -> dict:
        """
        Retorna as estatísticas de acerto (hits) e falha (misses) do cache.
        Como 'hits' e 'misses' são definidos na classe base, esta função
        funcionará automaticamente para todas as classes filhas.
        """
        return {"hits": self.hits, "misses": self.misses}


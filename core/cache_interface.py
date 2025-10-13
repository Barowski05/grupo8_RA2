from abc import ABC, abstractmethod
import time

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

    def get_cached_keys(self):
        """
        Retorna uma lista com os IDs dos textos atualmente armazenados no cache.
        Implementação padrão que funciona para qualquer subclasse que mantenha
        o dicionário `self.cache_data` (padrão na interface).
        """
        try:
            return list(self.cache_data.keys())
        except Exception:
            return []

# Adicionado: utilitários para testar a interface de forma independente.
if __name__ == '__main__':

    def dummy_disk_reader(text_id: int) -> str:
        """Simula leitura do disco (pequena latência) e retorna conteúdo dummy."""
        time.sleep(0.01)
        return f"Dummy content for id {text_id}"

    class DummyCache(CacheInterface):
        """Implementação mínima para testar a interface CacheInterface."""
        def get_text(self, text_id: int) -> str:
            if text_id in self.cache_data:
                self.hits += 1
                return self.cache_data[text_id]

            self.misses += 1
            content = self.disk_reader(text_id)

            # política simples de substituição: remove o primeiro item inserido (por ordem de dict)
            if len(self.cache_data) >= self.capacity:
                oldest_key = next(iter(self.cache_data))
                del self.cache_data[oldest_key]

            self.cache_data[text_id] = content
            return content

        def run_simulation(self):
            print("DummyCache: run_simulation não implementado (apenas teste).")

    # Sequência de teste
    cache = DummyCache(capacity=2, disk_reader_func=dummy_disk_reader)
    accesses = [1, 2, 1, 3, 2]

    for tid in accesses:
        content = cache.get_text(tid)
        print(f"[READ] id={tid} -> {content}")

    print()
    print("Stats:", cache.get_stats())
    print("Final cache_data:", cache.cache_data)


import os
from core.main import MainApp
from core.cache_interface import CacheInterface
from algorithms.FIFO import FIFOCache

# --- CONFIGURAÇÕES DO PROJETO ---
TEXTS_DIRECTORY = "texts"
CACHE_CAPACITY = 10
# ---------------------------------

class NoCache(CacheInterface):
    """
    Implementação de cache "falso" que agora segue o contrato da CacheInterface.
    Esta correção resolve o TypeError original.
    """
    def __init__(self, capacity: int, disk_reader_func):
        # Chama o construtor da classe pai para inicializar corretamente.
        super().__init__(capacity, disk_reader_func)

    def get_text(self, text_id: int) -> str:
        """Implementação obrigatória de get_text para NoCache."""
        self.misses += 1
        print(f"[NoCache] Cache miss para o texto {text_id}. Acessando o disco.")
        return self.disk_reader(text_id)

    def run_simulation(self):
        """Implementação obrigatória de run_simulation para NoCache."""
        print("\n[AVISO] O algoritmo 'NoCache' é um exemplo e não possui um modo de simulação.")
        print("Pressione Enter para retornar ao modo de leitura...")
        input()


def choose_cache_algorithm():
    """
    Permite ao usuário escolher o algoritmo de cache a ser usado.
    """
    algorithms = {
        "1": ("NoCache (Padrão Aluno A)", NoCache),
        "2": ("FIFO (Aluno B)", FIFOCache),
        # Adicionar os algoritmos dos Alunos C e D aqui no futuro.
    }

    print("--- Escolha o Algoritmo de Cache ---")
    for key, (name, _) in algorithms.items():
        print(f"[{key}] - {name}")
    
    choice = input(">> ")

    
    algorithm_class = algorithms.get(choice, algorithms["1"])[1]
    
    print(f"\nInicializando com o algoritmo '{algorithm_class.__name__}'.\n")
    
  
    return algorithm_class(capacity=CACHE_CAPACITY, disk_reader_func=None)

def main():
    """
    Função principal que inicializa e executa a aplicação.
    """
    cache_instance = choose_cache_algorithm()

    app = MainApp(text_dir=TEXTS_DIRECTORY, cache_algorithm=cache_instance)
    
    cache_instance.disk_reader = app._read_text_from_slow_disk

    app.run()

if __name__ == "__main__":
    main()


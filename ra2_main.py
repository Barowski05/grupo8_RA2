import os
from core.main import MainApp
from core.cache_interface import CacheInterface

# --- CONFIGURAÇÕES DO PROJETO ---
TEXTS_DIRECTORY = "texts"
CACHE_CAPACITY = 10
# ---------------------------------

class NoCache(CacheInterface):
    def get_text(self, text_id: int) -> str:
        self.misses += 1
        print(f"[NoCache] Cache miss para o texto {text_id}. Acessando o disco.")
        return self.disk_reader(text_id)
    def run_simulation(self):
        print("\n[AVISO] O algoritmo 'NoCache' é apenas um exemplo e não possui um modo de simulação.")
        print("A simulação deve ser implementada pelos algoritmos dos Alunos B, C e D.")
        print("Pressione Enter para retornar ao modo de leitura...")
        input()


def choose_cache_algorithm():
    print("Inicializando com o algoritmo padrão 'NoCache'.")
    return NoCache(capacity=CACHE_CAPACITY, disk_reader_func=None)

def main():
    cache_instance = choose_cache_algorithm()
    app = MainApp(text_dir=TEXTS_DIRECTORY, cache_algorithm=cache_instance)
    cache_instance.disk_reader = app._read_text_from_slow_disk

    app.run()

if __name__ == "__main__":
    main()


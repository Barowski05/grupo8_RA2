import os
import time
import contextlib
import builtins
import random
# tentar ativar um backend gráfico e modo interativo do matplotlib, se disponível
try:
    import matplotlib
    _BACKENDS_TO_TRY = ('TkAgg', 'Qt5Agg', 'Qt4Agg', 'WXAgg')
    for _b in _BACKENDS_TO_TRY:
        try:
            matplotlib.use(_b, force=True)
            break
        except Exception:
            continue
    import matplotlib.pyplot as plt  
    plt.ion()
    PLOT_AVAILABLE = True
except Exception:
    PLOT_AVAILABLE = False

from core.main import MainApp
from core.cache_interface import CacheInterface
from algorithms.FIFO import FIFOCache
from algorithms.lfu import LFUCache
from algorithms.MRU import MRUCache
from simulation.simulator import run_simulation_for_algorithm

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
        self.total_time = 0.0

    def get_text(self, text_id: int) -> str:
        """Implementação obrigatória de get_text para NoCache."""
        self.misses += 1
        start_time = time.perf_counter()
        content = self.disk_reader(text_id)
        self.total_time += time.perf_counter() - start_time
        return content

    def run_simulation(self):
        """Implementação obrigatória de run_simulation para NoCache."""
        return

def main():
    """
    Função principal que inicializa e executa a aplicação.
    """
    # Variáveis para armazenar o melhor algoritmo após simulação
    best_cache_instance = None
    best_cache_name = None
    def fast_disk_reader(tid: int) -> str:
        path = os.path.join(TEXTS_DIRECTORY, f"texto_{tid}.txt")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return f"ERROR: missing {tid}"

    def _clear_algorithm_state(alg):
        """Limpa estruturas internas de um algoritmo de cache (cache_data, filas, contadores).
        Usa reset_stats(keep_cache=False) se disponível, caso contrário faz limpeza direta.
        """
        try:
            if hasattr(alg, 'reset_stats'):
                try:
                    alg.reset_stats(keep_cache=False)
                except TypeError:
                    try:
                        alg.reset_stats()
                    except Exception:
                        pass
            else:
                if hasattr(alg, 'cache_data') and isinstance(alg.cache_data, dict):
                    alg.cache_data.clear()
                for attr in ('freq', 'time_stamp', 'per_text_miss', 'per_text_time'):
                    if hasattr(alg, attr):
                        try:
                            getattr(alg, attr).clear()
                        except Exception:
                            pass
                for attr in ('queue', 'usage_order'):
                    if hasattr(alg, attr):
                        try:
                            getattr(alg, attr).clear()
                        except Exception:
                            pass
                # reset simples
                if hasattr(alg, 'hits'):
                    alg.hits = 0
                if hasattr(alg, 'misses'):
                    alg.misses = 0
                if hasattr(alg, 'total_time'):
                    alg.total_time = 0.0
        except Exception:
            pass

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("--- Empresa Texto é Vida - Leitor de Textos (modo simplificado) ---")
        print("Digite -1 para entrar no modo de simulação (compara algoritmos e escolhe o melhor).")
        print("Digite 0 para sair do programa.")
        print("Ou digite um número de 1 a 100 para ler um texto usando o melhor algoritmo encontrado (ou FIFO por padrão).")
        user_input = input(">> ")

        if user_input.strip().lower() == 'c':
            if best_cache_instance is None:
                print("Nenhum algoritmo selecionado ainda. Rode a simulação (-1) primeiro.")
            else:
                keys = best_cache_instance.get_cached_keys()
                print(f"Cache ativo: {best_cache_name} -> {keys}")
            input("Pressione Enter para continuar...")
            continue

        if not user_input.lstrip('-').isdigit():
            print("Entrada inválida. Por favor, digite um número ou 'c'.")
            time.sleep(1.2)
            continue

        choice = int(user_input)

        if choice == 0:
            print("Encerrando o programa. Até logo!")
            break

        if choice == -1:
            candidates = [
                ("NoCache", NoCache),
                ("FIFO", FIFOCache),
                ("LFU", LFUCache),
                ("MRU", MRUCache),
            ]

            
            results = {}
            for name, cls in candidates:
                alg = None
                try:
                    alg = cls(capacity=CACHE_CAPACITY, disk_reader_func=fast_disk_reader)
                except TypeError:
                    try:
                        alg = cls(capacity=CACHE_CAPACITY, disk_reader=fast_disk_reader)
                    except TypeError:
                        try:
                            alg = cls(CACHE_CAPACITY, fast_disk_reader)
                        except Exception:
                            try:
                                alg = cls(capacity=CACHE_CAPACITY)
                                alg.disk_reader = fast_disk_reader
                            except Exception:
                                alg = None
                if alg is None:
                    print(f"Atenção: não foi possível instanciar {name}, pulando.")
                    continue

                seed = random.SystemRandom().randint(0, 2**32 - 1)
                orig_print = builtins.print
                try:
                    builtins.print = lambda *a, **k: None
                    try:
                        summary = run_simulation_for_algorithm(alg, seed=seed, show_plot=PLOT_AVAILABLE)
                    except Exception:
                        summary = {}
                finally:
                    builtins.print = orig_print

                dict_entries = [p for p in summary.values() if isinstance(p, dict) and 'hits' in p and 'total_requests' in p]
                total_hits = sum(p.get('hits', 0) for p in dict_entries)
                total_requests = sum(p.get('total_requests', 0) for p in dict_entries) or 1
                hit_rate = total_hits / total_requests
                results[name] = (hit_rate, alg)
                print(f"{name}: hit_rate={hit_rate:.4f} ({total_hits}/{total_requests}) seed={seed}")

                try:
                    _clear_algorithm_state(alg)
                except Exception:
                    pass

            best_name, best_pair = max(results.items(), key=lambda kv: kv[1][0])
            simulated_alg = best_pair[1]
            best_cache_name = best_name

            alg_class = simulated_alg.__class__
            try:
                best_cache_instance = alg_class(capacity=CACHE_CAPACITY, disk_reader_func=None)
            except Exception:
                best_cache_instance = simulated_alg
            try:
                if hasattr(best_cache_instance, 'cache_data'):
                    best_cache_instance.cache_data.clear()
            except Exception:
                pass
            print(f"{best_cache_name}: best_hit_rate={results[best_cache_name][0]:.4f}")
            input("Pressione Enter para continuar...")
            continue

        # leitura de texto (1-100)
        text_id = choice
        if not 1 <= text_id <= 100:
            print("Número de texto inválido. Por favor, escolha um número entre 1 e 100.")
            time.sleep(1.5)
            continue

        # Se não houve simulação ainda, usar FIFO como padrão
        if best_cache_instance is None:
            print("Nenhuma simulação executada: usando FIFO por padrão.")
            best_cache_instance = FIFOCache(capacity=CACHE_CAPACITY, disk_reader_func=None)
            best_cache_name = 'FIFO'

        # conectar o leitor de disco lento (com delay) ao cache escolhido
        app = MainApp(text_dir=TEXTS_DIRECTORY, cache_algorithm=best_cache_instance)
        best_cache_instance.disk_reader = app._read_text_from_slow_disk

        # executar a leitura do texto
        start_time = time.time()
        content = best_cache_instance.get_text(text_id)
        app._display_text(content, text_id, start_time)

if __name__ == "__main__":
    main()


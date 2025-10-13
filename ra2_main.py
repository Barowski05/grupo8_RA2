import os
import time
import contextlib
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

    # Esta função não é mais usada. Mantida apenas para compatibilidade futura.
    raise NotImplementedError("choose_cache_algorithm não é mais usado; o menu foi simplificado.")

def main():
    """
    Função principal que inicializa e executa a aplicação.
    """
    # Variáveis para armazenar o melhor algoritmo após simulação
    best_cache_instance = None
    best_cache_name = None

    # Função utilitária: leitor rápido (para simulação) — lê arquivos sem sleep
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
                    # se assinatura diferente, apenas chamar sem args
                    try:
                        alg.reset_stats()
                    except Exception:
                        pass
            else:
                if hasattr(alg, 'cache_data') and isinstance(alg.cache_data, dict):
                    alg.cache_data.clear()
                # tentativas genéricas para limpar outras estruturas
                for attr in ('freq', 'time_stamp', 'per_text_miss', 'per_text_time'):
                    if hasattr(alg, attr):
                        try:
                            getattr(alg, attr).clear()
                        except Exception:
                            pass
                # deque/ordereddict/queues
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

        # Permitimos também o comando 'c' para exibir chaves do cache atual
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
            print("\nExecutando simulação entre algoritmos...\n")

            # Instanciar candidatos com leitor rápido
            candidates = [
                ("NoCache", NoCache(capacity=CACHE_CAPACITY, disk_reader_func=fast_disk_reader)),
                ("FIFO", FIFOCache(capacity=CACHE_CAPACITY, disk_reader_func=fast_disk_reader)),
                ("LFU", LFUCache(capacity=CACHE_CAPACITY, disk_reader_func=fast_disk_reader)),
                ("MRU", MRUCache(capacity=CACHE_CAPACITY, disk_reader_func=fast_disk_reader)),
            ]

            results = {}
            for name, alg in candidates:
                # Suprimir saída detalhada (muitos HIT/MISS/evict prints) durante a simulação
                with open(os.devnull, 'w') as devnull:
                    with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
                        summary = run_simulation_for_algorithm(alg, show_plot=False)

                # calcular taxa de acerto agregada (soma de hits / soma de requests)
                total_hits = sum(p['hits'] for p in summary.values())
                total_requests = sum(p['total_requests'] for p in summary.values()) or 1
                hit_rate = total_hits / total_requests
                results[name] = (hit_rate, alg)
                print(f"{name}: hit_rate={hit_rate:.4f} ({total_hits}/{total_requests})")

                # limpar o estado do objeto usado na simulação para garantir que não
                # permaneça cache populado após a simulação
                try:
                    _clear_algorithm_state(alg)
                except Exception:
                    pass

            # escolher melhor algoritmo
            best_name, best_pair = max(results.items(), key=lambda kv: kv[1][0])
            simulated_alg = best_pair[1]
            best_cache_name = best_name

            # Reinstanciar um objeto novo (vazio) da mesma classe para evitar reaproveitar
            # o estado (cache cheio) que foi gerado durante a simulação.
            alg_class = simulated_alg.__class__
            try:
                best_cache_instance = alg_class(capacity=CACHE_CAPACITY, disk_reader_func=None)
            except Exception:
                # fallback: usar a instância simulada caso a reinicialização falhe
                best_cache_instance = simulated_alg
            # Defensive: garantir que o cache esteja vazio (sem chaves remanescentes)
            try:
                if hasattr(best_cache_instance, 'cache_data'):
                    best_cache_instance.cache_data.clear()
            except Exception:
                pass
            print(f"\nMelhor algoritmo segundo a simulação: {best_cache_name} (hit_rate={results[best_cache_name][0]:.4f})")
            print("Um novo objeto deste algoritmo foi criado e será usado para leituras reais (cache limpo).\n")
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


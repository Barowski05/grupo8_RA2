import os
import time
from core.cache_interface import CacheInterface

class MainApp:
    def __init__(self, text_dir: str, cache_algorithm: CacheInterface):
        self.text_dir = text_dir
        self.cache = cache_algorithm
        self.is_running = True

        
        if not os.path.isdir(text_dir) or not os.listdir(text_dir):
            print(f"ERRO: O diretório de textos '{text_dir}' não existe ou está vazio.")
            print("Por favor, execute o script 'generate_texts.py' primeiro para criar os textos.")
            self.is_running = False

    def _read_text_from_slow_disk(self, text_id: int) -> str:
        file_path = os.path.join(self.text_dir, f"texto_{text_id}.txt")
        
        if not os.path.exists(file_path):
            return f"ERRO: Texto com ID {text_id} não encontrado."

        print(f"\nLendo texto {text_id} do disco lento... (aguarde)")
        time.sleep(1.5) 
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"Texto {text_id} carregado com sucesso do disco.")
            return content
        except Exception as e:
            return f"ERRO: Falha ao ler o arquivo para o texto {text_id}: {e}"

    def _display_text(self, content: str, text_id: int, start_time: float):
        """Exibe o conteúdo do texto e as métricas de tempo."""
        end_time = time.time()
        load_time = end_time - start_time
        
        # Limpa o terminal para uma melhor visualização
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("--- CONTEÚDO DO TEXTO ---")
        print(content)
        print("-------------------------\n")
        print(f"Tempo de carregamento: {load_time:.4f} segundos.")
        
        stats = self.cache.get_stats()
        print(f"Estatísticas do Cache ({self.cache.__class__.__name__}): Hits={stats['hits']}, Misses={stats['misses']}")
        print("\nPressione Enter para solicitar um novo texto...")
        input()

    def run(self):
        """Inicia o laço principal da aplicação."""
        if not self.is_running:
            return

        while self.is_running:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("--- Empresa Texto é Vida - Leitor de Textos ---")
            print(f"Usando algoritmo de cache: {self.cache.__class__.__name__}")
            print("\nDigite o número do texto que deseja ler (1-100).")
            print("Digite -1 para entrar no modo de simulação.")
            print("Digite 0 para sair do programa.")
            
            user_input = input(">> ")

            if not user_input.isdigit() and user_input != '-1':
                print("Entrada inválida. Por favor, digite um número.")
                time.sleep(1)
                continue

            text_id = int(user_input)

            if text_id == 0:
                print("Encerrando o programa. Até logo!")
                self.is_running = False
                break
            
            if text_id == -1:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("--- MODO DE SIMULAÇÃO ---")
                self.cache.run_simulation()
                continue

            if not 1 <= text_id <= 100:
                print("Número de texto inválido. Por favor, escolha um número entre 1 e 100.")
                time.sleep(2)
                continue

            start_time = time.time()
            text_content = self.cache.get_text(text_id)
            
            self._display_text(text_content, text_id, start_time)

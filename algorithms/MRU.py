# algorithms/mru_cache.py
from collections import OrderedDict
from core.cache_interface import CacheInterface
import time

class MRUCache(CacheInterface):
    """
    Implementação do algoritmo de cache MRU (Most Recently Used).
    Remove o item mais recentemente usado quando o cache está cheio.
    """
    def __init__(self, capacidade: int, leitor_disco):
        """
        Construtor seguindo o mesmo padrão do FIFO.
        """
        # Chama o construtor da CacheInterface para inicializar atributos comuns
        super().__init__(capacidade, leitor_disco)
        # OrderedDict para controlar a ordem de uso (do menos recente para o mais recente)
        self.ordem_uso = OrderedDict()
        self.tempo_total = 0.0
        self.meu_cache = {}
        self.acertos = 0
        self.erros = 0

    def get_text(self, id_texto: int) -> str:
        """Lê o texto, usando o cache conforme a política MRU."""
        # Se o texto já está no cache → acerto
        if id_texto in self.meu_cache:
            self.acertos += 1
            print(f"[ACERTO] Texto {id_texto} está no cache.")
            # Atualiza a ordem de uso - move para o final (mais recente)
            self.ordem_uso.move_to_end(id_texto)
            return self.meu_cache[id_texto]
        else:
            self.erros += 1
            print(f"[ERRO] Texto {id_texto} não está no cache. Lendo do disco...")
            # Se o cache estiver cheio, remove o MAIS RECENTEMENTE USADO
            if len(self.meu_cache) >= self.capacity:
                # Remove o último item do OrderedDict (mais recente)
                id_mais_recente, _ = self.ordem_uso.popitem(last=True)
                if id_mais_recente in self.meu_cache:
                    del self.meu_cache[id_mais_recente]
                print(f"[MRU] Removendo texto {id_mais_recente} do cache (mais recentemente usado).")
            # Lê o conteúdo do disco
            inicio_leitura = time.perf_counter()
            conteudo = self.disk_reader(id_texto)
            self.tempo_total += time.perf_counter() - inicio_leitura
            # Adiciona o novo texto ao cache e à ordem de uso
            self.meu_cache[id_texto] = conteudo
            self.ordem_uso[id_texto] = True  # Valor não importa, só a chave
            return conteudo

    def run_simulation(self):
        """
        Implementação obrigatória do método de simulação.
        """
        print(f"\n[AVISO] O modo de simulação para o algoritmo {self.__class__.__name__} ainda não foi implementado.")
        print("Pressione Enter para voltar...")
        input()

if __name__ == '__main__':
    import time

    def leitor_disco_teste(id_texto: int) -> str:
        """Simula leitura do disco e retorna conteúdo fictício."""
        time.sleep(0.05)
        return f"Conteúdo do texto {id_texto}"

    # Teste do algoritmo MRU
    meu_cache = MRUCache(capacidade=3, leitor_disco=leitor_disco_teste)
    lista_acessos = [1, 2, 3, 1, 4, 2, 5, 1]

    print("=== TESTE DO MRU ===")
    for id_teste in lista_acessos:
        conteudo = meu_cache.get_text(id_teste)
        print(f"[LEITURA] id={id_teste} -> {conteudo}")
        print(f"Ordem atual do cache: {list(meu_cache.ordem_uso.keys())}")

    print(f"\nEstatísticas finais:")
    print(f"Acertos: {meu_cache.acertos}, Erros: {meu_cache.erros}")
    print(f"Taxa de acerto: {(meu_cache.acertos/(meu_cache.acertos + meu_cache.erros))*100:.1f}%")
    print(f"Conteúdo final do cache: {list(meu_cache.meu_cache.keys())}")
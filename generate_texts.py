import os
import requests
import re

# --- CONFIGURAÇÕES ---
# URL de um livro em texto plano do Projeto Gutenberg (ex: "Os Lusíadas")
BOOK_URL = "https://www.gutenberg.org/cache/epub/3333/pg3333.txt"
# Diretório onde os textos serão salvos
TEXTS_DIRECTORY = "texts"
# Número de textos a serem gerados
NUM_TEXTS = 100
# Mínimo de palavras por arquivo de texto
WORDS_PER_TEXT = 1000
# ---------------------

def download_and_clean_book(url):
    """Baixa o conteúdo de um livro e faz uma limpeza básica."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica se o download foi bem-sucedido
        # Converte para UTF-8 para garantir a compatibilidade de caracteres
        text = response.content.decode('utf-8', errors='ignore')

        # Remove o cabeçalho e o rodapé do Projeto Gutenberg
        start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK"
        end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"
        start_index = text.find(start_marker)
        if start_index != -1:
            start_index += len(start_marker)
            text = text[start_index:]

        end_index = text.find(end_marker)
        if end_index != -1:
            text = text[:end_index]

        # Remove quebras de linha excessivas e espaços em branco
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o livro: {e}")
        return None

def generate_texts():
    """Gera os arquivos de texto a partir do livro baixado."""
    print("Iniciando a geração de textos...")

    # Cria o diretório de textos se ele não existir
    if not os.path.exists(TEXTS_DIRECTORY):
        os.makedirs(TEXTS_DIRECTORY)
        print(f"Diretório '{TEXTS_DIRECTORY}' criado.")

    book_content = download_and_clean_book(BOOK_URL)
    if not book_content:
        print("Não foi possível gerar os textos devido a uma falha no download.")
        return

    words = book_content.split()
    total_words = len(words)

    if total_words < NUM_TEXTS * WORDS_PER_TEXT:
        print("AVISO: O livro fonte é muito curto para gerar 100 textos de 1000 palavras.")
        print("Os textos podem ter menos palavras do que o desejado.")

    word_index = 0
    # Loop para criar 100 arquivos de texto
    for i in range(1, NUM_TEXTS + 1):
        # --- MUDANÇA SOLICITADA (VERSÃO MELHORADA) ---
        # Informa o progresso numa única linha que se atualiza, sem criar 100 linhas no console.
        # O 'end="\r"' faz o cursor voltar ao início da linha a cada impressão.
        print(f"GERANDO TEXTO PARA O PROJETO: {i}/{NUM_TEXTS}", end='\r')
        # --- FIM DA MUDANÇA ---

        start_chunk = word_index
        end_chunk = word_index + WORDS_PER_TEXT
        # Garante que não ultrapasse o limite de palavras do livro
        if end_chunk > total_words:
            end_chunk = total_words

        text_chunk = " ".join(words[start_chunk:end_chunk])
        file_path = os.path.join(TEXTS_DIRECTORY, f"texto_{i}.txt")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_chunk)

        word_index = end_chunk
        # Se chegarmos ao final do livro, recomeçamos do início para garantir 100 textos
        if word_index >= total_words:
            word_index = 0
    
    # Adiciona uma nova linha no final para não sobrepor a última mensagem de progresso.
    print()
    print(f"\n{NUM_TEXTS} arquivos de texto foram gerados com sucesso na pasta '{TEXTS_DIRECTORY}'.")


if __name__ == "__main__":
    generate_texts()


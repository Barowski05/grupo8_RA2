import os
import time

# --- CONFIGURAÇÕES ---
TOTAL_TEXTS = 100
MIN_WORDS = 1001
TEXTS_DIR = "texts"
# --------------------

def create_texts_directory():
    """Cria o diretório de textos se ele não existir."""
    if not os.path.exists(TEXTS_DIR):
        print(f"Criando diretório '{TEXTS_DIR}'...")
        os.makedirs(TEXTS_DIR)
        print("Diretório criado com sucesso.")
    else:
        print(f"Diretório '{TEXTS_DIR}' já existe.")

def generate_text_files():
    """Gera 100 arquivos de texto com mais de 1000 palavras cada."""
    print("\nIniciando a geração de arquivos de texto...")
    
    base_sentence = (
        "Este é um texto de exemplo para o projeto da empresa 'Texto é Vida'. "
        "O objetivo é simular um arquivo com mais de mil palavras para testar "
        "o sistema de cache desenvolvido pelos alunos. A leitura deste arquivo "
        "simula o acesso a um disco forense lento, uma vez que a velocidade de "
        "acesso é uma preocupação central neste projeto de otimização de performance. "
        "Repetiremos esta frase diversas vezes para atingir o comprimento necessário. "
    )
    
    # Cada frase base tem 60 palavras. Repetindo 17 vezes, teremos 1020 palavras.
    long_text_content = (base_sentence + "\n") * 17

    for i in range(1, TOTAL_TEXTS + 1):
        file_path = os.path.join(TEXTS_DIR, f"texto_{i}.txt")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"### INÍCIO DO TEXTO NÚMERO {i} ###\n\n")
                f.write(long_text_content)
                f.write(f"\n### FIM DO TEXTO NÚMERO {i} ###")
            
            # Simula um processo de escrita lento
            time.sleep(0.05) 
            print(f"Arquivo 'texto_{i}.txt' criado com sucesso. Palavras: {len(long_text_content.split())}")

        except IOError as e:
            print(f"Erro ao criar o arquivo {file_path}: {e}")
            break
            
    print(f"\n{TOTAL_TEXTS} arquivos de texto foram gerados no diretório '{TEXTS_DIR}'.")

if __name__ == "__main__":
    create_texts_directory()
    generate_text_files()
    print("\nSetup inicial de textos concluído!")

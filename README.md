# Projeto de Simulação de Algoritmos de Cache

Este projeto implementa e compara diferentes algoritmos de substituição de cache para um sistema de recuperação de textos. O sistema simula um ambiente de produção onde os textos são armazenados em disco e podem ser acessados através de uma camada de cache para melhorar o desempenho.

## Estrutura do Projeto


├── algorithms/           # Implementações dos algoritmos de cache
│   ├── FIFO.py         # Implementação First-In-First-Out
│   ├── LFU.py          # Implementação Least Frequently Used
│   └── MRU.py          # Implementação Most Recently Used
├── core/                # Componentes principais do sistema
│   ├── cache_interface.py  # Classe base abstrata para algoritmos de cache
│   └── main.py            # Lógica principal da aplicação
├── simulation/          # Componentes de simulação
│   └── simulator.py     # Executor e análise de simulação
├── texts/              # Diretório contendo arquivos de texto de teste
├── generate_texts.py   # Script para gerar arquivos de texto de teste
└── ra2_main.py        # Ponto de entrada principal da aplicação


## Algoritmos de Cache Implementados

1. **FIFO (First-In-First-Out)**
O algoritmo FIFO armazena os textos em cache na ordem em que são acessados. Quando o cache atinge sua capacidade máxima, o texto mais antigo (primeiro inserido) é removido para dar espaço a novos textos. É simples e eficiente para cenários onde o padrão de acesso não favorece reutilização frequente dos mesmos itens.

2. **LFU (Least Frequently Used)**
  `` 

3. **MRU (Most Recently Used)**
   ``

## Funcionalidades

- Capacidade de cache configurável (padrão: 10 itens)
- Rastreamento de estatísticas de hit/miss
- Medição de desempenho (tempos de acesso)
- Modo de simulação para comparação de algoritmos
- Teste de múltiplos padrões de acesso
- Capacidades opcionais de plotagem (requer matplotlib)

## Configuração

Os principais parâmetros de configuração são definidos em `ra2_main.py`:

TEXTS_DIRECTORY = "texts"
CACHE_CAPACITY = 10


## Uso

1. Execute a aplicação principal:
  
   python -m ra2_main.py

2. Opções disponíveis:
   - Digite um número (1-100) para ler um texto usando o algoritmo de cache atual
   - Digite -1 para executar o modo de simulação (compara todos os algoritmos)
   - Digite 'c' para visualizar o conteúdo atual do cache
   - Digite 0 para sair

3. Modo de Simulação:
   ``

## Arquitetura do Projeto

- `CacheInterface`: Classe base abstrata que define o contrato para implementações de cache
- Cada algoritmo implementa:
  - `get_text(text_id)`: Lógica principal de cache
  - `run_simulation()`: Suporte à simulação
  - Contagem de hits/misses
  - Estatísticas de desempenho

## Dependências

- Python 3.6+
- matplotlib (para plotagem)
- Módulo Collections (deque, OrderedDict)
- Módulo Time (medição de desempenho)

## Testes

Cada implementação de algoritmo inclui testes unitários básicos que podem ser executados individualmente:

- python -m algorithms.FIFO
- python -m algorithms.LFU
- python -m algorithms.MRU


## Métricas de Desempenho

O sistema rastreia várias métricas de desempenho:
- Hits e misses do cache
- Porcentagem de taxa de acerto
- Tempo total de leitura do disco
- Estatísticas de acesso por texto


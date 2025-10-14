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
- **Mecanismo**: Armazena os textos em uma fila seguindo a ordem temporal de acesso.
- **Política de substituição**: Remove sempre o texto mais antigo quando o cache atinge capacidade máxima.
- **Complexidade**: Operações com estrutura de deque.
- **Cenário ideal**: Aplicações com padrão de acesso linear e pouca repetição de itens.
- **Característica**: Simplicidade de implementação e comportamento previsível.

2. **LFU (Least Frequently Used)**
- **Mecanismo**: Mantém contadores de frequência individuais para cada texto no cache.
- **Política de substituição**: Remove o texto com menor número de acessos históricos.
- **Critério de desempate**: Entre textos com mesma frequência, remove o menos recentemente acessado.
- **Cenário ideal**: Sistemas com "itens populares" bem definidos e estáveis ao longo do tempo.
- **Vantagem**: Protege efetivamente os textos mais frequentemente acessados.

3. **MRU (Most Recently Used)**
- **Mecanismo**: Controla a ordem de acesso através de uma estrutura que mantém o histórico recente
- **Política de substituição**: Remove o texto mais recentemente acessado quando necessário
- **Complexidade**: Operações de tempo constante para acesso e atualização
- **Cenário ideal**: Padrões de acesso sequencial onde itens recentes têm baixa probabilidade de reuso
- **Característica**: Inverte a lógica de prioridade tradicional, privilegiando itens menos recentes

## Funcionalidades

- Capacidade de cache configurável (padrão: 10 itens)
- Rastreamento de estatísticas de hit/miss
- Medição de desempenho (tempos de acesso)
- Modo de simulação para comparação de algoritmos
- Teste de múltiplos padrões de acesso
- Capacidades opcionais de plotagem (requer matplotlib)

## Configuração

Os principais parâmetros de configuração são definidos em `ra2_main.py`:

- TEXTS_DIRECTORY = "texts"
  
- CACHE_CAPACITY = 10


## Uso

1. Execute a aplicação principal:
  
   python -m ra2_main.py

2. Opções disponíveis:
   - Digite um número (1-100) para ler um texto usando o algoritmo de cache atual
   - Digite -1 para executar o modo de simulação (compara todos os algoritmos)
   - Digite 'c' para visualizar o conteúdo atual do cache
   - Digite 0 para sair

3. Modo de Simulação:

Ativado ao digitar -1, este modo executa uma análise de desempenho para comparar todos os algoritmos de cache.

Processo: Simula 3 usuários, cada um fazendo 200 solicitações de texto.
Padrões de Teste: Avalia cada algoritmo sob três cenários de acesso distintos:

- Aleatório Uniforme: Todos os textos têm a mesma chance de serem solicitados.

- Distribuição de Poisson: Concentra os acessos em torno de um grupo específico de textos.

- Ponderado (Hotspot): Um pequeno grupo de textos (30-40) tem 43% de chance de ser escolhido.

Resultado: Ao final, exibe um resumo no terminal com as métricas de hits e misses e gera gráficos comparativos para facilitar a escolha do algoritmo mais eficiente.

## Arquitetura do Projeto

- `CacheInterface`: Classe base abstrata que define o contrato para implementações de cache
- Cada algoritmo implementa:
  - `get_text(text_id)`: Lógica principal de cache
  - `run_simulation()`: Suporte à simulação
  - Contagem de hits/misses
  - Estatísticas de desempenho

## Dependências

- Python 3.11.9
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


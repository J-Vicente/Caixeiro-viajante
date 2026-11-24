# Caixeiro-viajante para inspeção de câmeras de trilha

Projeto acadêmico para comparar algoritmos que planejam uma rota de inspeção pelas câmeras de uma floresta e retornam à câmera de origem. O modelo dos grafos e os algoritmos são independentes da interface gráfica.

## Algoritmos disponíveis na interface

O seletor **Algoritmo** oferece três estratégias:

- **Força bruta — grafo de 5 pontos:** enumera ciclos a partir do vértice `1`, evita contar o percurso inverso como outro ciclo e descarta rotas que usam arestas inexistentes. Encontra o custo ótimo para essa instância pequena.
- **Dijkstra + vizinho mais próximo — grafo de 18 pontos:** calcula os caminhos mínimos entre as câmeras e, a partir dessas distâncias, visita a câmera candidata mais próxima em cada etapa. É uma heurística e não garante o ótimo global. Os caminhos físicos podem passar por vértices intermediários.
- **Dijkstra + bitmask — grafo de 18 pontos:** executa Dijkstra sobre estados formados pelo vértice atual e uma máscara de câmeras visitadas. A máscara impede revisitas antes de completar o ciclo; o retorno à origem só é permitido quando todas as câmeras já foram visitadas. Assim, encontra o ciclo hamiltoniano de menor custo usando as arestas do grafo.

O método com bitmask tem custo exponencial no número de vértices: o espaço de estados pode crescer proporcionalmente a `n × 2ⁿ`. Ele é adequado ao grafo atual de 18 pontos, mas o tempo e a memória aumentam rapidamente para instâncias maiores.

## Executar

Na raiz do projeto, instale as dependências da interface e inicie a janela:

```sh
python -m pip install -r src/caixeiro/requirements.txt
python -m src.caixeiro.UI
```

Na janela, o grafo fica à esquerda. À direita aparecem a imagem da câmera atual e, abaixo, as seções **Menu** e **Sobre o algoritmo**. O Menu permite selecionar o algoritmo, iniciar, pausar, avançar ou reiniciar a simulação e ajustar o intervalo entre as visitas.

As métricas mostram o algoritmo selecionado, o custo acumulado da simulação, o progresso e o tempo de cálculo. A seção **Sobre o algoritmo** apresenta estatísticas específicas de cada estratégia, como rotas avaliadas para a força bruta, relaxamentos de Dijkstra para o vizinho mais próximo e estados, transições e atualizações para o bitmask.

O botão **Detalhar** abre a visualização de dados do algoritmo sem redesenhar o mapa. Para o vizinho mais próximo, ela mostra a tabela de distâncias mínimas e os caminhos físicos usados em cada escolha. Para Dijkstra + bitmask, mostra o total de estados explorados por quantidade de câmeras visitadas e as transições do ciclo encontrado, incluindo a máscara e o custo acumulado.

O intervalo automático inicial é de 1,5 segundo e pode ser alterado pelo botão correspondente no Menu. Os pesos dos grafos são apresentados em unidades de custo, pois as imagens de referência não indicam uma unidade física.

No Ubuntu/Debian, o plugin gráfico XCB do Qt também pode requerer a biblioteca de sistema `libxcb-cursor0`. Se o Qt informar que não consegue carregar o plugin `xcb`, instale-a com:

```sh
sudo apt install libxcb-cursor0
```

## Execução pelo terminal

O módulo principal imprime as etapas implementadas, incluindo a solução por força bruta no grafo pequeno, caminhos mínimos de Dijkstra, a rota do vizinho mais próximo, os dados associados às câmeras e as validações:

```sh
python -m src.caixeiro
```

Esse fluxo de terminal documenta as etapas 1 a 5 do projeto. A seleção interativa entre os três métodos e a visualização do Dijkstra + bitmask estão disponíveis na interface gráfica.

## Estrutura

- `src/caixeiro/modelo.py`: representação e validação básica do grafo.
- `src/caixeiro/dados.py` e `src/caixeiro/dados_grafo_18.py`: vértices, arestas e pesos das duas instâncias.
- `src/caixeiro/forca_bruta.py`: enumeração exata dos ciclos para o grafo de 5 pontos.
- `src/caixeiro/dijkstra.py`: caminhos mínimos, predecessores e contadores de execução.
- `src/caixeiro/vizinho_mais_proximo.py`: heurística gulosa e registro das câmeras candidatas.
- `src/caixeiro/dijkstra_bitmask.py`: Dijkstra sobre estados com máscara de vértices visitados.
- `src/caixeiro/integracao.py`: serviços que conectam grafos, caminhos mínimos e algoritmo guloso.
- `src/caixeiro/dados_cameras.py`: associação das câmeras às fotos de `images_5/` e `images_18/`.
- `src/caixeiro/validacao.py`: verificações de consistência das instâncias e resultados existentes.
- `src/caixeiro/UI/janela.py`: janela principal, seleção do algoritmo e coordenação da simulação.
- `src/caixeiro/UI/grafo_ui.py`: desenho do grafo, pesos, câmeras e progresso da rota.
- `src/caixeiro/UI/camera_ui.py`: carregamento e redimensionamento da foto da câmera atual.
- `src/caixeiro/UI/controles.py`: seleção de algoritmo, controles da simulação e intervalo automático.
- `src/caixeiro/UI/metricas.py` e `src/caixeiro/UI/sobre_algoritmo.py`: métricas da execução.
- `src/caixeiro/UI/detalhes.py`: tabelas detalhadas do Dijkstra + guloso e do Dijkstra + bitmask.
- `src/caixeiro/requirements.txt`: dependências Python da interface gráfica.


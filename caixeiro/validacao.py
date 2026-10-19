"""Valida grafos e resultados antes de apresentá-los na simulação."""

from itertools import permutations
from math import inf, isclose, isfinite

from .dijkstra import ResultadoDijkstra, dijkstra
from .forca_bruta import ResultadoForcaBruta
from .modelo import Grafo
from .vizinho_mais_proximo import ResultadoGuloso


def validar_grafo(grafo: Grafo, origem: str) -> tuple[str, ...]:
    """Valida estrutura, pesos, arquivos associados e conectividade de ciclo."""
    erros: list[str] = []
    vertices = grafo.vertices
    conhecidos = set(vertices)
    if len(conhecidos) != len(vertices):
        erros.append("Há identificadores de vértices duplicados.")
    if origem not in conhecidos:
        erros.append(f"A origem {origem} não pertence ao grafo.")
        return tuple(erros)

    for (u, v), peso in grafo.arestas.items():
        if u not in conhecidos or v not in conhecidos:
            erros.append(f"A aresta {u}–{v} referencia vértice desconhecido.")
        if u == v:
            erros.append(f"A aresta {u}–{v} é um laço não permitido.")
        if not isinstance(peso, (int, float)) or not isfinite(peso) or peso < 0:
            erros.append(f"A aresta {u}–{v} tem peso inválido para Dijkstra.")
        if not grafo.direcionado and (v, u) in grafo.arestas:
            erros.append(f"A aresta não dirigida {u}–{v} foi cadastrada nos dois sentidos.")

    if grafo.cameras and set(grafo.cameras) != conhecidos:
        erros.append("O cadastro de câmeras não corresponde exatamente aos vértices.")
    for identificador, camera in grafo.cameras.items():
        if camera.identificador != identificador:
            erros.append(f"O identificador do cadastro da câmera {identificador} não confere.")
        if not camera.foto.is_file():
            erros.append(f"A foto da câmera {identificador} não foi encontrada: {camera.foto}.")

    if erros:
        return tuple(f"ERRO: {erro}" for erro in erros)

    # Para grafos não dirigidos, cada aresta é representada uma vez e vale
    # nos dois sentidos. Grafos dirigidos podem ser assimétricos.
    orientacao = "dirigido" if grafo.direcionado else "não dirigido e simétrico"
    resultados = {v: dijkstra(grafo, v) for v in vertices}
    inalcançaveis = [v for v in vertices if resultados[origem].distancias[v] == inf]
    sem_retorno = [v for v in vertices if resultados[v].distancias[origem] == inf]
    if inalcançaveis:
        erros.append(f"Câmeras inalcançáveis a partir de {origem}: {', '.join(inalcançaveis)}.")
    if sem_retorno:
        erros.append(f"Sem caminho de retorno à origem a partir de: {', '.join(sem_retorno)}.")
    if erros:
        return tuple(f"ERRO: {erro}" for erro in erros)
    return (f"OK: Grafo {orientacao}; identificadores, arestas, pesos e fotos válidos.",
            f"OK: Todas as {len(vertices)} câmeras são alcançáveis e têm retorno à origem {origem}.")


def validar_dijkstra(grafo: Grafo, resultado: ResultadoDijkstra) -> tuple[str, ...]:
    """Confere origem, distâncias e soma dos caminhos reconstruídos."""
    erros: list[str] = []
    if resultado.origem not in grafo.vertices:
        return ("ERRO: Dijkstra retornou uma origem ausente do grafo.",)
    if resultado.distancias.get(resultado.origem) != 0:
        erros.append("A distância da origem até ela mesma não é zero.")
    for destino in grafo.vertices:
        distancia = resultado.distancias.get(destino, inf)
        caminho = resultado.caminho_ate(destino)
        if distancia == inf:
            if caminho is not None:
                erros.append(f"O destino {destino} tem caminho apesar de ser inalcançável.")
            continue
        if caminho is None or caminho[0] != resultado.origem or caminho[-1] != destino:
            erros.append(f"O caminho reconstruído até {destino} está incompleto.")
            continue
        pesos = [grafo.peso(a, b) for a, b in zip(caminho, caminho[1:])]
        if any(peso is None for peso in pesos):
            erros.append(f"O caminho até {destino} usa aresta inexistente.")
            continue
        custo = sum(peso for peso in pesos if peso is not None)
        if not isclose(custo, distancia):
            erros.append(f"O custo reconstruído até {destino} não confere com Dijkstra.")
    for (u, v), peso in grafo.arestas.items():
        if resultado.distancias[u] < inf and resultado.distancias[v] > resultado.distancias[u] + peso:
            erros.append(f"A aresta {u}–{v} revela um caminho mais curto não refletido em Dijkstra.")
        if not grafo.direcionado and resultado.distancias[v] < inf and resultado.distancias[u] > resultado.distancias[v] + peso:
            erros.append(f"A aresta {v}–{u} revela um caminho mais curto não refletido em Dijkstra.")
    return tuple(f"ERRO: {erro}" for erro in erros)


def validar_forca_bruta(grafo: Grafo, resultado: ResultadoForcaBruta) -> tuple[str, ...]:
    """Confere o ótimo por uma enumeração independente de todos os sentidos."""
    if grafo.direcionado or resultado.origem not in grafo.vertices:
        return ("ERRO: Não foi possível validar a saída de força bruta neste grafo/origem.",)
    restantes = tuple(v for v in grafo.vertices if v != resultado.origem)
    custos: list[float] = []
    rotas_viaveis: set[tuple[str, ...]] = set()
    for ordem in permutations(restantes):
        rota = (resultado.origem, *ordem, resultado.origem)
        pesos = [grafo.peso(a, b) for a, b in zip(rota, rota[1:])]
        if any(peso is None for peso in pesos):
            continue
        custos.append(sum(peso for peso in pesos if peso is not None))
        rotas_viaveis.add(rota)
    minimo = min(custos, default=None)
    if minimo != resultado.custo_minimo:
        return (f"ERRO: O custo da força bruta ({resultado.custo_minimo}) difere da enumeração independente ({minimo}).",)
    if not resultado.rotas_otimas or any(rota not in rotas_viaveis for rota in resultado.rotas_otimas):
        return ("ERRO: A rota ótima informada não corresponde a um ciclo viável.",)
    for rota in resultado.rotas_otimas:
        pesos = [grafo.peso(a, b) for a, b in zip(rota, rota[1:])]
        custo_rota = sum(peso for peso in pesos if peso is not None)
        if custo_rota != minimo:
            return ("ERRO: O custo de uma rota informada como ótima não confere com o mínimo.",)
    return (f"OK: Ótimo confirmado por enumeração independente: custo {minimo:g}; {len(custos)} ciclos direcionados viáveis.",)


def validar_guloso(
    vertices: tuple[str, ...],
    matriz: dict[str, dict[str, float]],
    resultado: ResultadoGuloso,
) -> tuple[str, ...]:
    """Confere cobertura, fechamento, custo e escolha mínima em cada passo."""
    if resultado.rota is None or resultado.custo_total is None:
        return ("ERRO: O guloso não produziu um ciclo completo.",)
    rota = resultado.rota
    if not rota or rota[0] != resultado.origem or rota[-1] != resultado.origem:
        return ("ERRO: A rota gulosa não começa e termina na origem.",)
    if len(rota) != len(vertices) + 1 or set(rota[:-1]) != set(vertices):
        return ("ERRO: A rota gulosa não visita cada câmera exatamente uma vez.",)
    custo = 0.0
    nao_visitados = set(vertices) - {resultado.origem}
    for atual, proximo in zip(rota, rota[1:]):
        trecho = matriz[atual][proximo]
        if trecho == inf:
            return (f"ERRO: O trecho {atual} → {proximo} não tem caminho possível.",)
        if nao_visitados:
            alternativas = [matriz[atual][v] for v in nao_visitados if matriz[atual][v] < inf]
            if not alternativas or trecho > min(alternativas):
                return (f"ERRO: A escolha de {proximo} a partir de {atual} não era a mais próxima.",)
        custo += trecho
        nao_visitados.discard(proximo)
    if not isclose(custo, resultado.custo_total):
        return (f"ERRO: A soma dos trechos ({custo:g}) difere do custo declarado ({resultado.custo_total:g}).",)
    return (f"OK: Rota completa; {len(vertices)} câmeras visitadas, retorno à origem e escolhas mínimas confirmados (custo {custo:g}).",)


def validar_caso_dijkstra() -> tuple[str, ...]:
    """Exemplo conhecido em que um caminho indireto vence a aresta direta."""
    exemplo = Grafo(
        vertices=("A", "B", "C", "D"),
        arestas={("A", "B"): 10, ("A", "C"): 3, ("C", "B"): 2, ("B", "D"): 4, ("C", "D"): 20},
    )
    resultado = dijkstra(exemplo, "A")
    caminho = resultado.caminho_ate("D")
    if resultado.distancias["D"] != 9 or caminho != ("A", "C", "B", "D"):
        return ("ERRO: O exemplo conhecido de Dijkstra falhou.",)
    return ("OK: Exemplo de Dijkstra confirmado: A → C → B → D, custo 9 (melhor que A → B, custo 10).",)

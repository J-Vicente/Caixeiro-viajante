"""Busca de um ciclo hamiltoniano com Dijkstra sobre estados com máscara."""

from dataclasses import dataclass
from heapq import heappop, heappush
from math import inf

from .modelo import Grafo


@dataclass(frozen=True)
class PassoBitmask:
    origem: str
    destino: str
    custo_aresta: float
    mascara_visitados: int
    vertices_visitados: tuple[str, ...]
    custo_acumulado: float


@dataclass(frozen=True)
class CamadaBitmask:
    vertices_visitados: int
    estados_processados: int
    arestas_examinadas: int
    atualizacoes: int


@dataclass(frozen=True)
class ResultadoDijkstraBitmask:
    origem: str
    rota: tuple[str, ...] | None
    custo_total: float | None
    passos: tuple[PassoBitmask, ...]
    estados_processados: int
    arestas_examinadas: int
    transicoes_validas: int
    atualizacoes_estado: int
    camadas: tuple[CamadaBitmask, ...]


def resolver_com_bitmask(grafo: Grafo, origem: str) -> ResultadoDijkstraBitmask:
    """Encontra o ciclo mais barato sem revisitar vértices antes do retorno.

    Cada estado do Dijkstra é composto pelo vértice atual e pelo conjunto de
    vértices já visitados. As transições só avançam para vértices ainda não
    visitados; a aresta de retorno à origem só é liberada ao completar a máscara.
    """
    if origem not in grafo.vertices:
        raise ValueError(f"Origem desconhecida: {origem}.")
    if grafo.direcionado:
        raise ValueError("Dijkstra + bitmask requer um grafo não dirigido.")

    vertices = grafo.vertices
    total = len(vertices)
    indices = {vertice: indice for indice, vertice in enumerate(vertices)}
    origem_indice = indices[origem]
    mascara_completa = (1 << total) - 1

    adjacencias: list[list[tuple[int, float]]] = [[] for _ in vertices]
    for (u, v), peso in grafo.arestas.items():
        adjacencias[indices[u]].append((indices[v], peso))
        adjacencias[indices[v]].append((indices[u], peso))

    mascara_inicial = 1 << origem_indice
    estado_inicial = (origem_indice, mascara_inicial)
    distancias = {estado_inicial: 0.0}
    predecessores: dict[tuple[int, int], tuple[int, int] | None] = {
        estado_inicial: None
    }
    fila: list[tuple[float, int, int]] = [(0.0, *estado_inicial)]
    estados_processados = arestas_examinadas = transicoes_validas = 0
    atualizacoes_estado = 0
    contagens_camadas: dict[int, list[int]] = {}
    estado_final: tuple[int, int] | None = None

    while fila:
        custo, atual, mascara = heappop(fila)
        estado = (atual, mascara)
        if custo != distancias.get(estado, inf):
            continue

        visitados = mascara.bit_count()
        contagem = contagens_camadas.setdefault(visitados, [0, 0, 0])
        contagem[0] += 1
        estados_processados += 1

        if atual == origem_indice and mascara == mascara_completa:
            estado_final = estado
            break

        for vizinho, peso in adjacencias[atual]:
            arestas_examinadas += 1
            contagem[1] += 1
            bit_vizinho = 1 << vizinho
            if vizinho == origem_indice:
                if mascara != mascara_completa:
                    continue
                nova_mascara = mascara
            else:
                if mascara & bit_vizinho:
                    continue
                nova_mascara = mascara | bit_vizinho

            transicoes_validas += 1
            novo_estado = (vizinho, nova_mascara)
            novo_custo = custo + peso
            if novo_custo < distancias.get(novo_estado, inf):
                distancias[novo_estado] = novo_custo
                predecessores[novo_estado] = estado
                heappush(fila, (novo_custo, vizinho, nova_mascara))
                atualizacoes_estado += 1
                contagens_camadas.setdefault(nova_mascara.bit_count(), [0, 0, 0])[2] += 1

    camadas = tuple(
        CamadaBitmask(nivel, *contagens_camadas[nivel])
        for nivel in sorted(contagens_camadas)
    )
    if estado_final is None:
        return ResultadoDijkstraBitmask(
            origem,
            None,
            None,
            (),
            estados_processados,
            arestas_examinadas,
            transicoes_validas,
            atualizacoes_estado,
            camadas,
        )

    estados_rota = []
    estado: tuple[int, int] | None = estado_final
    while estado is not None:
        estados_rota.append(estado)
        estado = predecessores[estado]
    estados_rota.reverse()

    passos: list[PassoBitmask] = []
    for anterior, seguinte in zip(estados_rota, estados_rota[1:]):
        atual_indice, mascara_anterior = anterior
        proximo_indice, mascara_seguinte = seguinte
        custo_aresta = distancias[seguinte] - distancias[anterior]
        visitados = tuple(
            vertice
            for indice, vertice in enumerate(vertices)
            if mascara_seguinte & (1 << indice)
        )
        passos.append(
            PassoBitmask(
                vertices[atual_indice],
                vertices[proximo_indice],
                custo_aresta,
                mascara_seguinte,
                visitados,
                distancias[seguinte],
            )
        )

    rota = tuple(vertices[indice] for indice, _ in estados_rota)
    return ResultadoDijkstraBitmask(
        origem,
        rota,
        distancias[estado_final],
        tuple(passos),
        estados_processados,
        arestas_examinadas,
        transicoes_validas,
        atualizacoes_estado,
        camadas,
    )

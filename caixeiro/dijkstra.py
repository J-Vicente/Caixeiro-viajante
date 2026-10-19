"""Caminhos mínimos em grafos com pesos não negativos."""

from dataclasses import dataclass
from heapq import heappop, heappush
from math import inf

from .modelo import Grafo


@dataclass(frozen=True)
class ResultadoDijkstra:
    origem: str
    distancias: dict[str, float]
    predecessores: dict[str, str | None]

    def caminho_ate(self, destino: str) -> tuple[str, ...] | None:
        """Reconstrói o caminho; devolve None se o destino for inalcançável."""
        if destino not in self.distancias:
            raise ValueError(f"Destino desconhecido: {destino}.")
        if self.distancias[destino] == inf:
            return None
        caminho = []
        atual: str | None = destino
        while atual is not None:
            caminho.append(atual)
            if atual == self.origem:
                break
            atual = self.predecessores[atual]
        if caminho[-1] != self.origem:
            return None
        return tuple(reversed(caminho))


def dijkstra(grafo: Grafo, origem: str) -> ResultadoDijkstra:
    """Calcula distâncias mínimas da origem a todos os vértices."""
    if origem not in grafo.vertices:
        raise ValueError(f"Origem desconhecida: {origem}.")
    adjacencias: dict[str, list[tuple[str, float]]] = {v: [] for v in grafo.vertices}
    for (u, v), peso in grafo.arestas.items():
        adjacencias[u].append((v, peso))
        if not grafo.direcionado:
            adjacencias[v].append((u, peso))

    distancias = {v: inf for v in grafo.vertices}
    predecessores: dict[str, str | None] = {v: None for v in grafo.vertices}
    distancias[origem] = 0
    fila: list[tuple[float, str]] = [(0, origem)]

    while fila:
        distancia_atual, atual = heappop(fila)
        if distancia_atual != distancias[atual]:
            continue
        for vizinho, peso in adjacencias[atual]:
            alternativa = distancia_atual + peso
            if alternativa < distancias[vizinho]:
                distancias[vizinho] = alternativa
                predecessores[vizinho] = atual
                heappush(fila, (alternativa, vizinho))

    return ResultadoDijkstra(origem, distancias, predecessores)

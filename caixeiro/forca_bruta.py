"""Busca exata de ciclos hamiltonianos por enumeração."""

from dataclasses import dataclass
from itertools import permutations

from .modelo import Grafo


@dataclass(frozen=True)
class ResultadoForcaBruta:
    origem: str
    ciclos_candidatos: int
    ciclos_viaveis: int
    custo_minimo: float | None
    rotas_otimas: tuple[tuple[str, ...], ...]
    avaliacoes_arestas: int

    @property
    def ciclos_descartados(self) -> int:
        return self.ciclos_candidatos - self.ciclos_viaveis


def resolver(grafo: Grafo, origem: str) -> ResultadoForcaBruta:
    """Avalia ciclos a partir da origem, ignorando o percurso inverso duplicado."""
    if origem not in grafo.vertices:
        raise ValueError(f"Origem desconhecida: {origem}.")
    if len(grafo.vertices) < 3:
        raise ValueError("São necessários ao menos três vértices para formar um ciclo.")
    if grafo.direcionado:
        raise ValueError("A etapa 1 foi definida para grafos não dirigidos.")

    restantes = tuple(v for v in grafo.vertices if v != origem)
    melhor: float | None = None
    otimas: list[tuple[str, ...]] = []
    candidatas = viaveis = avaliacoes_arestas = 0

    for ordem in permutations(restantes):
        if ordem[0] > ordem[-1]:
            continue
        candidatas += 1
        rota = (origem, *ordem, origem)
        pesos = [grafo.peso(a, b) for a, b in zip(rota, rota[1:])]
        avaliacoes_arestas += len(pesos)
        if any(peso is None for peso in pesos):
            continue

        viaveis += 1
        custo = sum(peso for peso in pesos if peso is not None)
        if melhor is None or custo < melhor:
            melhor = custo
            otimas = [rota]
        elif custo == melhor:
            otimas.append(rota)

    return ResultadoForcaBruta(
        origem=origem,
        ciclos_candidatos=candidatas,
        ciclos_viaveis=viaveis,
        custo_minimo=melhor,
        rotas_otimas=tuple(otimas),
        avaliacoes_arestas=avaliacoes_arestas,
    )

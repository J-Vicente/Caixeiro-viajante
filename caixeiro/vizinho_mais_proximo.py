"""Heurística gulosa do vizinho mais próximo sobre uma matriz de custos."""

from dataclasses import dataclass
from math import inf


@dataclass(frozen=True)
class ResultadoGuloso:
    origem: str
    rota: tuple[str, ...] | None
    custo_total: float | None
    passos: tuple[tuple[str, str, float], ...]
    candidatos_por_passo: tuple[tuple[tuple[str, float], ...], ...] = ()


def vizinho_mais_proximo(
    vertices: tuple[str, ...],
    distancias: dict[str, dict[str, float]],
    origem: str,
) -> ResultadoGuloso:
    """Visita sempre o vértice não visitado mais próximo e fecha o ciclo."""
    if origem not in vertices:
        raise ValueError(f"Origem desconhecida: {origem}.")
    if len(set(vertices)) != len(vertices):
        raise ValueError("Os identificadores dos vértices devem ser únicos.")
    nao_visitados = set(vertices) - {origem}
    rota = [origem]
    passos: list[tuple[str, str, float]] = []
    candidatos_por_passo: list[tuple[tuple[str, float], ...]] = []
    atual = origem
    custo_total = 0.0

    while nao_visitados:
        alcancaveis = sorted(
            (distancias[atual][destino], destino)
            for destino in nao_visitados
            if distancias[atual][destino] < inf
        )
        if not alcancaveis:
            return ResultadoGuloso(
                origem, None, None, tuple(passos), tuple(candidatos_por_passo)
            )
        candidatos_por_passo.append(
            tuple((destino, custo) for custo, destino in alcancaveis)
        )
        custo, proximo = alcancaveis[0]
        passos.append((atual, proximo, custo))
        custo_total += custo
        rota.append(proximo)
        nao_visitados.remove(proximo)
        atual = proximo

    custo_retorno = distancias[atual][origem]
    if custo_retorno == inf:
        return ResultadoGuloso(
            origem, None, None, tuple(passos), tuple(candidatos_por_passo)
        )
    passos.append((atual, origem, custo_retorno))
    custo_total += custo_retorno
    rota.append(origem)
    return ResultadoGuloso(
        origem,
        tuple(rota),
        custo_total,
        tuple(passos),
        tuple(candidatos_por_passo),
    )

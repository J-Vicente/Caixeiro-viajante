"""Serviços que conectam o modelo de dados aos algoritmos."""

from .dijkstra import ResultadoDijkstra, dijkstra
from .modelo import Grafo
from .vizinho_mais_proximo import ResultadoGuloso, vizinho_mais_proximo


def caminhos_minimos(grafo: Grafo) -> dict[str, ResultadoDijkstra]:
    """Calcula resultados de Dijkstra para todas as origens."""
    return {
        origem: dijkstra(grafo, origem)
        for origem in grafo.vertices
    }


def matriz_distancias(
    grafo: Grafo,
    resultados: dict[str, ResultadoDijkstra] | None = None,
) -> dict[str, dict[str, float]]:
    """Monta os custos entre todos os pares usando Dijkstra uma vez por origem."""
    caminhos = resultados if resultados is not None else caminhos_minimos(grafo)
    return {origem: resultado.distancias for origem, resultado in caminhos.items()}


def planejar_rota_gulosa(grafo: Grafo, origem: str) -> ResultadoGuloso:
    """Executa Dijkstra para todos os vértices e aplica vizinho mais próximo."""
    distancias = matriz_distancias(grafo)
    return vizinho_mais_proximo(grafo.vertices, distancias, origem)

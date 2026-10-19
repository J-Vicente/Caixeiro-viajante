"""Modelo mínimo para grafos ponderados não dirigidos."""

from dataclasses import dataclass, field
from math import isfinite
from pathlib import Path


@dataclass(frozen=True)
class Camera:
    """Dados de uma câmera e o caminho para sua fotografia."""

    identificador: str
    foto: Path
    posicao_desenho: tuple[float, float] | None = None


@dataclass(frozen=True)
class ResultadoRota:
    """Formato comum para resultados apresentados pela aplicação."""

    algoritmo: str
    origem: str
    rota: tuple[str, ...]
    custo_total: float
    unidade: str
    duracao_segundos: float | None = None
    status: str = "concluída"


@dataclass(frozen=True)
class PassoSimulacao:
    """Estado acumulado de um passo futuro da simulação visual."""

    indice: int
    camera_atual: str
    proximo_trecho: tuple[str, str] | None
    distancia_acumulada: float


@dataclass(frozen=True)
class Grafo:
    vertices: tuple[str, ...]
    arestas: dict[tuple[str, str], float]
    direcionado: bool = False
    unidade: str = "unidades de custo"
    cameras: dict[str, Camera] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if len(set(self.vertices)) != len(self.vertices):
            raise ValueError("Os identificadores dos vértices devem ser únicos.")
        conhecidos = set(self.vertices)
        if self.cameras:
            if set(self.cameras) != conhecidos:
                raise ValueError("Cada vértice do grafo deve ter exatamente uma câmera associada.")
            for identificador, camera in self.cameras.items():
                if camera.identificador != identificador:
                    raise ValueError("A chave da câmera deve corresponder ao seu identificador.")
        for (origem, destino), peso in self.arestas.items():
            if origem not in conhecidos or destino not in conhecidos:
                raise ValueError(f"Aresta referencia vértice desconhecido: {origem}, {destino}.")
            if origem == destino:
                raise ValueError("Laços não são aceitos neste modelo.")
            if not isfinite(peso) or peso < 0:
                raise ValueError("Os pesos devem ser números finitos não negativos.")
            if not self.direcionado and (destino, origem) in self.arestas:
                raise ValueError("Informe cada aresta não dirigida apenas uma vez.")

    def peso(self, origem: str, destino: str) -> float | None:
        """Retorna o peso da aresta ou None quando ela não existe."""
        if (origem, destino) in self.arestas:
            return self.arestas[(origem, destino)]
        if not self.direcionado:
            return self.arestas.get((destino, origem))
        return None

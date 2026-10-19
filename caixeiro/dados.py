"""Instâncias transcritas das imagens fornecidas."""

from .modelo import Grafo
from .dados_cameras import CAMERAS_5


VERTICES_5 = ("1", "2", "3", "4", "5")

GRAFO_5 = Grafo(
    vertices=VERTICES_5,
    arestas={
        ("1", "2"): 2,
        ("1", "4"): 3,
        ("1", "5"): 6,
        ("2", "3"): 4,
        ("2", "4"): 3,
        ("3", "4"): 7,
        ("3", "5"): 3,
        ("4", "5"): 3,
    },
    cameras=CAMERAS_5,
)

"""Cadastro de câmeras e fotos locais de cada instância do grafo."""

from pathlib import Path

from .modelo import Camera


PASTA_DADOS = Path(__file__).resolve().parent

POSICOES_5 = {
    "1": (0.04, 0.36), "2": (0.48, 0.00), "3": (0.96, 0.37),
    "4": (0.25, 0.90), "5": (0.75, 0.91),
}
POSICOES_18 = {
    "1": (0.03, 0.31), "2": (0.09, 0.12), "3": (0.30, 0.08),
    "4": (0.53, 0.04), "5": (0.72, 0.25), "6": (0.85, 0.22),
    "7": (0.95, 0.06), "8": (0.25, 0.35), "9": (0.47, 0.28),
    "10": (0.66, 0.39), "11": (0.92, 0.39), "12": (0.15, 0.47),
    "13": (0.30, 0.50), "14": (0.59, 0.50), "15": (0.74, 0.55),
    "16": (0.39, 0.66), "17": (0.72, 0.68), "18": (0.87, 0.67),
}

# Mantém para os vértices 1 a 18 a associação criada anteriormente.
ARQUIVOS_FOTO_18 = (
    "coiote.jpg",
    "pumazoom.jpg",
    "coruja.jpg",
    "macacorindo.jpg",
    "lobo.jpg",
    "macaco.jpg",
    "surpresa.png",
    "onca.jpg",
    "veadobrilhando.jpg",
    "passaro.jpg",
    "puma.jpg",
    "raposa.jpg",
    "ursopolar.jpg",
    "veadocheirando.jpg",
    "veadolingua.jpg",
    "veadosaltando.jpg",
    "tigre.jpg",
    "macacozoom.jpg",
)

CAMERAS_5 = {
    str(indice): Camera(
        identificador=str(indice),
        foto=PASTA_DADOS / "images_5" / f"{indice}.jpeg",
        posicao_desenho=POSICOES_5[str(indice)],
    )
    for indice in range(1, 6)
}

CAMERAS_18 = {
    str(indice): Camera(
        identificador=str(indice),
        foto=PASTA_DADOS / "images_18" / nome_arquivo,
        posicao_desenho=POSICOES_18[str(indice)],
    )
    for indice, nome_arquivo in enumerate(ARQUIVOS_FOTO_18, start=1)
}

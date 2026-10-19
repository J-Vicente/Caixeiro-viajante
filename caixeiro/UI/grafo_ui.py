"""Vista central do grafo, com pesos, câmeras e progresso da rota."""

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QVBoxLayout,
    QWidget,
)

from ..modelo import Grafo


class GrafoUI(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.cena = QGraphicsScene(self)
        self.vista = QGraphicsView(self.cena)
        self.vista.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.vista.setBackgroundBrush(QColor("#f7f9fc"))
        self.vista.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.vista.setMinimumSize(520, 400)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.vista)
        self._grafo: Grafo | None = None

    def atualizar(
        self,
        grafo: Grafo,
        arestas_percorridas: set[frozenset[str]] | None = None,
        arestas_proximas: set[frozenset[str]] | None = None,
        cameras_visitadas: set[str] | None = None,
        camera_atual: str | None = None,
    ) -> None:
        self._grafo = grafo
        arestas_percorridas = arestas_percorridas or set()
        arestas_proximas = arestas_proximas or set()
        cameras_visitadas = cameras_visitadas or set()
        self.cena.clear()
        self.cena.setSceneRect(0, 0, 1000, 680)
        self._adicionar_fundo_floresta(grafo)

        posicoes_fonte = {
            identificador: camera.posicao_desenho
            for identificador, camera in grafo.cameras.items()
        }
        if len(posicoes_fonte) != len(grafo.vertices) or any(
            value is None for value in posicoes_fonte.values()
        ):
            posicoes = self._disposicao_circular(grafo.vertices)
        else:
            pontos = {identificador: ponto for identificador, ponto in posicoes_fonte.items() if ponto}
            xs = [ponto[0] for ponto in pontos.values()]
            ys = [ponto[1] for ponto in pontos.values()]
            if len(grafo.vertices) == 5:
                # Preserva o posicionamento relativo das cinco clareiras da foto.
                posicoes = {
                    identificador: (58 + ponto[0] * 884, 48 + ponto[1] * 584)
                    for identificador, ponto in pontos.items()
                }
            else:
                largura = max(max(xs) - min(xs), 0.001)
                altura = max(max(ys) - min(ys), 0.001)
                posicoes = {
                    identificador: (
                        58 + (ponto[0] - min(xs)) / largura * 884,
                        48 + (ponto[1] - min(ys)) / altura * 584,
                    )
                    for identificador, ponto in pontos.items()
                }

        for indice_aresta, ((origem, destino), peso) in enumerate(grafo.arestas.items()):
            x1, y1 = posicoes[origem]
            x2, y2 = posicoes[destino]
            chave = frozenset((origem, destino))
            if chave in arestas_proximas:
                cor, largura = QColor("#e67e22"), 5
            elif chave in arestas_percorridas:
                cor, largura = QColor("#00ff00"), 4
            else:
                cor, largura = QColor("#666666"), 2 #f2f2f2 -- cor para destacar as arestas
            linha = QGraphicsLineItem(x1, y1, x2, y2)
            linha.setPen(QPen(cor, largura, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            linha.setZValue(1)
            self.cena.addItem(linha)
            dx, dy = x2 - x1, y2 - y1
            comprimento = max((dx * dx + dy * dy) ** 0.5, 1)
            lado = 1 if indice_aresta % 2 == 0 else -1
            deslocamento_x = -dy / comprimento * 10 * lado
            deslocamento_y = dx / comprimento * 10 * lado
            rotulo = QGraphicsSimpleTextItem(f"{peso:g}")
            rotulo.setBrush(QBrush(QColor("#ffffff")))
            rotulo.setFont(self._fonte(11, True))
            caixa_texto = rotulo.boundingRect()
            meio_x = (x1 + x2) / 2 + deslocamento_x
            meio_y = (y1 + y2) / 2 + deslocamento_y
            rotulo.setZValue(4)
            rotulo.setPos(meio_x - caixa_texto.width() / 2, meio_y - caixa_texto.height() / 2)
            self.cena.addItem(rotulo)

        for identificador in grafo.vertices:
            x, y = posicoes[identificador]
            if identificador == camera_atual:
                preenchimento, contorno = QColor("#f6c85f"), QColor("#b97800")
            elif identificador in cameras_visitadas:
                preenchimento, contorno = QColor("#76c7a8"), QColor("#138a63")
            else:
                preenchimento, contorno = QColor("#ffffff"), QColor("#52657a")
            no = QGraphicsEllipseItem(x - 19, y - 19, 38, 38)
            no.setBrush(QBrush(preenchimento))
            no.setPen(QPen(contorno, 2.5))
            no.setZValue(5)
            self.cena.addItem(no)
            rotulo = QGraphicsSimpleTextItem(identificador)
            rotulo.setBrush(QBrush(QColor("#17212d")))
            rotulo.setFont(self._fonte(12, True))
            caixa = rotulo.boundingRect()
            rotulo.setPos(x - caixa.width() / 2, y - caixa.height() / 2)
            rotulo.setZValue(6)
            self.cena.addItem(rotulo)

        self.vista.fitInView(self.cena.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def _adicionar_fundo_floresta(self, grafo: Grafo) -> None:
        if len(grafo.vertices) not in (5, 18) or not grafo.cameras:
            return
        # As fotos das câmeras ficam junto ao forest.png de cada conjunto.
        # Usar a pasta da foto seleciona automaticamente images_5 ou images_18.
        arquivo = grafo.cameras[grafo.vertices[0]].foto.parent / "forest.png"
        imagem = QPixmap(str(arquivo))
        if imagem.isNull():
            return
        tamanho_cena = QSize(1000, 680)
        imagem = imagem.scaled(
            tamanho_cena,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        esquerda = max((imagem.width() - tamanho_cena.width()) // 2, 0)
        topo = max((imagem.height() - tamanho_cena.height()) // 2, 0)
        imagem = imagem.copy(esquerda, topo, tamanho_cena.width(), tamanho_cena.height())
        fundo = QGraphicsPixmapItem(imagem)
        fundo.setZValue(-10)
        self.cena.addItem(fundo)



    @staticmethod
    def _disposicao_circular(vertices: tuple[str, ...]) -> dict[str, tuple[float, float]]:
        from math import cos, pi, sin

        centro = (500, 340)
        raio_x, raio_y = 380, 260
        return {
            vertice: (
                centro[0] + raio_x * cos(2 * pi * i / len(vertices) - pi / 2),
                centro[1] + raio_y * sin(2 * pi * i / len(vertices) - pi / 2),
            )
            for i, vertice in enumerate(vertices)
        }

    @staticmethod
    def _fonte(tamanho: int, negrito: bool):
        from PySide6.QtGui import QFont

        fonte = QFont("Sans Serif", tamanho)
        fonte.setBold(negrito)
        return fonte

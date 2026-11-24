"""Tabelas detalhadas das execuções de Dijkstra e da estratégia gulosa."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..dijkstra import ResultadoDijkstra
from ..dijkstra_bitmask import ResultadoDijkstraBitmask
from ..modelo import Grafo
from ..vizinho_mais_proximo import ResultadoGuloso


class DetalhesUI(QWidget):
    voltarSolicitado = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(8)

        cabecalho = QHBoxLayout()
        titulo = QLabel("Detalhes da execução")
        titulo.setObjectName("panelTitle")
        botao_voltar = QPushButton("Voltar")
        botao_voltar.clicked.connect(self.voltarSolicitado)
        cabecalho.addWidget(titulo)
        cabecalho.addStretch(1)
        cabecalho.addWidget(botao_voltar)
        layout.addLayout(cabecalho)

        tabelas = QSplitter(Qt.Orientation.Vertical)
        self.titulo_distancias = QLabel("Tabela final de distâncias")
        self.titulo_distancias.setObjectName("panelTitle")
        self.titulo_guloso = QLabel("Caminhos utilizados pelo algoritmo guloso")
        self.titulo_guloso.setObjectName("panelTitle")
        self.tabela_distancias = self._criar_tabela(
            ("Origem", "Destino", "Distância mínima", "Predecessor", "Caminho reconstruído")
        )
        self.tabela_guloso = self._criar_tabela(
            (
                "Origem",
                "Destino escolhido",
                "Distância mínima",
                "Câmeras candidatas (distância)",
                "Câmera escolhida",
                "Caminho físico",
                "Distância acumulada",
            )
        )
        tabelas.addWidget(
            self._secao(self.titulo_distancias, self.tabela_distancias)
        )
        tabelas.addWidget(
            self._secao(self.titulo_guloso, self.tabela_guloso)
        )
        tabelas.setStretchFactor(0, 1)
        tabelas.setStretchFactor(1, 1)
        layout.addWidget(tabelas, 1)

    @staticmethod
    def _secao(titulo: QLabel, tabela: QTableWidget) -> QWidget:
        secao = QWidget()
        layout = QVBoxLayout(secao)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(titulo)
        layout.addWidget(tabela, 1)
        return secao

    @staticmethod
    def _criar_tabela(colunas: tuple[str, ...]) -> QTableWidget:
        tabela = QTableWidget(0, len(colunas))
        tabela.setHorizontalHeaderLabels(colunas)
        tabela.verticalHeader().setVisible(False)
        # Evita as cores AlternateBase do tema do sistema, que podem esconder
        # os itens quando a janela aplica um tema global.
        tabela.setAlternatingRowColors(False)
        tabela.setStyleSheet(
            "QTableWidget { background-color: #ffffff; color: #243447; "
            "gridline-color: #d8e0e8; selection-background-color: #cfe1f2; "
            "selection-color: #17212d; }"
        )
        tabela.setWordWrap(False)
        tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        tabela.horizontalHeader().setStretchLastSection(False)
        tabela.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        tabela.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        tabela.setMinimumHeight(150)
        return tabela

    @staticmethod
    def _adicionar_linha(tabela: QTableWidget, valores: tuple[str, ...]) -> None:
        linha = tabela.rowCount()
        tabela.insertRow(linha)
        for coluna, texto in enumerate(valores):
            item = QTableWidgetItem(texto)
            cor_fundo = "#ffffff" if linha % 2 == 0 else "#f1f5f8"
            item.setBackground(QColor(cor_fundo))
            item.setForeground(QColor("#243447"))
            item.setToolTip(texto)
            if coluna and ("distância" in tabela.horizontalHeaderItem(coluna).text().lower()
                           or "acumulada" in tabela.horizontalHeaderItem(coluna).text().lower()):
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tabela.setItem(linha, coluna, item)

    def atualizar_vizinho_mais_proximo(
        self,
        grafo: Grafo,
        resultados_dijkstra: dict[str, ResultadoDijkstra],
        resultado_guloso: ResultadoGuloso,
    ) -> None:
        self.titulo_distancias.setText("Tabela final de distâncias do Dijkstra")
        self.titulo_guloso.setText("Caminhos utilizados pelo algoritmo guloso")
        self._configurar_colunas(
            self.tabela_distancias,
            ("Origem", "Destino", "Distância mínima", "Predecessor", "Caminho reconstruído"),
            (60, 60, 105, 80, 270),
        )
        self._configurar_colunas(
            self.tabela_guloso,
            (
                "Origem", "Destino escolhido", "Distância mínima",
                "Câmeras candidatas (distância)", "Câmera escolhida",
                "Caminho físico", "Distância acumulada",
            ),
            (60, 105, 105, 260, 105, 270, 120),
        )

        for origem in grafo.vertices:
            resultado = resultados_dijkstra[origem]
            for destino in grafo.vertices:
                distancia = resultado.distancias[destino]
                predecessor = resultado.predecessores[destino]
                caminho = resultado.caminho_ate(destino)
                texto_distancia = f"{distancia:g}" if distancia != float("inf") else "∞"
                self._adicionar_linha(
                    self.tabela_distancias,
                    (
                        origem,
                        destino,
                        texto_distancia,
                        predecessor or "—",
                        " → ".join(caminho) if caminho else "Sem caminho",
                    ),
                )

        acumulada = 0.0
        for indice, (origem, destino, distancia) in enumerate(resultado_guloso.passos):
            acumulada += distancia
            caminho_fisico = resultados_dijkstra[origem].caminho_ate(destino)
            candidatos = (
                resultado_guloso.candidatos_por_passo[indice]
                if indice < len(resultado_guloso.candidatos_por_passo)
                else ()
            )
            texto_candidatos = (
                " · ".join(f"{camera} ({custo:g})" for camera, custo in candidatos)
                if candidatos
                else "Fechamento do ciclo"
            )
            self._adicionar_linha(
                self.tabela_guloso,
                (
                    origem,
                    destino,
                    f"{distancia:g}",
                    texto_candidatos,
                    destino,
                    " → ".join(caminho_fisico) if caminho_fisico else "Sem caminho",
                    f"{acumulada:g}",
                ),
            )

    def atualizar_dijkstra_bitmask(self, resultado: ResultadoDijkstraBitmask) -> None:
        self.titulo_distancias.setText("Estados processados por quantidade de vértices visitados")
        self.titulo_guloso.setText("Transições do ciclo ótimo com bitmask")
        self._configurar_colunas(
            self.tabela_distancias,
            (
                "Vértices visitados",
                "Estados processados",
                "Arestas examinadas",
                "Estados atualizados",
            ),
            (130, 135, 135, 135),
        )
        self._configurar_colunas(
            self.tabela_guloso,
            (
                "Etapa",
                "Origem",
                "Destino",
                "Custo da aresta",
                "Vértices já visitados",
                "Máscara",
                "Custo acumulado",
            ),
            (55, 65, 65, 105, 220, 105, 115),
        )
        for camada in resultado.camadas:
            self._adicionar_linha(
                self.tabela_distancias,
                (
                    str(camada.vertices_visitados),
                    f"{camada.estados_processados:,}".replace(",", "."),
                    f"{camada.arestas_examinadas:,}".replace(",", "."),
                    f"{camada.atualizacoes:,}".replace(",", "."),
                ),
            )
        tamanho_mascara = max(
            (passo.mascara_visitados.bit_length() for passo in resultado.passos),
            default=1,
        )
        for indice, passo in enumerate(resultado.passos, start=1):
            self._adicionar_linha(
                self.tabela_guloso,
                (
                    str(indice),
                    passo.origem,
                    passo.destino,
                    f"{passo.custo_aresta:g}",
                    ", ".join(passo.vertices_visitados),
                    f"0b{passo.mascara_visitados:0{tamanho_mascara}b}",
                    f"{passo.custo_acumulado:g}",
                ),
            )

    @staticmethod
    def _configurar_colunas(
        tabela: QTableWidget,
        colunas: tuple[str, ...],
        larguras: tuple[int, ...],
    ) -> None:
        tabela.setRowCount(0)
        tabela.setColumnCount(len(colunas))
        tabela.setHorizontalHeaderLabels(colunas)
        for indice, largura in enumerate(larguras):
            tabela.setColumnWidth(indice, largura)

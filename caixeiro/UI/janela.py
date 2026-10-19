"""Janela principal e coordenação da simulação."""

from time import perf_counter

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QVBoxLayout, QWidget

from ..dados import GRAFO_5
from ..dados_grafo_18 import GRAFO_18
from ..dijkstra import ResultadoDijkstra
from ..forca_bruta import resolver
from ..integracao import caminhos_minimos, matriz_distancias
from ..vizinho_mais_proximo import vizinho_mais_proximo
from .camera_ui import CameraUI
from .controles import ControlesUI
from .grafo_ui import GrafoUI
from .metricas import MetricasUI


class JanelaPrincipal(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Inspeção de câmeras de trilha")
        self.setMinimumSize(1180, 760)
        self.resize(1460, 900)

        self.grafo = GRAFO_5
        self.algoritmo = ""
        self.rota: tuple[str, ...] = ()
        self.custos_por_etapa: list[float] = []
        self.caminhos_por_etapa: list[tuple[str, ...]] = []
        self.resultados_dijkstra: dict[str, ResultadoDijkstra] = {}
        self.indice_rota = 0
        self.custo_acumulado = 0.0
        self.cameras_visitadas: set[str] = set()
        self.executando = False
        self.tempo_calculo_segundos = 0.0

        self.grafo_ui = GrafoUI()
        self.camera_ui = CameraUI()
        self.metricas_ui = MetricasUI()
        self.controles = ControlesUI()
        self._montar_layout()

        self.controles.grafoAlterado.connect(self._trocar_grafo)
        self.controles.iniciarSolicitado.connect(self._iniciar)
        self.controles.pausarSolicitado.connect(self._pausar)
        self.controles.avancarSolicitado.connect(self._avancar)
        self.controles.reiniciarSolicitado.connect(self._reiniciar)

        self.timer = QTimer(self)
        self.timer.setInterval(1500)
        self.timer.timeout.connect(self._tick)
        self._preparar_rota()
        self._reiniciar()

    def _montar_layout(self) -> None:
        central = QWidget()
        raiz = QHBoxLayout(central)
        raiz.setContentsMargins(16, 16, 16, 12)
        raiz.setSpacing(12)

        painel_grafo = self._painel("Mapa da floresta", self.grafo_ui)
        painel_lateral = QFrame()
        painel_lateral.setObjectName("panel")
        lateral = QVBoxLayout(painel_lateral)
        lateral.setContentsMargins(10, 10, 10, 10)
        lateral.setSpacing(12)
        lateral.addWidget(self._painel("Imagem da câmera", self.camera_ui), 3)
        paineis_inferiores = QHBoxLayout()
        paineis_inferiores.setSpacing(10)
        menu = QWidget()
        menu_layout = QVBoxLayout(menu)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(8)
        menu_layout.addWidget(self.metricas_ui, 3)
        menu_layout.addWidget(self.controles, 2)
        paineis_inferiores.addWidget(self._painel("Menu", menu), 1)
        paineis_inferiores.addWidget(
            self._painel("Calculos", QWidget()), 1
        )
        lateral.addLayout(paineis_inferiores, 2)
        raiz.addWidget(painel_grafo, 7)
        raiz.addWidget(painel_lateral, 5)
        self.setCentralWidget(central)
        self.setStyleSheet(
            """
            QMainWindow, QWidget { background: #eef2f6; color: #243447; font-size: 13px; }
            QFrame#panel { background: white; border: 1px solid #d8e0e8; border-radius: 10px; }
            QLabel#panelTitle { color: #23364a; font-size: 15px; font-weight: 700; }
            QFrame#metricCard { background: #f7f9fc; border: 1px solid #e3e9ef; border-radius: 6px; }
            QLabel#metricLabel { color: #617386; font-size: 11px; }
            QLabel#metricValue { color: #243447; font-size: 12px; font-weight: 600; }
            QLabel#cameraImage { background: #f7f9fc; border: 1px solid #e3e9ef; border-radius: 8px; }
            QPushButton { background: #285f8f; color: white; border: 0; border-radius: 6px; padding: 9px 14px; }
            QPushButton:hover { background: #1f4d76; }
            QPushButton:disabled { background: #b9c4ce; color: #edf0f3; }
            QComboBox { background: white; border: 1px solid #c9d3dd; border-radius: 5px; padding: 7px; }
            """
        )

    @staticmethod
    def _painel(titulo: str, conteudo: QWidget) -> QFrame:
        painel = QFrame()
        painel.setObjectName("panel")
        layout = QVBoxLayout(painel)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(8)
        rotulo = QLabel(titulo)
        rotulo.setObjectName("panelTitle")
        layout.addWidget(rotulo)
        layout.addWidget(conteudo, 1)
        return painel

    def _trocar_grafo(self, identificador: str) -> None:
        self.timer.stop()
        self.executando = False
        self.grafo = GRAFO_5 if identificador == "5" else GRAFO_18
        self._preparar_rota()
        self._reiniciar()

    def _preparar_rota(self) -> None:
        inicio_calculo = perf_counter()
        self.resultados_dijkstra = {}
        if len(self.grafo.vertices) == 5:
            resultado = resolver(self.grafo, origem=self.grafo.vertices[0])
            if not resultado.rotas_otimas:
                self.rota = ()
                self.tempo_calculo_segundos = perf_counter() - inicio_calculo
                self.statusBar().showMessage("Não foi encontrada uma rota fechada para este grafo.")
                return
            self.algoritmo = "Força bruta — solução ótima"
            self.rota = resultado.rotas_otimas[0]
            self.caminhos_por_etapa = [(a, b) for a, b in zip(self.rota, self.rota[1:])]
            self.custos_por_etapa = [self.grafo.peso(a, b) or 0 for a, b in zip(self.rota, self.rota[1:])]
        else:
            self.resultados_dijkstra = caminhos_minimos(self.grafo)
            matriz = matriz_distancias(self.grafo, self.resultados_dijkstra)
            resultado = vizinho_mais_proximo(self.grafo.vertices, matriz, origem=self.grafo.vertices[0])
            if resultado.rota is None:
                self.rota = ()
                self.tempo_calculo_segundos = perf_counter() - inicio_calculo
                self.statusBar().showMessage("Não foi possível construir uma rota completa.")
                return
            self.algoritmo = "Dijkstra + vizinho mais próximo"
            self.rota = resultado.rota
            self.custos_por_etapa = [custo for _, _, custo in resultado.passos]
            self.caminhos_por_etapa = []
            for atual, proximo in zip(self.rota, self.rota[1:]):
                caminho = self.resultados_dijkstra[atual].caminho_ate(proximo)
                self.caminhos_por_etapa.append(caminho or ())
        self.tempo_calculo_segundos = perf_counter() - inicio_calculo
        self.statusBar().showMessage("Pronto para iniciar a inspeção.")

    def _iniciar(self) -> None:
        if not self.rota:
            return
        if self.indice_rota >= len(self.rota) - 1:
            self._reiniciar()
        self.executando = True
        self.timer.start()
        self._atualizar_interface()

    def _pausar(self) -> None:
        self.executando = False
        self.timer.stop()
        self._atualizar_interface()

    def _avancar(self) -> None:
        self.executando = False
        self._avancar_uma_etapa()

    def _avancar_uma_etapa(self) -> None:
        if not self.rota or self.indice_rota >= len(self.rota) - 1:
            self.executando = False
            self.timer.stop()
            self._atualizar_interface()
            return
        etapa = self.indice_rota
        self.indice_rota += 1
        self.custo_acumulado += self.custos_por_etapa[etapa]
        camera = self.rota[self.indice_rota]
        if camera != self.rota[0]:
            self.cameras_visitadas.add(camera)
        if self.indice_rota == len(self.rota) - 1:
            self.executando = False
            self.timer.stop()
            self.statusBar().showMessage("Inspeção concluída; retorno à câmera de origem realizado.")
        self._atualizar_interface()

    def _reiniciar(self) -> None:
        self.executando = False
        self.timer.stop()
        self.indice_rota = 0
        self.custo_acumulado = 0.0
        self.cameras_visitadas = {self.rota[0]} if self.rota else set()
        self._atualizar_interface()

    def _tick(self) -> None:
        if self.executando:
            self._avancar_uma_etapa()

    def _atualizar_interface(self) -> None:
        rota_disponivel = bool(self.rota)
        camera_atual = self.rota[self.indice_rota] if rota_disponivel else None
        arestas_percorridas: set[frozenset[str]] = set()
        arestas_proximas: set[frozenset[str]] = set()
        if rota_disponivel:
            for caminho in self.caminhos_por_etapa[:self.indice_rota]:
                arestas_percorridas.update(frozenset((a, b)) for a, b in zip(caminho, caminho[1:]))
            if self.indice_rota < len(self.caminhos_por_etapa):
                caminho = self.caminhos_por_etapa[self.indice_rota]
                arestas_proximas.update(frozenset((a, b)) for a, b in zip(caminho, caminho[1:]))

        self.grafo_ui.atualizar(
            self.grafo,
            arestas_percorridas=arestas_percorridas,
            arestas_proximas=arestas_proximas,
            cameras_visitadas=self.cameras_visitadas,
            camera_atual=camera_atual,
        )
        camera = self.grafo.cameras.get(camera_atual) if camera_atual else None
        self.camera_ui.mostrar_camera(camera)
        self._atualizar_metricas()
        concluida = rota_disponivel and self.indice_rota >= len(self.rota) - 1
        self.controles.definir_estado(
            executando=self.executando,
            concluida=concluida,
        )

    def _atualizar_metricas(self) -> None:
        self.metricas_ui.atualizar(
            algoritmo=self.algoritmo or "—",
            custo=self.custo_acumulado,
            unidade=self.grafo.unidade,
            inspecionadas=len(self.cameras_visitadas),
            total=len(self.grafo.vertices),
            tempo_calculo_segundos=self.tempo_calculo_segundos,
        )

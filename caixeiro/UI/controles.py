"""Barra de controles para executar a inspeção passo a passo."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QGridLayout, QLabel, QPushButton, QWidget


class ControlesUI(QWidget):
    grafoAlterado = Signal(str)
    iniciarSolicitado = Signal()
    pausarSolicitado = Signal()
    avancarSolicitado = Signal()
    reiniciarSolicitado = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.seletor = QComboBox()
        self.seletor.addItem("Grafo de 5 pontos", "5")
        self.seletor.addItem("Grafo de 18 pontos", "18")
        self.iniciar = QPushButton("Iniciar")
        self.pausar = QPushButton("Pausar")
        self.avancar = QPushButton("Avançar")
        self.reiniciar = QPushButton("Reiniciar")
        self.pausar.setEnabled(False)
        self.avancar.setEnabled(False)
        self.reiniciar.setEnabled(False)

        layout = QGridLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(8)
        layout.addWidget(QLabel("Instância"), 0, 0, 1, 2)
        layout.addWidget(self.seletor, 1, 0, 1, 2)
        layout.addWidget(self.iniciar, 2, 0)
        layout.addWidget(self.pausar, 2, 1)
        layout.addWidget(self.avancar, 3, 0)
        layout.addWidget(self.reiniciar, 3, 1)
        self.seletor.setMinimumWidth(0)
        for botao in (self.iniciar, self.pausar, self.avancar, self.reiniciar):
            botao.setMinimumWidth(0)

        self.seletor.currentIndexChanged.connect(self._notificar_grafo)
        self.iniciar.clicked.connect(self.iniciarSolicitado)
        self.pausar.clicked.connect(self.pausarSolicitado)
        self.avancar.clicked.connect(self.avancarSolicitado)
        self.reiniciar.clicked.connect(self.reiniciarSolicitado)

    def _notificar_grafo(self) -> None:
        self.grafoAlterado.emit(str(self.seletor.currentData()))

    def definir_estado(self, executando: bool, concluida: bool) -> None:
        self.iniciar.setEnabled(not executando and not concluida)
        self.pausar.setEnabled(executando)
        self.avancar.setEnabled(not concluida and not executando)
        self.reiniciar.setEnabled(True)

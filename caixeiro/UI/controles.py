"""Barra de controles para executar a inspeção passo a passo."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QInputDialog,
    QWidget,
)


class ControlesUI(QWidget):
    grafoAlterado = Signal(str)
    iniciarSolicitado = Signal()
    pausarSolicitado = Signal()
    avancarSolicitado = Signal()
    reiniciarSolicitado = Signal()
    intervaloAlterado = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.seletor = QComboBox()
        self.seletor.addItem("Grafo de 5 pontos", "5")
        self.seletor.addItem("Grafo de 18 pontos", "18")
        self.iniciar = QPushButton("Iniciar")
        self.pausar = QPushButton("Pausar")
        self.avancar = QPushButton("Avançar")
        self.reiniciar = QPushButton("Reiniciar")
        self.intervalo_segundos = 1.5
        self.ajustar_intervalo = QPushButton()
        self._atualizar_rotulo_intervalo()
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
        layout.addWidget(self.ajustar_intervalo, 4, 0, 1, 2)
        self.seletor.setMinimumWidth(0)
        for botao in (self.iniciar, self.pausar, self.avancar, self.reiniciar):
            botao.setMinimumWidth(0)

        self.seletor.currentIndexChanged.connect(self._notificar_grafo)
        self.iniciar.clicked.connect(self.iniciarSolicitado)
        self.pausar.clicked.connect(self.pausarSolicitado)
        self.avancar.clicked.connect(self.avancarSolicitado)
        self.reiniciar.clicked.connect(self.reiniciarSolicitado)
        self.ajustar_intervalo.clicked.connect(self._editar_intervalo)

    def _editar_intervalo(self) -> None:
        valor, aceito = QInputDialog.getDouble(
            self,
            "Intervalo entre câmeras",
            "Tempo entre visitas (segundos):",
            self.intervalo_segundos,
            0.25,
            60.0,
            2,
            step=0.25,
        )
        if not aceito:
            return
        self.intervalo_segundos = valor
        self._atualizar_rotulo_intervalo()
        self.intervaloAlterado.emit(round(valor * 1000))

    def _atualizar_rotulo_intervalo(self) -> None:
        valor = f"{self.intervalo_segundos:.2f}".rstrip("0").rstrip(".")
        self.ajustar_intervalo.setText(f"Intervalo: {valor.replace('.', ',')} s")

    def _notificar_grafo(self) -> None:
        self.grafoAlterado.emit(str(self.seletor.currentData()))

    def definir_estado(self, executando: bool, concluida: bool) -> None:
        self.iniciar.setEnabled(not executando and not concluida)
        self.pausar.setEnabled(executando)
        self.avancar.setEnabled(not concluida and not executando)
        self.reiniciar.setEnabled(True)

"""Painel de algoritmo, custo, progresso e tempo de simulação."""

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class MetricasUI(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.algoritmo = QLabel("—")
        self.custo = QLabel("0 unidades de custo")
        self.progresso = QLabel("0 / 0 câmeras")
        self.tempo = QLabel("0,000 ms")

        itens = (
            ("Algoritmo", self.algoritmo),
            ("Custo percorrido", self.custo),
            ("Progresso da inspeção", self.progresso),
            ("Tempo de cálculo", self.tempo),
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        for legenda, valor in itens:
            cartao = QFrame()
            cartao.setObjectName("metricCard")
            cartao_layout = QVBoxLayout(cartao)
            cartao_layout.setContentsMargins(9, 5, 9, 5)
            cartao_layout.setSpacing(1)
            rotulo = QLabel(legenda)
            rotulo.setObjectName("metricLabel")
            valor.setWordWrap(True)
            valor.setObjectName("metricValue")
            cartao_layout.addWidget(rotulo)
            cartao_layout.addWidget(valor)
            layout.addWidget(cartao)
        layout.addStretch(1)

    def atualizar(
        self,
        algoritmo: str,
        custo: float,
        unidade: str,
        inspecionadas: int,
        total: int,
        tempo_calculo_segundos: float,
    ) -> None:
        self.algoritmo.setText(algoritmo)
        self.custo.setText(f"{custo:g} {unidade}")
        self.progresso.setText(f"{inspecionadas} / {total} câmeras")
        tempo_ms = max(tempo_calculo_segundos, 0.0) * 1000
        self.tempo.setText(f"{tempo_ms:.3f} ms")

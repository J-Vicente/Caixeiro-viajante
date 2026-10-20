"""Resumo das métricas dos algoritmos de busca de rota."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ..forca_bruta import ResultadoForcaBruta


class SobreAlgoritmoUI(QWidget):
    detalharSolicitado = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.valores: dict[str, QLabel] = {}
        self.linhas: dict[str, tuple[QLabel, QLabel]] = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(5)

        self.aviso = QLabel()
        self.aviso.setWordWrap(True)
        self.aviso.setStyleSheet("color: #8a4b08; font-weight: 600;")
        self.aviso.hide()
        layout.addWidget(self.aviso)

        grade = QGridLayout()
        grade.setContentsMargins(0, 0, 0, 0)
        grade.setHorizontalSpacing(8)
        grade.setVerticalSpacing(4)

        campos = (
            ("Rotas avaliadas", "rotas"),
            ("Rotas válidas", "validas"),
            ("Rotas descartadas", "descartadas"),
            ("Menor custo", "custo"),
            ("Rota de menor custo", "rota"),
            ("Avaliações de arestas", "avaliacoes"),
            ("Vértices processados", "vertices"),
            ("Arestas examinadas", "arestas"),
            ("Relaxamentos com atualização", "relaxamentos"),
            ("Atualizações de distância", "atualizacoes"),
            ("Tempo de cálculo", "tempo"),
        )
        for linha, (titulo, chave) in enumerate(campos):
            nome = QLabel(titulo)
            nome.setObjectName("metricLabel")
            valor = QLabel("—")
            valor.setObjectName("metricValue")
            valor.setWordWrap(True)
            self.valores[chave] = valor
            self.linhas[chave] = (nome, valor)
            grade.addWidget(nome, linha, 0)
            grade.addWidget(valor, linha, 1)
        grade.setColumnStretch(1, 1)
        layout.addLayout(grade)

        self.botao_detalhar = QPushButton("Detalhar")
        self.botao_detalhar.clicked.connect(self.detalharSolicitado)
        self.botao_detalhar.hide()
        layout.addWidget(self.botao_detalhar)
        layout.addStretch(1)

    def limpar(self, mensagem: str = "Disponível para o grafo de 5 pontos.") -> None:
        for valor in self.valores.values():
            valor.setText("—")
        self._mostrar_campos({"rotas"})
        self.valores["rotas"].setText(mensagem)
        self.aviso.hide()
        self.botao_detalhar.hide()

    def atualizar_forca_bruta(
        self,
        resultado: ResultadoForcaBruta,
        tempo_calculo_segundos: float,
        unidade: str,
    ) -> None:
        self._mostrar_campos(
            {"rotas", "validas", "descartadas", "custo", "rota", "avaliacoes", "tempo"}
        )
        self.valores["rotas"].setText(str(resultado.ciclos_candidatos))
        self.valores["validas"].setText(str(resultado.ciclos_viaveis))
        self.valores["descartadas"].setText(str(resultado.ciclos_descartados))
        custo = (
            f"{resultado.custo_minimo:g} {unidade}"
            if resultado.custo_minimo is not None
            else "Não encontrada"
        )
        self.valores["custo"].setText(custo)
        if resultado.rotas_otimas:
            rotas = [" → ".join(rota) for rota in resultado.rotas_otimas]
            self.valores["rota"].setText("\n".join(rotas))
        else:
            self.valores["rota"].setText("Não encontrada")
        self.valores["avaliacoes"].setText(f"{resultado.avaliacoes_arestas:,}".replace(",", "."))
        tempo_ms = max(tempo_calculo_segundos, 0.0) * 1000
        self.valores["tempo"].setText(f"{tempo_ms:.3f} ms")
        self.aviso.hide()
        self.botao_detalhar.hide()

    def atualizar_vizinho_mais_proximo(
        self,
        custo: float | None,
        rota: tuple[str, ...] | None,
        unidade: str,
        vertices_processados: int,
        arestas_examinadas: int,
        relaxamentos_com_atualizacao: int,
        atualizacoes_distancia: int,
        tempo_calculo_segundos: float,
    ) -> None:
        self._mostrar_campos(
            {
                "custo", "rota", "vertices", "arestas", "relaxamentos",
                "atualizacoes", "tempo",
            }
        )
        self.valores["rotas"].setText("—")
        self.valores["validas"].setText("—")
        self.valores["descartadas"].setText("—")
        self.valores["custo"].setText(
            f"{custo:g} {unidade}" if custo is not None else "Não encontrada"
        )
        self.valores["rota"].setText(" → ".join(rota) if rota else "Não encontrada")
        self.valores["avaliacoes"].setText("—")
        self.valores["vertices"].setText(f"{vertices_processados:,}".replace(",", "."))
        self.valores["arestas"].setText(f"{arestas_examinadas:,}".replace(",", "."))
        self.valores["relaxamentos"].setText(
            f"{relaxamentos_com_atualizacao:,}".replace(",", ".")
        )
        self.valores["atualizacoes"].setText(
            f"{atualizacoes_distancia:,}".replace(",", ".")
        )
        tempo_ms = max(tempo_calculo_segundos, 0.0) * 1000
        self.valores["tempo"].setText(f"{tempo_ms:.3f} ms")
        self.aviso.setText(
            "Observação: o vizinho mais próximo é uma heurística e não garante o ótimo global."
        )
        self.aviso.show()
        self.botao_detalhar.show()

    def _mostrar_campos(self, chaves_visiveis: set[str]) -> None:
        for chave, widgets in self.linhas.items():
            for widget in widgets:
                widget.setVisible(chave in chaves_visiveis)

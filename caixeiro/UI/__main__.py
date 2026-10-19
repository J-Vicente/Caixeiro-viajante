"""Ponto de entrada da interface gráfica."""

import sys

from PySide6.QtWidgets import QApplication

from .janela import JanelaPrincipal


def main() -> None:
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

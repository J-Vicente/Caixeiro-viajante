"""Painel para exibir a fotografia da câmera atual."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PIL import Image, ImageOps

from ..modelo import Camera


class CameraUI(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._camera: Camera | None = None
        self._pixmap = QPixmap()

        self.titulo = QLabel("Registro da câmera")
        self.titulo.setObjectName("panelTitle")
        self.imagem = QLabel("Selecione uma câmera")
        self.imagem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imagem.setMinimumSize(300, 260)
        self.imagem.setObjectName("cameraImage")
        self.imagem.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.addWidget(self.titulo)
        layout.addWidget(self.imagem, 1)

    def mostrar_camera(self, camera: Camera | None) -> None:
        self._camera = camera
        if camera is None:
            self._pixmap = QPixmap()
            self.titulo.setText("Registro da câmera")
            self.imagem.setPixmap(QPixmap())
            self.imagem.setText("Nenhuma câmera selecionada")
            return

        self.titulo.setText(f"Câmera {camera.identificador}")
        try:
            with Image.open(camera.foto) as imagem:
                imagem = ImageOps.exif_transpose(imagem).convert("RGBA")
                dados = imagem.tobytes()
                qimage = QImage(
                    dados,
                    imagem.width,
                    imagem.height,
                    imagem.width * 4,
                    QImage.Format.Format_RGBA8888,
                ).copy()
            self._pixmap = QPixmap.fromImage(qimage)
        except (OSError, ValueError):
            self._pixmap = QPixmap()
        if self._pixmap.isNull():
            self.imagem.setPixmap(QPixmap())
            self.imagem.setText(f"Não foi possível carregar a imagem\n{camera.foto.name}")
        else:
            self._atualizar_tamanho()

    def resizeEvent(self, event) -> None:  # noqa: N802 - assinatura Qt
        super().resizeEvent(event)
        self._atualizar_tamanho()

    def _atualizar_tamanho(self) -> None:
        if self._camera is None or self._pixmap.isNull():
            return
        area = self.imagem.contentsRect().size()
        self.imagem.setPixmap(
            self._pixmap.scaled(
                area,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

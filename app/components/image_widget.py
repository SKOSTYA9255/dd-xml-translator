from typing import Optional

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QBrush, QPainterPath
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from module.tools.types.general import StrPath

class ImageWidget(QWidget):
    def __init__(self, image: StrPath, parent: Optional[QWidget]=None):
        try:
            super().__init__(parent)
            self.image = QPixmap(image)
            self.setMinimumHeight(350)
            self.setMaximumHeight(self.image.height())
        except Exception:
            self.deleteLater()
            raise

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.RenderHint.SmoothPixmapTransform | QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.FillRule.WindingFill)
        w, h = self.width(), 200
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h - 50, 50, 50))
        path.addRect(QRectF(w - 50, 0, 50, 50))
        path.addRect(QRectF(w - 50, h - 50, 50, 50))
        path = path.simplified()

        # Calculate the required height for maintaining image aspect ratio
        image_height = self.width() * self.image.height() // self.image.width()

        # draw banner image with aspect ratio preservation
        pixmap = self.image.scaled(
            self.width(), image_height,
            aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
            transformMode=Qt.TransformationMode.SmoothTransformation
        )
        path.addRect(QRectF(0, h, w, self.height() - h))
        painter.fillPath(path, QBrush(pixmap))
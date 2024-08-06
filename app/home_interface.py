import os
from typing import Any, Optional

from qfluentwidgets import ScrollArea, FluentIcon
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QBrush, QPainterPath
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QGraphicsDropShadowEffect

from app.common.signal_bus import signalBus
from app.common.stylesheet import StyleSheet
from app.components.infobar_test import InfoBar, InfoBarPosition
from app.components.link_card import LinkCardView

from module.config.internal.app_args import AppArgs
from module.config.internal.names import ModuleNames
from module.config.app_config import AppConfig


class BannerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.isBackgroundActive = bool(AppConfig().getValue("appBackground"))
        self.showBanner = not self.isBackgroundActive or int(AppConfig().getValue("backgroundOpacity")) == 0

        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel(f'{ModuleNames.app_name}\nv{AppArgs.app_version}', self)
        self.galleryLabel.setStyleSheet("color: white;font-size: 30px; font-weight: 600;")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20.0)
        shadow.setColor(Qt.GlobalColor.black)
        shadow.setOffset(1.2, 1.2)

        self.galleryLabel.setGraphicsEffect(shadow)
        self.galleryLabel.setObjectName('galleryLabel')

        self.banner = QPixmap(f"{AppArgs.asset_images_dir}{os.sep}banner.jpg")

        self.linkCardView = LinkCardView(self)
        self.linkCardView.setContentsMargins(0, 0, 0, 36)

        # Create a horizontal layout for the linkCardView with bottom alignment and margin
        linkCardLayout = QHBoxLayout()
        linkCardLayout.addWidget(self.linkCardView)
        linkCardLayout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.setMinimumHeight(350)
        self.setMaximumHeight(self.banner.height())

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addLayout(linkCardLayout)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.linkCardView.addCard(
            FluentIcon.GITHUB,
            self.tr('GitHub repo'),
            self.tr(''),
            AppArgs.link_github,
        )
        self.__connectSignalToSlot()

    def __connectSignalToSlot(self) -> None:
        signalBus.configUpdated.connect(self.__onAppConfigUpdated)

    def __onAppConfigUpdated(self, configkey: str, valuePack: tuple[Any,]) -> None:
        value = valuePack[0]
        if configkey == "appBackground":
            self.showBanner = not bool(value)
            self.isBackgroundActive = bool(value)
        elif configkey == "backgroundOpacity":
            self.showBanner = not self.isBackgroundActive or int(value) == 0

    def paintEvent(self, e):
        super().paintEvent(e)
        if self.showBanner:
            painter = QPainter(self)
            painter.setRenderHints(QPainter.RenderHint.SmoothPixmapTransform | QPainter.RenderHint.Antialiasing)
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
            image_height = self.width() * self.banner.height() // self.banner.width()

            # draw banner image with aspect ratio preservation
            pixmap = self.banner.scaled(
                self.width(), image_height,
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation
            )
            path.addRect(QRectF(0, h, w, self.height() - h))
            painter.fillPath(path, QBrush(pixmap))


class HomeInterface(ScrollArea):
    def __init__(self, parent: Optional[QWidget]=None):
        super().__init__(parent)
        self.banner = BannerWidget(self)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__initWidget()
        self.__checkConfig()

    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner, stretch=2)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.__setQss()

    def __setQss(self):
        self.view.setObjectName('view')
        self.setObjectName('homeInterface')
        StyleSheet.HOME_INTERFACE.apply(self)

    def __checkConfig(self):
        from module.config.app_config import AppConfig

        if AppConfig().getFailureStatus():
            InfoBar.warning(
                title=self.tr("Using internal config"),
                content=self.tr("Setting changes may not persist"),
                isClosable=False,
                duration=20000,
                position=InfoBarPosition.TOP,
                parent=self
            )
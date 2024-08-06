from typing import Any
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPaintEvent
from PyQt6.QtWidgets import (QApplication, QGraphicsBlurEffect, QGraphicsItem,
                             QGraphicsPixmapItem, QGraphicsScene, QGraphicsView)
from PyQt6.QtCore import QSize, Qt
from contextlib import redirect_stdout

with redirect_stdout(None):
    from qfluentwidgets import (NavigationItemPosition, MSFluentWindow, SplashScreen,
                                NavigationBarPushButton, toggleTheme, setTheme, theme,
                                setThemeColor, Theme)
    from qfluentwidgets import FluentIcon as FIF
import os
import traceback

from app.common.signal_bus import signalBus
from app.common.stylesheet import StyleSheet
from app.components.infobar_test import InfoBar, InfoBarPosition

from module.config.internal.app_args import AppArgs
from module.config.internal.names import ModuleNames
from module.config.app_config import AppConfig
from module.logger import logger


class MainWindow(MSFluentWindow):
    _logger = logger
    _app_config = AppConfig()

    def __init__(self):
        super().__init__()
        val = self._app_config.getValue("appBackground")
        self.background = QPixmap(val) if val else None # type: QPixmap | None
        self.backgroundOpacity = self._app_config.getValue("backgroundOpacity", 0.0)
        self.backgroundBlurRadius = self._app_config.getValue("backgroundBlur", 0.0)
        self.errorLog = []

        self.setMicaEffectEnabled(False)
        setTheme(Theme.AUTO, lazy=True) # Set initial theme

        try:
            self.__initWindow()
            self.__connectSignalToSlot()
            try:
                from app.home_interface import HomeInterface
                self.homeInterface = HomeInterface(self)
            except Exception:
                self.errorLog.append(traceback.format_exc(limit=AppArgs.traceback_limit))
                self.homeInterface = None

            try:
                from app.xml_interface import XMLInterface
                self.processInterface = XMLInterface(self)
            except Exception:
                self.errorLog.append(traceback.format_exc(limit=AppArgs.traceback_limit))
                self.processInterface = None

            try:
                from app.settings_interface import SettingsInterface
                self.settingsInterface = SettingsInterface(self)
            except Exception:
                self.errorLog.append(traceback.format_exc(limit=AppArgs.traceback_limit))
                self.settingsInterface = None

            self.__initNavigation()
        except Exception:
            self.errorLog.append(traceback.format_exc(limit=AppArgs.traceback_limit))

        StyleSheet.MAIN_WINDOW.apply(self)
        self.splashScreen.finish()

        if len(self.errorLog) > 0:
            self._displayErrors()
        else:
            self._logger.info("Application startup successful!")

    def __initNavigation(self):
        if self.homeInterface:
            self.addSubInterface(self.homeInterface, FIF.HOME, self.tr("Home"))
        if self.processInterface:
            self.addSubInterface(self.processInterface, FIF.IOT, self.tr("Process"))

        self.navigationInterface.addWidget(
            'themeButton',
            NavigationBarPushButton(FIF.CONSTRACT, "", isSelectable=False),
            self.toggleTheme,
            NavigationItemPosition.BOTTOM)

        if self.settingsInterface:
            self.addSubInterface(self.settingsInterface, FIF.SETTING, self.tr('Settings'), position=NavigationItemPosition.BOTTOM)

    def __initWindow(self):
        #self.titleBar.maxBtn.setHidden(True)
        #self.titleBar.maxBtn.setDisabled(True)
        #self.titleBar.setDoubleClickEnabled(False)
        #self.setResizeEnabled(False)
        self.setMinimumSize(960, 700)
        self.resize(1280, 720)
        self.setWindowIcon(QIcon(f"{AppArgs.logo_dir}{os.sep}logo.png"))
        self.setWindowTitle(f"{ModuleNames.app_name} {AppArgs.app_version}")

        # Create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(128, 128))
        self.splashScreen.raise_()

        # Calculate window position
        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        # Setup rendering for background image
        self.scene = QGraphicsScene()
        self.view = QGraphicsView()

        self.show()
        QApplication.processEvents()

    def __connectSignalToSlot(self) -> None:
        signalBus.configUpdated.connect(self.__onAppConfigUpdated)
        signalBus.configValidationError.connect(lambda configname, title, content: self.__onConfigValidationFailed(title, content))
        signalBus.configStateChange.connect(self.__onConfigStateChanged)

    def __onAppConfigUpdated(self, configkey: str, valuePack: tuple[Any,]) -> None:
        value = valuePack[0]
        if configkey == "appBackground":
            self.background = QPixmap(value) if value else None
            self.update()
        elif configkey == "appTheme":
            self.__onThemeChanged(value)
        elif configkey == "appColor":
            setThemeColor(value, lazy=True)
        elif configkey == "backgroundOpacity":
            self.backgroundOpacity = value / 100
            self.update()
        elif configkey == "backgroundBlur":
            self.backgroundBlurRadius = float(value)
            self.update()

    def __onConfigValidationFailed(self, title: str, content: str):
        InfoBar.warning(
            title=self.tr(title),
            content=self.tr(content),
            orient=Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal,
            isClosable=False,
            duration=5000,
            position=InfoBarPosition.TOP,
            parent=self
        )

    def __onConfigStateChanged(self, state: bool, title: str, content: str):
        if state:
            InfoBar.success(
                title=self.tr(title),
                content=self.tr(content),
                orient=Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal,
                isClosable=False,
                duration=5000,
                position=InfoBarPosition.TOP,
                parent=self
            )
        else:
            InfoBar.error(
                title=self.tr(title),
                content=self.tr(content),
                orient=Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal,
                isClosable=False,
                duration=5000,
                position=InfoBarPosition.TOP,
                parent=self
            )

    def __onThemeChanged(self, value: str):
        if value == "Light":
            setTheme(Theme.LIGHT, lazy=True)
        elif value == "Dark":
            setTheme(Theme.DARK, lazy=True)
        else:
            setTheme(Theme.AUTO, lazy=True)

    def _displayErrors(self):
        for error in self.errorLog:
            self._logger.critical("Encountered a critical error during startup\n" + error)
            InfoBar.error(
                title=self.tr("Critical Error!"),
                content=error,
                isClosable=True,
                duration=-1,
                position=InfoBarPosition.TOP,
                parent=self
            )

    def toggleTheme(self):
        toggleTheme(lazy=True)
        signalBus.updateConfigSettings.emit("appTheme", (theme().value,))

    def paintEvent(self, e: QPaintEvent):
        super().paintEvent(e)
        if self.background:
            # Only set scene once!
            if not self.view.scene():
                self.view.setScene(self.scene)

            # Setup painter
            painter = QPainter(self)
            painter.setRenderHints(QPainter.RenderHint.SmoothPixmapTransform | QPainter.RenderHint.Antialiasing | QPainter.RenderHint.LosslessImageRendering)
            painter.setPen(Qt.PenStyle.NoPen)

            # Draw background image with aspect ratio preservation
            pixmap = self.background.scaled(
                self.width(), self.height(),
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                transformMode=Qt.TransformationMode.SmoothTransformation
            )

            # Get new pixmap rect
            rect = pixmap.rect().toRectF()

            # Add blur effect
            blur = QGraphicsBlurEffect()
            blur.setBlurRadius(self.backgroundBlurRadius)
            blur.setBlurHints(QGraphicsBlurEffect.BlurHint.QualityHint)

            # Create pixmap for the graphics scene
            pixmapItem = QGraphicsPixmapItem(pixmap)
            pixmapItem.setGraphicsEffect(blur)
            pixmapItem.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresParentOpacity)
            pixmapItem.setOpacity(self.backgroundOpacity)

            # Add image with effects to the scene and render image
            self.scene.clear()
            self.scene.addItem(pixmapItem)
            self.view.render(painter, rect, rect.toRect())
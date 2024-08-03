import traceback
import os
from typing import Optional

from qfluentwidgets import ScrollArea, qrouter, PopUpAniStackedWidget
from PyQt6.QtCore import Qt, QEasingCurve
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from app.common.stylesheet import StyleSheet
from app.components.infobar_test import InfoBar, InfoBarPosition
from app.components.sample_card import SampleCardView
from app.settings_interface_app import SettingsInterface_App

from module.config.internal.app_args import AppArgs
from module.config.internal.names import ModuleNames
from module.logger import logger


class SettingsInterface(ScrollArea):
    _logger = logger

    def __init__(self, parent: Optional[QWidget]=None):
        try:
            super().__init__(parent)
            self.view = QWidget(self)
            self.vBoxLayout = QVBoxLayout(self.view)
            self.stackedWidget = PopUpAniStackedWidget()

            try:
                self.settingInterface_App = SettingsInterface_App()
            except Exception:
                self._logger.error(f"Could not load {ModuleNames.app_name} settings panel\n"
                                    + traceback.format_exc(limit=AppArgs.traceback_limit))
                self.settingInterface_App = None

            self.__initWidget()
        except Exception:
            self.deleteLater()
            raise

    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.__setQss()
        self.__initSampleCards() # Must be created before layout
        self.__initLayout()

    def __setQss(self):
        self.setObjectName("settingInterface")
        self.view.setObjectName("view")
        StyleSheet.SETTINGS_INTERFACE.apply(self)

    def __initLayout(self):
        self.vBoxLayout.addWidget(self.sampleCardView)
        self.vBoxLayout.addWidget(self.stackedWidget, stretch=1)
        self.vBoxLayout.setSpacing(20)
        self.stackedWidget.setHidden(True)

    def __initSampleCards(self):
        self.sampleCardView = SampleCardView()
        self.addSampleCard(
            icon=f"{AppArgs.logo_dir}{os.sep}logo-sq.ico",
            title=ModuleNames.app_name,
            widget=self.settingInterface_App,
        )

    def __onCurrentIndexChanged(self, index: int):
        widget = self.stackedWidget.widget(index)
        if widget:
            qrouter.push(self.stackedWidget, widget.objectName())
            self.stackedWidget.setCurrentWidget(widget, duration=250,
                                                easingCurve=QEasingCurve.Type.InQuad
                                                )
            self.stackedWidget.setHidden(False)
        else:
            InfoBar.error(
                title=self.tr("Module is not available"),
                content=self.tr(f"Please check the logs at:\n {AppArgs.log_dir.resolve()}"),
                orient=Qt.Orientation.Vertical,
                isClosable=False,
                duration=5000,
                position=InfoBarPosition.TOP,
                parent=self
            )

    def addSampleCard(self, icon, title: str, widget):
        if widget:
           self.stackedWidget.addWidget(widget)
        else:
            title += self.tr("\n❌Unavailable")
        self.sampleCardView.addSampleCard(
            icon=icon,
            title=title,
            onClick=self.__onCurrentIndexChanged
        )
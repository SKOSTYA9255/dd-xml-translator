from qfluentwidgets import ScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from typing import Optional

from app.common.stylesheet import StyleSheet
from app.components.cardstack import PivotCardStack
from app.generators.card_generator import CardGenerator

from module.config.app_config import AppConfig
from module.config.internal.names import ModuleNames
from module.config.templates.app_template import AppTemplate


class SettingsInterface_App(ScrollArea):
    def __init__(self, parent: Optional[QWidget]=None):
        try:
            super().__init__(parent=parent)
            self.config = AppConfig()
            generator = CardGenerator(
                config=self.config,
                template=AppTemplate(),
                parent=self
            )
            cardStack = PivotCardStack(
                generator=generator,
                labeltext=self.tr(f"{ModuleNames.app_name} Settings"),
                parent=self
            )
            StyleSheet.SETTINGS_SUBINTERFACE.apply(cardStack)
            self.view = QWidget(self)
            self.vGeneralLayout = QVBoxLayout(self)
            self.vGeneralLayout.addWidget(cardStack)
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

    def __setQss(self):
        self.view.setObjectName("view")
        self.setObjectName("settingsSubInterface")
        StyleSheet.SETTINGS_SUBINTERFACE.apply(self)
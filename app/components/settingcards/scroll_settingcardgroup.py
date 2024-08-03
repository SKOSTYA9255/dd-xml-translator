from qfluentwidgets import SettingCardGroup, ScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

from typing import Optional


class ScrollSettingCardGroup(ScrollArea):
    def __init__(self, title: str, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self._cards = []
        self._cardGroup = SettingCardGroup(title, self)
        self.vGeneralLayout = QVBoxLayout(self)
        self.vGeneralLayout.addWidget(self._cardGroup)
        self.__initWidget()

    def __initWidget(self) -> None:
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 10, 10)
        self.setWidget(self._cardGroup)
        self.setWidgetResizable(True)

    def addSettingCard(self, card: QWidget) -> None:
        self._cardGroup.addSettingCard(card)
        self._cards.append(card)

    def getCards(self) -> list[QWidget]:
        return self._cards

    def getTitleLabel(self) -> QLabel:
        return self._cardGroup.titleLabel
from qfluentwidgets import IconWidget, FluentIconBase, FlowLayout, CardWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect

from typing import Callable, Optional, Union

from app.common.stylesheet import StyleSheet


class SampleCard(CardWidget):
    sampleCardClicked = pyqtSignal(int) # index

    def __init__(self, icon: Union[str, QIcon, FluentIconBase],
                 title: str, index: int, onClick: Optional[Callable], parent: Optional[QWidget]=None) -> None:
        super().__init__(parent=parent)
        self.index = index
        if onClick:
            self.sampleCardClicked.connect(onClick)

        self.iconWidget = IconWidget(icon, self)
        self.iconOpacityEffect = QGraphicsOpacityEffect(self)
        self.iconOpacityEffect.setOpacity(1)  # Set the initial semi-transparency
        self.iconWidget.setGraphicsEffect(self.iconOpacityEffect)

        self.titleLabel = QLabel(title, self)
        self.titleLabel.setStyleSheet("font-size: 16px; font-weight: 500;")
        self.titleOpacityEffect = QGraphicsOpacityEffect(self)
        self.titleOpacityEffect.setOpacity(1)  # Set the initial semi-transparency
        self.titleLabel.setGraphicsEffect(self.titleOpacityEffect)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hBoxLayout = QVBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        # Define sample card size
        w, h = 130, 160 # Initial size
        if self.titleLabel.fontMetrics().boundingRect(self.titleLabel.text()).width() >= w:
            self.titleLabel.setWordWrap(True)
            h += self.titleLabel.rect().height() - 15
        h += title.count("\n") * 15
        self.setFixedSize(w, h)
        self.iconWidget.setFixedSize(110, 110)

        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.addWidget(self.iconWidget, alignment=Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.titleLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addStretch(1)

        self.titleLabel.setObjectName('titleLabel')

    def mouseReleaseEvent(self, event) -> None:
        super().mouseReleaseEvent(event)
        self.sampleCardClicked.emit(self.index)

    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        self.iconOpacityEffect.setOpacity(0.75)
        self.titleOpacityEffect.setOpacity(0.75)
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # Set the mouse pointer to hand shape

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        self.iconOpacityEffect.setOpacity(1)
        self.titleOpacityEffect.setOpacity(1)
        self.setCursor(Qt.CursorShape.ArrowCursor)  # Restore the default shape of the mouse pointer


class SampleCardView(QWidget):
    def __init__(self, title: Optional[str]=None, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.indexCounter = 0
        self.titleLabel = QLabel(title, self) if title else None
        self.vBoxLayout = QVBoxLayout(self)
        self.flowLayout = FlowLayout()

        self.vBoxLayout.setContentsMargins(20, 0, 20, 0)
        self.vBoxLayout.setSpacing(10)

        self.flowLayout.setContentsMargins(0, 0, 0, 0)
        self.flowLayout.setHorizontalSpacing(12)
        self.flowLayout.setVerticalSpacing(12)

        if self.titleLabel:
            self.vBoxLayout.addWidget(self.titleLabel)
            self.titleLabel.setObjectName('viewTitleLabel')
        self.vBoxLayout.addLayout(self.flowLayout, 1)

        StyleSheet.SAMPLE_CARD.apply(self)

    def addSampleCard(self, icon: Union[str, QIcon, FluentIconBase],
                      title: str, onClick: Optional[Callable]=None) -> None:
        card = SampleCard(icon=icon,
                          title=title,
                          index=self.indexCounter,
                          onClick=onClick,
                          parent=self)
        self.flowLayout.addWidget(card)
        self.indexCounter += 1
from abc import abstractmethod
from qfluentwidgets import (Pivot, SegmentedToolWidget, SegmentedToolItem, ScrollArea,
                            qrouter, FluentIconBase, ToolTipFilter, ToolTipPosition)
from qfluentwidgets import FluentIcon as FIF
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QStackedWidget
from PyQt6.QtGui import QIcon

from typing import Optional, TypeAlias, Union, override

from app.common.stylesheet import StyleSheet

from module.tools.types.gui_generators import AnyCardGenerator
    # InQuad                   // Straight
    # QEasingCurve.Type.InBack      // Bounce up
    # QEasingCurve.Type.InOutBack   // Bounce up & down

AnyPivot: TypeAlias = (Pivot | SegmentedToolWidget) # All QFluentWidgets' pivot classes are supported. Add as needed.

class CardStackBase(ScrollArea):
    def __init__(self, generator: AnyCardGenerator, Pivot: AnyPivot,
                 pivotAlignment: Qt.AlignmentFlag=Qt.AlignmentFlag.AlignLeft,
                 labeltext: Optional[str]=None, parent: Optional[QWidget]=None) -> None:
        try:
            super().__init__(parent)
            self._cards = generator.getCards()
            self._defaultGroup = generator.getDefaultGroup()
            self.titleLabel = QLabel(self.tr(labeltext)) if labeltext else None
            self.view = QWidget(self)
            self.vGeneralLayout = QVBoxLayout(self.view)
            self.hPivotLayout = QHBoxLayout()
            self.pivot = Pivot() # type: AnyPivot
            self.pivotAlignment = pivotAlignment
            self.stackedWidget = QStackedWidget()
        except Exception:
            self.deleteLater()
            raise

    # This method is providing the interface for connecting the card to the QStackedWidget and the Pivot object
    @abstractmethod
    def _addSubInterface(self, widget: QWidget, objectName: str, title: str, *args, **kwargs) -> None: ...

    # This method is adding the cards from the generator to the QStackedWidget using the method addSubInterface
    @abstractmethod
    def _addCards(self) -> None: ...

    def _initWidget(self) -> None:
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self._setQss()

    def _setQss(self) -> None:
        self.view.setObjectName("view")
        if self.titleLabel:
            self.titleLabel.setObjectName("titleLabel")

    def _initLayout(self) -> None:
        self._addCards()
        self.hPivotLayout.addWidget(self.pivot, alignment=self.pivotAlignment)

        if self.titleLabel:
            self.vGeneralLayout.addWidget(self.titleLabel)
        self.vGeneralLayout.addLayout(self.hPivotLayout)
        self.vGeneralLayout.addSpacing(10)
        self.vGeneralLayout.addWidget(self.stackedWidget)
        self.vGeneralLayout.setContentsMargins(0, 0, 0, 0)

        self.stackedWidget.setCurrentWidget(self._defaultGroup) # Set Group shown on app start
        self.pivot.setCurrentItem(self._defaultGroup.objectName()) # Set Group marked as selected on app start
        qrouter.setDefaultRouteKey(self.stackedWidget, self._defaultGroup.objectName()) # Set navigation history to default Group

    def _connectpyqtSignalToSlot(self) -> None:
        self.stackedWidget.currentChanged.connect(self._onCurrentIndexChanged)

    def _onCurrentIndexChanged(self, index) -> None:
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())


class PivotCardStack(CardStackBase):
    def __init__(self, generator: AnyCardGenerator, labeltext: Optional[str]=None,
                 parent: Optional[QWidget]=None) -> None:
        """Create a standard settings interface.

        It is composed of a Pivot and a QStackedWidget.
        Uses widgets created by the generator as content.

        Parameters
        ----------
        generator : AnyCardGenerator
            The widget generator which supplies the content widgets displayed.

        labeltext : str, optional
            The title of the CardStack, by default None.

        parent : QWidget, optional
            The parent widget of the CardStack, by default None.
        """
        try:
            super().__init__(
                generator=generator,
                Pivot=Pivot,
                labeltext=labeltext,
                parent=parent
            )
            self._initWidget()
            self._initLayout()
            self._connectpyqtSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    @override
    def _addCards(self) -> None:
        for group in self._cards:
            name = group.getTitleLabel().text()
            self._addSubInterface(widget=group, objectName=name, title=name)

    @override
    def _addSubInterface(self, widget: QWidget, objectName: str, title: str) -> None:
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=title,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget),
            icon=None
        )


class SegmentedPivotCardStack(CardStackBase):
    def __init__(self, generator: AnyCardGenerator, icons: dict[str, Union[str, QIcon, FluentIconBase]],
                 stylesheet: Optional[StyleSheet]=None, labeltext: Optional[str]=None,
                 parent: Optional[QWidget]=None) -> None:
        """Create a standard settings interface.

        It is composed of a Segmented Pivot, which uses the supplied icon list, and a QStackedWidget.
        Uses widgets created by the generator as content.

        Parameters
        ----------
        generator : AnyCardGenerator
            The widget generator which supplies the content widgets displayed.

        icons : list[str | QIcon | FluentIconBase]
            The icons shown in the pivot for each card category

        stylesheet : StyleSheet, optional
            Use this stylesheet for the CardStack.

        labeltext : str, optional
            The title of the CardStack, by default None.

        parent : QWidget, optional
            The parent widget of the CardStack, by default None.
        """
        try:
            super().__init__(
                generator=generator,
                Pivot=Pivot,
                pivotAlignment=Qt.AlignmentFlag.AlignHCenter,
                stylesheet=stylesheet,
                labeltext=labeltext,
                parent=parent
            )
            self.icons = icons

            self._initWidget()
            self._initLayout()
            self._connectpyqtSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    @override
    def _addCards(self) -> None:
        for group in self._cards:
            name = group.getTitleLabel().text()
            self._addSubInterface(widget=group, objectName=name, title=name, icon=self.icons.get(name.lower(), FIF.CANCEL_MEDIUM))

    @override
    def _addSubInterface(self, widget: QWidget, objectName: str, title: str,
                          icon: Union[str, QIcon, FluentIconBase]):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)

        pivotItem = SegmentedToolItem(icon)
        pivotItem.setToolTip(title)
        pivotItem.setToolTipDuration(5000)
        pivotItem.installEventFilter(
            ToolTipFilter(
                parent=pivotItem,
                showDelay=100,
                position=ToolTipPosition.TOP
            )
        )
        self.pivot.addWidget(
            routeKey=objectName,
            widget=pivotItem,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )
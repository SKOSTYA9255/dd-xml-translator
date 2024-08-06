from qfluentwidgets import PrimaryPushButton, PillPushButton, FluentIconBase, FluentStyleSheet
from qfluentwidgets.components.settings.expand_setting_card import HeaderSettingCard, SpaceWidget, ExpandBorderWidget, GroupSeparator
from qfluentwidgets import FluentIcon as FIF
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QScrollArea, QFrame, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve

from typing import Any, Optional, Union

from app.components.settings.checkbox import CheckBox_
from app.components.settings.switch import Switch

from module.tools.types.gui_settings import AnySetting

# Courtesy of qfluentwidgets (with modification)
class ExpandSettingCard(QScrollArea):
    """ Expandable setting card """

    def __init__(self, icon: Union[str, QIcon, FIF], title: str, content: str = None, parent=None):
        super().__init__(parent=parent)
        self.isExpand = False

        self.scrollWidget = QFrame(self)
        self.view = QFrame(self.scrollWidget)
        self.card = HeaderSettingCard(icon, title, content, self)

        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.viewLayout = QVBoxLayout(self.view)
        self.spaceWidget = SpaceWidget(self.scrollWidget)
        self.borderWidget = ExpandBorderWidget(self)

        # expand animation
        self.expandAni = QPropertyAnimation(self.verticalScrollBar(), b'value', self)

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setFixedHeight(self.card.height())
        self.setViewportMargins(0, self.card.height(), 0, 0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # initialize layout
        self.scrollLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollLayout.setSpacing(0)
        self.scrollLayout.addWidget(self.view)
        self.scrollLayout.addWidget(self.spaceWidget)

        # initialize expand animation
        self.expandAni.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.expandAni.setDuration(200)

        # initialize style sheet
        self.view.setObjectName('view')
        self.scrollWidget.setObjectName('scrollWidget')
        self.setProperty('isExpand', False)
        FluentStyleSheet.EXPAND_SETTING_CARD.apply(self.card)
        FluentStyleSheet.EXPAND_SETTING_CARD.apply(self)

        self.card.installEventFilter(self)
        self.expandAni.valueChanged.connect(self._onExpandValueChanged)
        self.card.expandButton.clicked.connect(self.toggleExpand)

    def addWidget(self, widget: QWidget):
        """ add widget to tail """
        self.card.addWidget(widget)

    def wheelEvent(self, e):
        """ Modification!
        Ensure scrolling is working on this widget
        by passing the wheelEvent to its parent if any
        """
        if self.parentWidget():
            self.parentWidget().wheelEvent(e)

    def setExpand(self, isExpand: bool):
        """ set the expand status of card """
        if self.isExpand == isExpand:
            return

        # update style sheet
        self.isExpand = isExpand
        self.setProperty('isExpand', isExpand)
        self.setStyle(QApplication.style())

        # start expand animation
        if isExpand:
            h = self.viewLayout.sizeHint().height()
            self.verticalScrollBar().setValue(h)
            self.expandAni.setStartValue(h)
            self.expandAni.setEndValue(0)
        else:
            self.expandAni.setStartValue(0)
            self.expandAni.setEndValue(self.verticalScrollBar().maximum())

        self.expandAni.start()
        self.card.expandButton.setExpand(isExpand)

    def toggleExpand(self):
        """ toggle expand status """
        self.setExpand(not self.isExpand)

    def resizeEvent(self, e):
        self.card.resize(self.width(), self.card.height())
        self.scrollWidget.resize(self.width(), self.scrollWidget.height())

    def _onExpandValueChanged(self):
        vh = self.viewLayout.sizeHint().height()
        h = self.viewportMargins().top()
        self.setFixedHeight(max(h + vh - self.verticalScrollBar().value(), h))

    def _adjustViewSize(self):
        """ adjust view size """
        h = self.viewLayout.sizeHint().height()
        self.spaceWidget.setFixedHeight(h)

        if self.isExpand:
            self.setFixedHeight(self.card.height()+h)

    def setValue(self, value):
        """ set the value of config item """
        pass


# Courtesy of qfluentwidgets
class ExpandGroupSettingCard(ExpandSettingCard):
    """ Expand group setting card """

    def addGroupWidget(self, widget: QWidget):
        """ add widget to group """
        # add separator
        if self.viewLayout.count() >= 1:
            self.viewLayout.addWidget(GroupSeparator(self.view))

        widget.setParent(self.view)
        self.viewLayout.addWidget(widget)
        self._adjustViewSize()


class ExpandingSettingCard(ExpandGroupSettingCard):
    notifyCard = pyqtSignal(tuple) # notifyType, value
    disableCard = pyqtSignal(bool)
    disableChildren = pyqtSignal(bool)

    def __init__(self, setting: str, icon: Union[str, QIcon, FluentIconBase],
                 title: str, content: Optional[str], parent: Optional[QWidget]=None) -> None:
        """Expanding Setting card which can hold child cards

        Parameters
        ----------
        setting : str
            The name used for this card in the template

        icon : Union[str, QIcon, FluentIconBase]
            Display icon

        title : str
            Title of this card

        content : str, optional
            Extra text. Sort of a description. Defaults to None.

        parent : QWidget, optional
            The parent of this card. Defaults to None.
        """
        try:
            super().__init__(icon, title, content, parent)
            self._setting = setting
            self._option = None # type: AnySetting
            self._disableButton = None # type: PillPushButton
            self._resetbutton = None # type: PrimaryPushButton
            self._canGetDisabled = False
            self.isDisabled = False
            self.buttonLayout = QHBoxLayout()

            self.__initWidget()
            self.__initLayout()
            self.__connectSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def __initWidget(self) -> None:
        self._disableButton = PillPushButton(self.tr("Enabled"))
        self._disableButton.setObjectName("ui_disable")
        self._disableButton.clicked.connect(lambda: self.setDisableAll(not self.isDisabled))

    def __initLayout(self) -> None:
        self.buttonLayout.setSpacing(20)
        self.card.hBoxLayout.insertLayout(self.card.hBoxLayout.count()-2, self.buttonLayout) # Add buttonLayout as second-last of all child layouts
        self.card.hBoxLayout.addSpacing(10) # Add space for dropdown button - right side

    def __connectSignalToSlot(self) -> None:
        self.disableCard.connect(self.__onDisableCard)
        self.notifyCard.connect(self.__onParentNotified)

    def __onDisableCard(self, isDisabled: bool) -> None:
        self.isDisabled = isDisabled
        self._disableButton.click()

    def __onParentNotified(self, values: tuple[str, Any]) -> None:
        type = values[0]
        value = values[1]
        if type == "disable":
            self.__onDisableCard(value)
        elif type == "canGetDisabled":
            self._canGetDisabled = value
        elif type == "updateState":
            if self._canGetDisabled and self._option.isDisabled:
                self._disableButton.click()

    def addChild(self, child: QWidget) -> None:
        self.addGroupWidget(child)

    def getCardName(self) -> str:
        return self._setting

    def getOption(self) -> AnySetting | None:
        return self._option

    def setDisableAll(self, isDisabled: bool) -> None:
        self.isDisabled = isDisabled
        self.disableChildren.emit(self.isDisabled)
        if self._option:
            self._option.notifySetting.emit(("disable", (self.isDisabled, True)))
            if not isinstance(self._option, Switch):
                self._option.setHidden(self.isDisabled)

        self._disableButton.setText(self.tr("Disabled") if isDisabled else self.tr("Enabled"))

        if self._resetbutton:
            self._resetbutton.setDisabled(isDisabled)

    def setOption(self, widget: AnySetting):
        # Delete old instances
        if self._option:
            self._option.deleteLater()
        if self._resetbutton:
            self._resetbutton.deleteLater()

        self._option = widget
        self.buttonLayout.addWidget(widget, 0, Qt.AlignmentFlag.AlignRight)
        self.buttonLayout.addWidget(self._disableButton, 0, Qt.AlignmentFlag.AlignRight)

        # Special case for this class - do not show switch buttons/checkboxes since the disable button does the same thing
        if isinstance(widget, (Switch, CheckBox_)):
            widget.setHidden(True)
            self._canGetDisabled = True
            self._option.notifyParent.connect(self.__onParentNotified)
            self._option.notifySetting.emit(("content", None))
        else:
            self._option.notifySetting.emit(("canGetDisabled", None))

        if not self._canGetDisabled:
            self._resetbutton = PrimaryPushButton(self.tr("Reset"))
            self._resetbutton.clicked.connect(widget.resetValue)
            self.buttonLayout.addWidget(self._resetbutton, 0, Qt.AlignmentFlag.AlignRight)

        self.buttonLayout.addSpacing(15) # Add space for dropdown button - left side

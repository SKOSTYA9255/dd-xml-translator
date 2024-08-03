from qfluentwidgets import (ExpandGroupSettingCard, PrimaryPushButton, PillPushButton,
                            FluentIconBase)
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal

from typing import Any, Optional, Union

from app.components.settings.checkbox import CheckBox_
from app.components.settings.switch import Switch

from module.tools.types.gui_settings import AnySetting


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
            self.__connectpyqtSignalToSlot()
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

    def __connectpyqtSignalToSlot(self) -> None:
        self.disableCard.connect(self.__onDisableCard)

    def __onDisableCard(self, isDisabled: bool) -> None:
        self.isDisabled = not isDisabled
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

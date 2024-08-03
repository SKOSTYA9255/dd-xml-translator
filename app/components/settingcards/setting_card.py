from qfluentwidgets import FluentIconBase, FluentStyleSheet, isDarkTheme, PillPushButton, PrimaryPushButton
from qfluentwidgets.components.settings.setting_card import SettingIconWidget
from PyQt6.QtCore import pyqtSignal, pyqtBoundSignal, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from typing import Any, Optional, Union

from module.tools.types.gui_settings import AnySetting


class SettingCard(QFrame):
    """ Setting card. Courtesy of qfluentwidgets (with modifications) """

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title: str, content: Optional[str]=None,
                 parent: Optional[QWidget]=None):
        """
        Parameters
        ----------
        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        parent: QWidget
            parent widget
        """
        super().__init__(parent=parent)
        self.iconLabel = SettingIconWidget(icon, self)
        self.titleLabel = QLabel(title, self)
        self.contentLabel = QLabel(content or "", self)
        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        n = content.count("\n")
        self.setFixedHeight(60 + 15 * n-1  if content else 50)
        self.iconLabel.setFixedSize(16, 16)

        self.contentLabel.setHidden(not bool(content))
        self.contentLabel.setObjectName('contentLabel')

        # initialize layout
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(16, 0, 0, 0)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.hBoxLayout.addWidget(self.iconLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.hBoxLayout.addSpacing(16)

        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.vBoxLayout.addWidget(self.contentLabel, 0, Qt.AlignmentFlag.AlignLeft)

        self.hBoxLayout.addSpacing(16)
        self.hBoxLayout.addStretch(1)

        FluentStyleSheet.SETTING_CARD.apply(self)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        if isDarkTheme():
            painter.setBrush(QColor(255, 255, 255, 13))
            painter.setPen(QColor(0, 0, 0, 50))
        else:
            painter.setBrush(QColor(255, 255, 255, 170))
            painter.setPen(QColor(0, 0, 0, 19))

        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 6, 6)


class GenericSettingCard(SettingCard):
    disableCard = pyqtSignal(bool)
    disableChildren = pyqtSignal(bool)

    def __init__(self, setting: str, icon: Union[str, QIcon, FluentIconBase],
                 title: str, content: Optional[str], parent: Optional[QWidget]=None) -> None:
        """Generic Setting card

        Parameters
        ----------
        setting : str
            The name used for this card in the template

        icon : Union[str, QIcon, FluentIconBase]
            Display icon

        title : str
            Title of this card

        content : str
            Description of this card

        parent : QWidget, optional
            The parent of this card. Defaults to None.
        """
        try:
            super().__init__(icon, title, content, parent)
            self._setting = setting
            self._option = None # type: AnySetting
            self._disableButton = None # type: PillPushButton
            self._resetbutton = None # type: PrimaryPushButton
            self.isDisabled = False
            self.buttonLayout = QHBoxLayout()

            self.__initLayout()
            self.__connectpyqtSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def __initLayout(self) -> None:
        self.buttonLayout.setSpacing(20)
        self.hBoxLayout.addLayout(self.buttonLayout)

    def __connectpyqtSignalToSlot(self) -> None:
        self.disableCard.connect(self.__onDisableCard)

    def __onDisableCard(self, isDisabled: bool) -> None:
        self.isDisabled = not isDisabled
        self._disableButton.click()

    def __onParentNotified(self, values: tuple[str, Any]) -> None:
        type = values[0]
        value = values[1]
        if type == "disable":
            self.disableCard.emit(value)
        elif type == "canGetDisabled" and value:
            if self._disableButton is None:
                self.createDisableButton()
            if self._option.isDisabled:
                self._disableButton.click()
        elif type == "content":
            self.contentLabel.setText(value)
            self.contentLabel.setHidden(not bool(value))

    def getCardName(self) -> str:
        return self._setting

    def getOption(self) -> AnySetting | None:
        return self._option

    def createDisableButton(self) -> None:
        self._disableButton = PillPushButton(self.tr("Enabled"))
        self._disableButton.setObjectName("ui_disable")
        self._disableButton.clicked.connect(lambda: self.setDisableAll(not self.isDisabled))

    def setDisableAll(self, isDisabled: bool) -> None:
        self.isDisabled = isDisabled
        self.disableChildren.emit(self.isDisabled)
        if self._option:
            self._option.notifyParent.emit(self.isDisabled, True)
            self._option.setHidden(self.isDisabled)

        if self._disableButton:
            self._disableButton.setText(self.tr("Disabled") if isDisabled else self.tr("Enabled"))

        if self._resetbutton:
            self._resetbutton.setDisabled(isDisabled)

    def setOption(self, widget: AnySetting):
        # Delete old instances
        if self._option:
            self._option.deleteLater()
        if self._resetbutton:
            self._resetbutton.deleteLater()

        # Setting widget
        self._option = widget
        self.buttonLayout.addWidget(widget, 0, Qt.AlignmentFlag.AlignRight)

        # Setup communication between option and card
        self._option.notifyParent.connect(self.__onParentNotified)
        self._option.notifySetting.emit(("canGetDisabled", None))
        self._option.notifySetting.emit(("content", None))

        if self._disableButton:
            self.buttonLayout.addWidget(self._disableButton, 0, Qt.AlignmentFlag.AlignRight)

        # Reset button
        self._resetbutton = PrimaryPushButton(self.tr("Reset"))
        self._resetbutton.clicked.connect(widget.resetValue)
        self.buttonLayout.addWidget(self._resetbutton, 0, Qt.AlignmentFlag.AlignRight)

        self.buttonLayout.addSpacing(65) # Ensure it aligns with expand setting card


class ChildSettingCard(SettingCard):
    disableCard = pyqtSignal(bool)

    def __init__(self, setting: str, icon: Union[str, QIcon, FluentIconBase], title: str,
                 content: Optional[str]=None, parent: Optional[QWidget]=None) -> None:
        """ Child Setting card

        Parameters
        ----------
        setting : str
            The name used for this card in the template

        icon : Union[str, QIcon, FluentIconBase]
            Display icon

        title : str
            Title of this card

        content : str
            Description of this card

        parent : QWidget, optional
            The parent of this card. Defaults to None.
        """
        try:
            super().__init__(icon, title, content, parent)
            self._setting = setting
            self._option = None
            self._resetbutton = None
            self.isDisabled = False
            self.buttonLayout = QHBoxLayout()

            self.__initLayout()
            self.__connectpyqtSignalToSlot()
        except Exception:
            self.deleteLater()
            raise

    def __initLayout(self) -> None:
        self.buttonLayout.setSpacing(20)
        self.hBoxLayout.addLayout(self.buttonLayout)

    def __connectpyqtSignalToSlot(self) -> None:
        self.disableCard.connect((lambda: self.setDisableAll(not self.isDisabled)))

    def __onParentNotified(self, values: tuple[str, Any]) -> None:
        type = values[0]
        value = values[1]
        if type == "disable":
            self.disableCard.emit(value)
        elif type == "content":
            self.contentLabel.setText(value)
            self.contentLabel.setHidden(not bool(value))

    def getCardName(self) -> str:
        return self._setting

    def getOption(self) -> AnySetting | None:
        return self._option

    def setDisableAll(self, isDisabled: bool) -> None:
        if self._option:
            self._option.notifySetting.emit(("disable", (isDisabled, True)))
        if self._resetbutton:
            self._resetbutton.setDisabled(isDisabled)

    def setOption(self, widget: AnySetting):
        # Delete old instances
        if self._option:
            self._option.deleteLater()
        if self._resetbutton:
            self._resetbutton.deleteLater()

        # Setting widget
        self._option = widget
        self.buttonLayout.addWidget(widget, 0, Qt.AlignmentFlag.AlignRight)

        # Setup communication between option and card
        self._option.notifyParent.connect(self.__onParentNotified)
        self._option.notifySetting.emit(("content", None))

        # Reset button
        self._resetbutton = PrimaryPushButton(self.tr("Reset"))
        self._resetbutton.clicked.connect(widget.resetValue)
        self.buttonLayout.addWidget(self._resetbutton, 0, Qt.AlignmentFlag.AlignRight)

        self.buttonLayout.addSpacing(65) # Ensure it aligns with expand setting card

        if widget.isDisabled:
            self.disableCard.emit()

    def paintEvent(self, e) -> None:
        pass
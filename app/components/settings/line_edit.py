from qfluentwidgets import LineEdit
from PyQt6.QtWidgets import QWidget

from typing import Any, Optional

from app.common.signal_bus import signalBus
from app.components.settings.base_setting import BaseSetting

from module.tools.types.config import AnyConfig


class LineEdit_(BaseSetting):
    def __init__(self, config: AnyConfig, configkey: str, configname: str,
                 invalidmsg: Optional[dict[str, str]]=None, ui_disable: Optional[str]=None,
                 tooltip: Optional[str]=None, parent: Optional[QWidget]=None) -> None:
        """LineEdit widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        configkey : str
            The option key in the config which should be associated with this setting.

        configname : str
            The name of the config.

        invalidmsg : dict[str, str], optional
            The validation error message shown to the user.

        ui_disable: str, optional
            The value which disables this setting.

        tooltip : str, optional
            Tooltip for this setting, by default None.

        parent : QWidget, optional
            Parent of this class, by default None.
        """
        try:
            super().__init__(
                config=config,
                configkey=configkey,
                configname=configname,
                parent=parent
            )
            self.minWidth = 100
            self.maxWidth = 400
            self.invalidmsg = [val for val in invalidmsg.values()] if invalidmsg else ["", ""]
            self.lineEdit = LineEdit(self)
            self.currentValue = config.getValue(self.configkey, self.configname)
            self.defaultValue = self.config.getValue(self.configkey, self.configname, use_internal_config=True)
            self.disableValue = ui_disable
            self.backupValue = self.currentValue
            self.isDisabled = False

            # Set disabled status
            if self.currentValue == ui_disable:
                self.__setDisableWidget(isDisabled=True, saveValue=False)

            # Configure LineEdit
            self.lineEdit.setText(self.currentValue)
            self.lineEdit.setToolTip(tooltip)
            self.lineEdit.setToolTipDuration(4000)
            self.__resizeTextBox()

            # Add LineEdit to layout
            self.buttonlayout.addWidget(self.lineEdit)

            self.__connectpyqtSignalToSlot()
            signalBus.configUpdated.emit(self.configkey, (self.currentValue,))
        except Exception:
            self.deleteLater()
            raise

    def __connectpyqtSignalToSlot(self) -> None:
        self.lineEdit.editingFinished.connect(lambda: self.setValue(self.lineEdit.text()))
        self.lineEdit.textChanged.connect(self.__resizeTextBox)
        self.notifySetting.connect(self.__onParentNotification)
        signalBus.updateConfigSettings.connect(self.__onUpdateConfigSettings)

    def __onUpdateConfigSettings(self, configkey: str, value: tuple[Any,]) -> None:
        if self.configkey == configkey:
            self.setValue(value[0])

    def __onParentNotification(self, values: tuple) -> None:
        type = values[0]
        value = values[1]
        if type == "disable":
            self.__setDisableWidget(value[0], value[1])
        elif type == "canGetDisabled":
            self.notifyParent.emit(("canGetDisabled", self._canGetDisabled()))

    def __setDisableWidget(self, isDisabled: bool, saveValue: bool) -> None:
        if self.isDisabled != isDisabled:
            self.isDisabled = isDisabled
            self.lineEdit.setDisabled(self.isDisabled)

            if self.isDisabled:
                self.backupValue = self.currentValue
                value = self.disableValue
            else:
                value = self.backupValue
            if self.disableValue is not None and saveValue:
                self.setValue(value)

    def __resizeTextBox(self) -> None:
        padding = 24
        w = self.lineEdit.fontMetrics().boundingRect(self.lineEdit.text()).width()

        if w <= self.minWidth:
            w = self.minWidth
        elif w > self.maxWidth:
            w = self.maxWidth
        self.lineEdit.setFixedWidth(w + padding)

    def _canGetDisabled(self) -> bool:
        if self.disableValue is not None:
            return True
        return False

    def resetValue(self) -> None:
        self.setValue(self.defaultValue)

    def setValue(self, value: str) -> None:
        if self.currentValue != value:
            if self.config.setValue(self.configkey, value, self.configname):
                self.currentValue = value
                if not self.isDisabled:
                    self.lineEdit.setText(value)
                if value == self.disableValue:
                    self.notifyParent.emit(("disable", True))
            else:
                signalBus.configValidationError.emit(self.configname, self.invalidmsg[0], self.invalidmsg[1])

    def setMaxWidth(self, width: int) -> None:
        self.maxWidth = width if 0 < width > self.minWidth else self.maxWidth

    def setMinWidth(self, width: int) -> None:
        self.minWidth = width if 0 < width < self.maxWidth else 0
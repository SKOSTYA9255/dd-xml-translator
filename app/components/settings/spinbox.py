from qfluentwidgets import SpinBox
from PyQt6.QtWidgets import QWidget

from typing import Any, Optional

from app.common.signal_bus import signalBus
from app.components.settings.base_setting import BaseSetting

from module.tools.types.config import AnyConfig


class SpinBox_(BaseSetting):
    def __init__(self, config: AnyConfig, configkey:str, configname: str, min_value: int,
                 ui_disable: Optional[int]=None, parent: Optional[QWidget]=None) -> None:
        """Spinbox widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        configkey : str
            The option key in the config which should be associated with this setting.

        configname : str
            The name of the config.

        min : int
            The minimum value this setting will accept.

        ui_disable: int, optional
            The value which disables this setting.

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
            self.minValue = min_value
            self.spinboxButton = SpinBox(self)
            self.currentValue = self.config.getValue(self.configkey, self.configname)
            self.defaultValue = self.config.getValue(self.configkey, self.configname, use_internal_config=True)
            self.disableValue = ui_disable
            self.backupValue = self._ensureValidGUIValue(self.currentValue)
            self.isDisabled = False

            # Set disabled status
            if self.currentValue == ui_disable:
                self.__setDisableWidget(isDisabled=True, saveValue=False)

            # Ensure value cannot be invalid in the GUI
            self.currentValue = self._ensureValidGUIValue(self.currentValue)

            # Configure spinbox
            self.spinboxButton.setAccelerated(True)
            self.spinboxButton.setSingleStep(1)
            self.spinboxButton.setRange(min_value, 999999)
            self.spinboxButton.setValue(self.currentValue)

            # Add SpinBox to layout
            self.buttonlayout.addWidget(self.spinboxButton)

            self.__connectpyqtSignalToSlot()
            signalBus.configUpdated.emit(self.configkey, (self.currentValue,))
        except Exception:
            self.deleteLater()
            raise

    def __connectpyqtSignalToSlot(self) -> None:
        self.spinboxButton.valueChanged.connect(self.setValue)
        self.notifySetting.connect(self.__onParentNotification)
        signalBus.updateConfigSettings.connect(self._onUpdateConfigSettings)

    def _onUpdateConfigSettings(self, configkey: str, value: tuple[Any,]) -> None:
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
            self.spinboxButton.setDisabled(self.isDisabled)

            if self.isDisabled:
                self.backupValue = self._ensureValidGUIValue(self.currentValue)
                value = self.disableValue
            else:
                value = self.backupValue
            if self.disableValue is not None and saveValue:
                self.setValue(value)

    def _ensureValidGUIValue(self, value: int) -> int:
        if value < self.minValue:
            value = self.minValue
        return value

    def _canGetDisabled(self) -> bool:
        if self.disableValue is not None:
            return True
        return False

    def resetValue(self) -> None:
        self.setValue(self.defaultValue)

    def setValue(self, value: int) -> None:
        if self.currentValue != value:
            if self.config.setValue(self.configkey, value, self.configname):
                self.currentValue = value
                if value == self.disableValue:
                    self.notifyParent.emit(("disable", True))
                else:
                    # Do not update GUI with disable values
                    self.spinboxButton.setValue(value)
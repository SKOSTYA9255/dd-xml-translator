from qfluentwidgets import ColorPickerButton
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QColor, QHideEvent

from typing import Any, Optional

from app.common.signal_bus import signalBus
from app.components.settings.base_setting import BaseSetting

from module.tools.types.config import AnyConfig


class ColorPicker(BaseSetting):
    def __init__(self, config: AnyConfig, configkey: str, configname: str,
                 parent: Optional[QWidget]=None) -> None:
        """ColorPicker widget connected to a config key

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting

        configkey : str
            The option key in the config which should be associated with this setting

        configname : str
            The name of the config.

        title : str
            Widget title

        parent : QWidget, optional
            Parent of this class, by default None
        """
        try:
            super().__init__(
                config=config,
                configkey=configkey,
                configname=configname,
                parent=parent
            )
            self.currentValue = QColor(config.getValue(configkey, self.configname))
            self.defaultValue = QColor(config.getValue(configkey, self.configname, use_internal_config=True))
            self.disableValue = None # This setting cannot be disabled
            self.colorbutton = ColorPickerButton(self.currentValue, self.tr("application color"), self) # Lowercase string is intended

            # Add colorpicker to layout
            self.buttonlayout.addWidget(self.colorbutton)

            self.__connectpyqtSignalToSlot()
            signalBus.configUpdated.emit(self.configkey, (self.currentValue,))
        except Exception:
            self.deleteLater()
            raise

    def __connectpyqtSignalToSlot(self) -> None:
        self.colorbutton.colorChanged.connect(self.setValue)
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
            self.colorbutton.setDisabled(self.isDisabled)

            if self.isDisabled:
                self.backupValue = self.currentValue
                value = self.disableValue
            else:
                value = self.backupValue
            if self.disableValue is not None and saveValue:
                self.setValue(value)

    def _canGetDisabled(self) -> bool:
        if self.disableValue is not None:
            return True
        return False

    def setValue(self, color: QColor | str) -> None:
        if not isinstance(color, QColor):
            color = QColor(color)

        if self.currentValue != color:
            if self.config.setValue(self.configkey, color.name(), self.configname):
                self.currentValue = color
                self.colorbutton.setColor(color)
                if color == self.disableValue:
                    self.notifyParent.emit(("disable", True))

    def resetValue(self) -> None:
        self.setValue(self.defaultValue)
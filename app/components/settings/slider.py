from qfluentwidgets import Slider
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt

from typing import Any, Optional

from app.common.signal_bus import signalBus
from app.components.settings.base_setting import BaseSetting

from module.config.internal.app_args import AppArgs
from module.tools.types.config import AnyConfig
from module.tools.utilities import dictLookup


class Slider_(BaseSetting):
    def __init__(self, config: AnyConfig, configkey: str, configname: str, num_range: list[int], ui_disable: Optional[int]=None,
                 baseunit: Optional[str]=None, parent: Optional[QWidget]=None) -> None:
        """Slider widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        configkey : str
            The option key in the config which should be associated with this setting.

        configname : str
            The name of the config.

        range : list
            Slider range. range[0] == min | range[1] == max.

        ui_disable: int, optional
            The value which disables this setting.

        baseunit : str, optional
            The unit of the setting, e.g. "day", by default None.

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
            self.baseunit = baseunit
            self.numRange = num_range
            self.slider = Slider(Qt.Orientation.Horizontal, self)
            self.valueLabel = QLabel(self)
            self.currentValue = config.getValue(self.configkey, self.configname)
            self.defaultValue = self.config.getValue(self.configkey, self.configname, use_internal_config=True)
            self.disableValue = ui_disable
            self.backupValue = self._ensureValidGUIValue(self.currentValue)
            self.isDisabled = False
            self.notifyDisabled = True

            # Set disabled status
            if self.currentValue == ui_disable:
                self.__setDisableWidget(isDisabled=True, saveValue=False)

            # Ensure value cannot be invalid in the GUI
            self.currentValue = self._ensureValidGUIValue(self.currentValue)

            # Configure slider and label
            self.slider.setMinimumWidth(268)
            self.slider.setSingleStep(1)
            self.slider.setRange(num_range[0], num_range[1])
            self.slider.setValue(self.currentValue)
            self.__setLabelText(self.currentValue)
            self.valueLabel.setObjectName('valueLabel')

            # Add label and slider to layout
            self.buttonlayout.addWidget(self.valueLabel)
            self.buttonlayout.addWidget(self.slider)
            self.buttonlayout.addSpacing(-10)

            self.__connectSignalToSlot()
            signalBus.configUpdated.emit(self.configkey, (self.currentValue,))
        except Exception:
            self.deleteLater()
            raise

    def __connectSignalToSlot(self) -> None:
        self.slider.valueChanged.connect(self.setValue)
        self.notifySetting.connect(self.__onParentNotification)
        signalBus.updateConfigSettings.connect(self.__onUpdateConfigSettings)

    def __onUpdateConfigSettings(self, configkey: str, value: tuple[Any,]) -> None:
        if self.configkey == configkey:
            self.setValue(value[0])

    def __onParentNotification(self, values: tuple) -> None:
        type = values[0]
        value = values[1]
        if type == "disable":
            self.notifyDisabled = False
            self.__setDisableWidget(value[0], value[1])
            self.notifyDisabled = True
        elif type == "canGetDisabled":
            self.notifyParent.emit(("canGetDisabled", self._canGetDisabled()))

    def __setLabelText(self, value: int) -> None:
        if self.baseunit:
            unit = self.baseunit
            if value < -1 or value == 0 or value > 1:
                unit = dictLookup(AppArgs.config_units, unit)

            if unit is not None:
                if unit == "": # This unit does not have a plural definition
                    unit = self.baseunit
                self.valueLabel.setText(f"{value} {unit}")
                return
        self.valueLabel.setNum(value)

    def __setDisableWidget(self, isDisabled: bool, saveValue: bool) -> None:
        if self.isDisabled != isDisabled:
            self.isDisabled = isDisabled
            self.slider.setDisabled(self.isDisabled)
            self.valueLabel.setDisabled(self.isDisabled)

            if self.isDisabled:
                self.backupValue = self._ensureValidGUIValue(self.currentValue)
                value = self.disableValue
            else:
                value = self.backupValue
            if self._canGetDisabled() and saveValue:
                self.setValue(value)

    def _ensureValidGUIValue(self, value: int) -> int:
        if value < self.numRange[0]:
            value = self.numRange[0]
        return value

    def _canGetDisabled(self) -> bool:
        if self.disableValue is not None:
            return True
        return False

    def resetValue(self) -> None:
        self.setValue(self.defaultValue)

    def setValue(self, value: int) -> None:
        if self.currentValue != value or self.backupValue == value:
            if self.config.setValue(self.configkey, value, self.configname):
                self.currentValue = value
                if value == self.disableValue:
                    if self._canGetDisabled() and self.notifyDisabled:
                        self.notifyParent.emit(("disable", True))
                else:
                    # Do not update GUI with disable values
                    self.slider.setValue(value)
                    self.__setLabelText(value)
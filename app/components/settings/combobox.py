from qfluentwidgets import ComboBox
from PyQt6.QtWidgets import QWidget

from typing import Any, Optional, Union

from app.common.signal_bus import signalBus
from app.components.settings.base_setting import BaseSetting

from module.tools.types.config import AnyConfig


class ComboBox_(BaseSetting):
    def __init__(self, config: AnyConfig, configkey: str, configname: str, texts: Union[list, dict],
                 ui_disable: Optional[str]=None, parent: Optional[QWidget]=None) -> None:
        """Combobox widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        configkey : str
            The option key in the config which should be associated with this setting.

        configname : str
            The name of the config.

        texts : list | dict
            All possible values this option can have.

        ui_disable: str, optional
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
            self.comboBox = ComboBox(self)
            self.currentValue = config.getValue(self.configkey, self.configname)
            self.defaultValue = self.config.getValue(self.configkey, self.configname, use_internal_config=True)
            self.disableValue = ui_disable
            self.backupValue = self.currentValue
            self.isDisabled = False
            self.notifyDisabled = True

            # Set disabled status
            if self.currentValue == ui_disable:
                self.__setDisableWidget(isDisabled=True, saveValue=False)

            # Populate combobox with values
            if isinstance(texts, dict):
                for k, v in texts.items():
                    self.comboBox.addItem(k, userData=v)
            else:
                for text, option in zip(texts, texts):
                    self.comboBox.addItem(text, userData=option)

            self.comboBox.setCurrentText(self.currentValue)
            self.buttonlayout.addWidget(self.comboBox)

            self.__connectSignalToSlot()
            signalBus.configUpdated.emit(self.configkey, (self.currentValue,))
        except Exception:
            self.deleteLater()
            raise

    def __connectSignalToSlot(self) -> None:
        self.comboBox.currentIndexChanged.connect(lambda index: self.setValue(self.comboBox.itemData(index)))
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

    def __setDisableWidget(self, isDisabled: bool, saveValue: bool) -> None:
        if self.isDisabled != isDisabled:
            self.isDisabled = isDisabled
            self.comboBox.setDisabled(self.isDisabled)

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

    def resetValue(self) -> None:
        self.setValue(self.defaultValue)

    def setValue(self, value) -> None:
        if self.currentValue != value or self.backupValue == value:
            if self.config.setValue(self.configkey, value, self.configname):
                self.currentValue = value
                self.comboBox.setCurrentText(value)
                if self._canGetDisabled() and value == self.disableValue and self.notifyDisabled:
                    self.notifyParent.emit(("disable", True))
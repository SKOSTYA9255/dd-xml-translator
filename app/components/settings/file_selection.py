from qfluentwidgets import PushButton
from PyQt6.QtWidgets import QWidget, QFileDialog

from typing import Any, Optional

from app.common.signal_bus import signalBus
from app.components.settings.base_setting import BaseSetting

from module.tools.types.config import AnyConfig
from module.tools.types.general import StrPath

class FileSelect(BaseSetting):
    def __init__(self, config: AnyConfig, configkey: str, configname: str,
                 caption: str, directory: StrPath, filter: str, initial_filter: str,
                 ui_disable: Optional[bool]=None, parent: Optional[QWidget]=None) -> None:
        """File Select widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        configkey : str
            The option key in the config which should be associated with this setting.

        configname : str
            The name of the config.

        ui_disable: bool, optional
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
            self.caption = caption
            self.directory = directory
            self.filter = filter
            self.initial_filter = initial_filter
            self.selectButton = PushButton("Select")
            self.currentValue = self.config.getValue(self.configkey, self.configname)
            self.defaultValue = self.config.getValue(self.configkey, self.configname, use_internal_config=True)
            self.disableValue = ui_disable
            self.backupValue = self.currentValue
            self.isDisabled = False
            self.notifyDisabled = True

            # Set disabled status
            if self.currentValue == ui_disable:
                self.__setDisableWidget(isDisabled=True, saveValue=False)

            # Add file selection to layout
            self.buttonlayout.addWidget(self.selectButton)

            self.__connectSignalToSlot()
            signalBus.configUpdated.emit(self.configkey, (self.currentValue,))
        except Exception:
            self.deleteLater()
            raise

    def __connectSignalToSlot(self) -> None:
        self.selectButton.clicked.connect(self.__onSelectClicked)
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
        elif type == "content":
            self.notifyParent.emit(("content", self.currentValue))

    def __onSelectClicked(self) -> None:
        file = QFileDialog.getOpenFileName(
            parent=self.parent() if self.parent() else self,
            caption=self.caption,
            directory=self.directory,
            filter=self.filter,
            initialFilter=self.initial_filter
        )
        if file[0]:
            self.setValue(file[0])

    def __setDisableWidget(self, isDisabled: bool, saveValue: bool) -> None:
        if self.isDisabled != isDisabled:
            self.isDisabled = isDisabled
            self.selectButton.setDisabled(self.isDisabled)

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

    def setValue(self, value: StrPath) -> None:
        if self.currentValue != value or self.backupValue == value:
            if self.config.setValue(self.configkey, value, self.configname):
                self.currentValue = value
                self.notifyParent.emit(("content", self.currentValue))
                if self._canGetDisabled() and value == self.disableValue and self.notifyDisabled:
                    self.notifyParent.emit(("disable", True))

    def resetValue(self) -> None:
        self.setValue(self.defaultValue)
from typing import Any, Optional
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtGui import QHideEvent
from PyQt6.QtCore import pyqtSignal


from module.tools.types.config import AnyConfig

class BaseSetting(QWidget):
    notifySetting = pyqtSignal(tuple) # isDisabled, saveValue
    notifyParent = pyqtSignal(tuple) # notifyType, value

    def __init__(self, config: AnyConfig, configkey: str, configname: str,
                 parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.config = config
        self.configkey = configkey
        self.configname = configname
        self.buttonlayout = QHBoxLayout(self)

    def hideEvent(self, e: QHideEvent | None) -> None:
        super().hideEvent(e)
        self.config.saveConfig()

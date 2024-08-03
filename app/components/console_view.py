from qfluentwidgets import PrimaryPushButton
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import QSize, Qt, pyqtSignal

from typing import Optional

from app.common.stylesheet import StyleSheet
from app.components.text_area import TextArea


class ConsoleView(QWidget):
    terminationRequest = pyqtSignal(int)
    activated = pyqtSignal(bool)

    def __init__(self, processID: int, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.processID = processID
        self.consoleLabel = QLabel(self.tr(f"Process {processID}"))
        self.textArea = TextArea(
            object_name="console",
            read_only=True,
            parent=self
        )
        self.terminateButton = PrimaryPushButton(self.tr("Terminate"), self)
        self.terminateButton.setDisabled(True)
        self.vBoxLayout = QVBoxLayout(self)
        self.buttonLayout = QHBoxLayout()

        self.buttonLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.buttonLayout.setSpacing(20)
        self.buttonLayout.addWidget(self.terminateButton)

        self.vBoxLayout.addWidget(self.consoleLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.textArea, stretch=1)
        self.vBoxLayout.addLayout(self.buttonLayout)

        self.consoleLabel.setObjectName("Label")
        StyleSheet.CONSOLE_VIEW.apply(self)
        self._connectpyqtSignalToSlot()

    def _connectpyqtSignalToSlot(self) -> None:
        self.terminateButton.clicked.connect(self._onTerminationRequest)
        self.activated.connect(self.terminateButton.setEnabled)

    def _onTerminationRequest(self) -> None:
        self.terminationRequest.emit(self.processID)

    def write(self, text: str) -> None:
        self.textArea.write(text)

    def clear(self) -> None:
        self.textArea.clearText()

    def minimumSizeHint(self) -> QSize:
        return QSize(400, 400)
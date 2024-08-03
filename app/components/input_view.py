from qfluentwidgets import PushButton
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtBoundSignal

from typing import Optional

from app.common.stylesheet import StyleSheet
from app.components.text_area import TextArea


class InputView(QWidget):
    def __init__(self, label: str, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.tr(label))
        self.textArea = TextArea(read_only=False, parent=self)
        self.clearButton = None
        self.vBoxLayout = QVBoxLayout(self)
        self.buttonLayout = QHBoxLayout()

        self.buttonLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.buttonLayout.setSpacing(20)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout.addWidget(self.textArea, stretch=2)
        self.vBoxLayout.addLayout(self.buttonLayout)

        self.label.setObjectName("Label")
        self.setObjectName("inputView")
        StyleSheet.INPUT_VIEW.apply(self)

    def disableText(self, disable: bool) -> None:
        self.textArea.setDisabled(disable)

    def editingDone(self) -> pyqtBoundSignal:
        return self.textArea.editingDone()

    def addButton(self, button: QWidget) -> None:
        self.buttonLayout.addWidget(button)

    def enableClearButton(self) -> None:
        if self.clearButton is None:
            self.clearButton = PushButton(self.tr("Clear"), self)
            self.clearButton.clicked.connect(self.textArea.clearText)
            self.buttonLayout.addWidget(self.clearButton)

    def setReadOnly(self, value: bool) -> None:
        self.textArea.textEdit.setReadOnly(value)

    def setText(self, text: str) -> None:
        self.textArea.textEdit.setText(text)

    def text(self) -> str:
        return self.textArea.textEdit.toPlainText()
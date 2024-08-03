from qfluentwidgets import ScrollArea, TextEdit
from PyQt6.QtGui import QFocusEvent
from PyQt6.QtWidgets import QWidget, QTextEdit
from PyQt6.QtCore import Qt, pyqtSignal, pyqtBoundSignal

from typing import Optional

class ResponsiveTextEdit(TextEdit):
    editingDone = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def focusOutEvent(self, event: QFocusEvent):
        super().focusOutEvent(event)
        self.editingDone.emit(self.toPlainText())


class TextArea(ScrollArea):
    def __init__(self, read_only: bool=False, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.textEdit = ResponsiveTextEdit(self)
        self.textEdit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.textEdit.setReadOnly(read_only)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setWidget(self.textEdit)

        self.textEdit.setObjectName("textEdit")
        self.setObjectName("textArea")

    def write(self, text: str) -> None:
        self.textEdit.append(text)

    def clearText(self) -> None:
        self.textEdit.clear()

    def editingDone(self) -> pyqtBoundSignal:
        return self.textEdit.editingDone
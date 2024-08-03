import os
from pathlib import Path
from qfluentwidgets import ScrollArea, PrimaryPushButton, PushButton
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QSizePolicy
from typing import Any, Optional

import traceback

from app.common.signal_bus import signalBus
from app.common.stylesheet import StyleSheet
from app.components.infobar_test import InfoBar, InfoBarPosition
from app.components.input_view import InputView
from app.components.settings.line_edit import LineEdit_
from app.components.settings.combobox import ComboBox_

from module.config.app_config import AppConfig
from module.config.internal.app_args import AppArgs
from module.config.templates.app_template import AppTemplate
from module.config.tools.config_tools import retrieveDictValue
from module.logger import logger
from module.xml_tools import XMLParser, XMLSubstituter


class XMLInterface(ScrollArea):
    _app_config = AppConfig()
    _logger = logger

    def __init__(self, parent: Optional[QWidget]=None):
        try:
            super().__init__(parent=parent)
            self.parser = XMLParser()
            self.substituter = XMLSubstituter()

            self.view = QWidget(self)
            self.vBoxLayout = QVBoxLayout(self.view)
            self.hTextViewLayout = QHBoxLayout()
            self.hFileSelectLayout = QHBoxLayout()

            self.__initWidget()
            self.__initLayout()
            self.__connectpyqtSignalToSlot()
            self._parseXMLLocation()
        except Exception:
            self.deleteLater()
            raise

    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.__setQss()

    def __setQss(self):
        self.setObjectName('processInterface')
        self.view.setObjectName("view")
        StyleSheet.XML_INTERFACE.apply(self)

    def __initLayout(self):
        self.confirmButton = PrimaryPushButton(self.tr("Confirm"))

        self.xmlFileSelectButton = PushButton(self.tr("Select XML file"))
        self.xmlFileLocationSetting = LineEdit_(
            config=self._app_config,
            configkey="xmlLocation",
            configname=self._app_config.getConfigName(),
            invalidmsg=retrieveDictValue(AppTemplate().getTemplate(), "ui_invalidmsg", "xmlLocation", default=""),
        )
        self.xmlFileLocationSetting.setMaxWidth(600)

        self.extractedTextView = InputView("Extracted Input")
        self.extractLangTag = ComboBox_(
            config=self._app_config,
            configkey="extractLangTag",
            configname=self._app_config.getConfigName(),
            texts=AppArgs.template_langTags,
        )
        self.extractedTextView.setReadOnly(True)
        self.extractedTextView.addButton(self.extractLangTag)
        self.extractedTextView.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        self.translatedTextView = InputView("Translated Input")
        self.translatedLangTag = ComboBox_(
            config=self._app_config,
            configkey="writeLangTag",
            configname=self._app_config.getConfigName(),
            texts=AppArgs.template_langTags,
        )
        self.translatedTextView.enableClearButton()
        self.translatedTextView.addButton(self.translatedLangTag)
        self.translatedTextView.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.outputXMLPreview = InputView("XML Output Preview")
        self.outputXMLPreview.addButton(self.confirmButton)

        self.hTextViewLayout.setSpacing(20)
        self.hTextViewLayout.addWidget(self.extractedTextView, stretch=1)
        self.hTextViewLayout.addWidget(self.translatedTextView, stretch=1)
        self.hTextViewLayout.addWidget(self.outputXMLPreview, stretch=2)

        self.hFileSelectLayout.setSpacing(20)
        self.hFileSelectLayout.addWidget(self.xmlFileSelectButton)
        self.hFileSelectLayout.addWidget(self.xmlFileLocationSetting)
        self.hFileSelectLayout.addStretch(1)

        self.vBoxLayout.setContentsMargins(20, 0, 20, 36)
        self.vBoxLayout.addLayout(self.hTextViewLayout)
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addLayout(self.hFileSelectLayout)

    def __connectpyqtSignalToSlot(self):
        self.xmlFileSelectButton.clicked.connect(self._onFileSelectButtonClicked)
        self.translatedTextView.editingDone().connect(self._substituteXML)
        self.confirmButton.clicked.connect(self._onConfirmButtonClicked)
        signalBus.configUpdated.connect(self.__onAppConfigUpdated)
        signalBus.xml_process_exception.connect(self._onProcessException)
        # TODO: When the translated text is inserted in the text box, compare the length of it with that of the extracted text box
        #       Display warning if they differ and how much

    def __onAppConfigUpdated(self, configkey: str, valuePack: tuple[Any,]) -> None:
        value = valuePack[0]
        if configkey == "xmlLocation":
            self._parseXMLLocation()
        elif configkey == "extractLangTag":
            self._parseXMLLocation(True)
        elif configkey == "writeLangTag":
            self._substituteXML(self.translatedTextView.text())

    def _onFileSelectButtonClicked(self):
        file = QFileDialog.getOpenFileName(
            parent=self,
            caption=self.tr("Select XML file to translate"),
            directory=f"{AppArgs.app_dir}",
            filter=self.tr("XML Files (*.xml)"),
            initialFilter=self.tr("XML Files (*.xml)")
        )
        if file[0]:
            self.xmlFileLocationSetting.setValue(file[0])

    def _parseXMLLocation(self, t=False):
        location = self._app_config.getValue("xmlLocation")
        if location:
            self.parser.parse(location, self._app_config.getValue("extractLangTag"))
            extracted_text = self.parser.getExtractedText()
            self.extractedTextView.setText("".join(extracted_text))

    def _substituteXML(self, translation: str) -> None:
        clean_translation = []
        for line in translation.splitlines():
            if line != "":
                clean_translation.append(line)
        self.translatedTextView.setText("\n".join(clean_translation))

        self.substituter.substitute(
            write_lang_tag=self._app_config.getValue("writeLangTag"),
            parsed_xml_lines=self.parser.getParsedLines(),
            sanitized_xml=self.parser.getSanitizedInput(),
            localized_text=clean_translation
        )
        preview_xml = self.substituter.getPreviewXML()
        self.outputXMLPreview.setText("".join(preview_xml))

    def _onConfirmButtonClicked(self) -> None:
        try:
            xmlData = self.outputXMLPreview.text()
            if xmlData:
                if not AppArgs.data_dir.exists():
                    os.mkdir(AppArgs.data_dir.resolve())
                file_name = "TR_" + os.path.split(self._app_config.getValue("xmlLocation"))[1]
                dstPath = Path(AppArgs.data_dir, file_name).resolve()
                with open(dstPath, "w", encoding="utf-8") as file:
                    file.writelines(xmlData)
                    self._logger.debug(f"Saving XML to {dstPath}")
                InfoBar.success(
                    title="Translation saved!",
                    content=f"Location: {dstPath}",
                    isClosable=False,
                    duration=6000,
                    position=InfoBarPosition.TOP_RIGHT,
                    parent=self
                )
            else:
                InfoBar.warning(
                    title="Preview empty",
                    content="",
                    isClosable=False,
                    duration=4000,
                    position=InfoBarPosition.TOP_RIGHT,
                    parent=self
                )
        except Exception:
            msg = "An unexpected exception occurred while writing XML"
            trace = traceback.format_exc(limit=AppArgs.traceback_limit)
            self._logger.error(msg + "\n" + trace)
            self._onProcessException(msg, trace)

    def _onProcessException(self, msg: str, trace: str):
        InfoBar.error(
            title=msg,
            content=trace,
            orient=Qt.Orientation.Vertical if trace else Qt.Orientation.Horizontal,
            isClosable=True,
            duration=10000,
            position=InfoBarPosition.TOP,
            parent=self
        )
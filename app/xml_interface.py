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
from module.xml_tools import XMLParser, XMLSubstituter, XMLValidator

import requests
import json


class XMLInterface(ScrollArea):
    _app_config = AppConfig()
    _logger = logger

    def __init__(self, parent: Optional[QWidget]=None):
        try:
            super().__init__(parent=parent)
            self.parser = XMLParser(self._app_config)
            self.substituter = XMLSubstituter(self._app_config, self.parser)
            self.validator = XMLValidator(self._app_config, self.parser, self.substituter)
            self.xmlLocation = self._app_config.getValue("xmlLocation")
            self.extractLangTag = self._app_config.getValue("extractLangTag")
            self.writeLangTag = self._app_config.getValue("writeLangTag")
            self.previewErrorMessages = {} # type: dict[str, InfoBar | None]
            self.previewValid = False
            self.isReadOnlyViews = True

            self.view = QWidget(self)
            self.vBoxLayout = QVBoxLayout(self.view)
            self.hTextViewLayout = QHBoxLayout()
            self.hFileSelectLayout = QHBoxLayout()

            self.__initWidget()
            self.__initLayout()
            self.__connectSignalToSlot()
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
        self.translateButton = PrimaryPushButton(self.tr("Translate"))
        self.confirmButton = PrimaryPushButton(self.tr("Confirm"))
        self.xmlFileSelectButton = PushButton(self.tr("Select XML file"))
        self.xmlFileLocationSetting = LineEdit_(
            config=self._app_config,
            configkey="xmlLocation",
            configname=self._app_config.getConfigName(),
            invalidmsg=retrieveDictValue(AppTemplate().getTemplate(), "ui_invalidmsg", "xmlLocation", default=""),
        )
        self.xmlFileLocationSetting.setMaxWidth(self.parentWidget().width() // 2)

        self.extractedTextView = InputView("Extracted Input")
        self.extractLangTagSelect = ComboBox_(
            config=self._app_config,
            configkey="extractLangTag",
            configname=self._app_config.getConfigName(),
            texts=AppArgs.template_langTags,
        )
        self.extractedTextView.setReadOnly(self.isReadOnlyViews)
        self.extractedTextView.addButton(self.extractLangTagSelect)
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
        self.translatedTextView.addButton(self.translateButton)
        self.translatedTextView.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.outputXMLPreview = InputView("XML Output Preview")
        self.outputXMLPreview.addButton(self.confirmButton)
        self.outputXMLPreview.setReadOnly(self.isReadOnlyViews)

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

    def __connectSignalToSlot(self):
        self.translateButton.clicked.connect(self._substituteXML)
        self.confirmButton.clicked.connect(self._onConfirmButtonClicked)
        self.xmlFileSelectButton.clicked.connect(self._onFileSelectButtonClicked)
        self.translatedTextView.editingDone().connect(self._validateTranslation)
        if not self.isReadOnlyViews:
            self.outputXMLPreview.editingDone().connect(self._validatePreview)
        signalBus.configUpdated.connect(self.__onAppConfigUpdated)
        signalBus.xmlProcessException.connect(self._infoBarManager)
        signalBus.xmlValidationError.connect(self._infoBarManager)
        signalBus.xmlPreviewInvalid.connect(self._updatePreviewValidity)

    def __onAppConfigUpdated(self, configkey: str, valuePack: tuple[Any,]) -> None:
        value = valuePack[0]
        if configkey == "xmlLocation":
            self.xmlLocation = value
            self._parseXMLLocation()
        elif configkey == "extractLangTag":
            self.extractLangTag = value
            self._parseXMLLocation()
            if self.extractLangTag == self.writeLangTag:
                self._infoBarManager(f"TAG_Config", "ETAG_Language tags are identical", "", True)
        elif configkey == "writeLangTag":
            self.writeLangTag = value
            if self.extractLangTag == self.writeLangTag:
                self._infoBarManager(f"TAG_Config", "WTAG_Language tags are identical", "", True)

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

    def _parseXMLLocation(self):
        if self.xmlLocation:
            self.parser.parse(self.xmlLocation, self.extractLangTag)
            extractedText = self.parser.getExtractedText()
            self.extractedTextView.setText("\n".join(self.cleanTranslation(extractedText)))

    def _validateTranslation(self, translation: str) -> None:
        if not translation: return
        cleanTranslation = self.cleanTranslation(translation.splitlines())
        self.translatedTextView.setText("\n".join(cleanTranslation))

        extractSize = len(self.cleanTranslation(self.parser.getExtractedText()))
        translateSize = len(cleanTranslation)
        if extractSize == translateSize:
            # All good
            self._infoBarManager("LOCOK_InputLoc", "Translation and extraction length are matching", "")
        elif extractSize > translateSize:
            # Missing translations
            amount = extractSize-translateSize
            self._infoBarManager("LOCMIS_InputLoc", f"Missing {amount} {"translations" if amount != 1 else "translation"}",
                                 "Please check the translation to avoid missing localization entries in the output")
        else:
            # Too many translations
            self._infoBarManager("LOCEXC_InputLoc", f"Too many translations!",
                                 f"Excess translations: {translateSize-extractSize}\nThis will cause trouble for the XML engine")

    def _substituteXML(self) -> None:
        translation = []
        to_trans = self.parser.getExtractedText()
        for v in to_trans:
            url = "http://localhost:5000/translate"
            payload = {
                "q": v,
                "source": "zh-Hans",
                "target": "en",
                "format": "text",
                "api_key": ""
            }
            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(url, headers=headers, data=json.dumps(payload))

            try:
                translation.append(response.json()["translatedText"])
            except KeyError:
                translation.append(v) #can be changed to any message like "???" or "No translation avaliable"
                print("WARNING: No translation available for: ", v)
        

        print([translation if translation != "" or None else "No translation!"])
        if not translation: return
        self.substituter.substitute(
            write_lang_tag=self.writeLangTag,
            parsed_xml_lines=self.parser.getParsedLines(),
            extracted_text=self.parser.getExtractedText(),
            sanitized_xml=self.parser.getSanitizedInput(),
            localized_text=translation
        )
        previewXML = "".join(self.substituter.getPreviewXML())
        self.outputXMLPreview.setText(previewXML)
        self._validatePreview(previewXML)

    def cleanTranslation(self, translation: list[str]) -> list[str]:
        cleanTranslation = []
        for line in translation:
            if line != "":
                cleanTranslation.append(line)
        return cleanTranslation

    def _validatePreview(self, preview: str) -> None:
        self.validator.validatePreview(
            preview=preview.splitlines(),
            extract_lang_tag=self.extractLangTag,
            write_lang_tag=self.writeLangTag
        )

    def _onConfirmButtonClicked(self) -> None:
        try:
            xmlData = self.outputXMLPreview.text()
            if xmlData:
                if not AppArgs.data_dir.exists():
                    os.mkdir(AppArgs.data_dir.resolve())
                prefix = self._app_config.getValue("outFilePrefix")
                file_name = f"{prefix}{os.path.split(self.xmlLocation)[1]}"
                dstPath = Path(AppArgs.data_dir, file_name).resolve()
                with open(dstPath, "w", encoding="utf-8") as file:
                    file.writelines(xmlData)
                    self._logger.debug(f"Saving XML to {dstPath}")

                # No errors are present
                if self.previewValid:
                    InfoBar.success(
                        title="Translation saved",
                        content=f"Location: {dstPath}",
                        orient=Qt.Orientation.Vertical,
                        isClosable=False,
                        duration=5000,
                        position=InfoBarPosition.TOP_RIGHT,
                        parent=self
                    )
                # Errors are present
                else:
                    InfoBar.warning(
                        title="Translation saved with errors!",
                        content=f"Location: {dstPath}",
                        orient=Qt.Orientation.Vertical,
                        isClosable=False,
                        duration=5000,
                        position=InfoBarPosition.TOP_RIGHT,
                        parent=self
                    )
            else:
                InfoBar.info(
                    title="Preview empty",
                    content="",
                    isClosable=False,
                    duration=5000,
                    position=InfoBarPosition.TOP_RIGHT,
                    parent=self
                )
        except Exception:
            msg = "An unexpected exception occurred while saving XML"
            trace = traceback.format_exc(limit=AppArgs.traceback_limit)
            self._logger.error(msg + "\n" + trace)
            self._infoBarManager("PE_Saving", msg, trace)

    def _removeErrorMsg(self, errorType: str) -> None:
        self.previewErrorMessages[errorType] = None

    def _updatePreviewValidity(self, isValid: bool, showErrors: bool) -> None:
        if isValid or not showErrors:
            for errorType, infobar in self.previewErrorMessages.items():
                if errorType.find("VE_") != -1 and infobar:
                    infobar.close()
        self.previewValid = isValid

    def _infoBarManager(self, errorType: str, msg: str, content: str, singleton: bool=False) -> None:
        if errorType not in self.previewErrorMessages:
            self.previewErrorMessages |= {errorType: None}

        # The old error msg is now invalid
        if self.previewErrorMessages[errorType]:
            if singleton:
                return
            else:
                self.previewErrorMessages[errorType].close()

        if errorType.find("VE_W1") != -1:
            bar = InfoBar.warning(
                title=msg,
                content=content,
                orient=Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal,
                isClosable=True,
                duration=-1,
                position=InfoBarPosition.TOP_RIGHT,
                parent=self.outputXMLPreview
            )
        elif errorType.find("VE_E1") != -1:
            bar = InfoBar.error(
                title=msg,
                content=content,
                orient=Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal,
                isClosable=True,
                duration=-1,
                position=InfoBarPosition.TOP_LEFT,
                parent=self.outputXMLPreview
            )
        elif errorType.find("MALFIX_") != -1:
            bar = InfoBar.info(
                title=msg,
                content=content,
                orient=Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal,
                isClosable=True,
                duration=6000,
                position=InfoBarPosition.BOTTOM_RIGHT,
                parent=self
            )
        elif errorType.find("MAL_") != -1:
            bar = InfoBar.warning(
                title=msg,
                content=content,
                orient=Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal,
                isClosable=True,
                duration=-1,
                position=InfoBarPosition.TOP_LEFT,
                parent=self
            )
        elif errorType.find("TAG_") != -1:
            splitmsg = msg.split("_")
            changedTag = splitmsg[0]
            msg = splitmsg[1]
            bar = InfoBar.warning(
                title=msg,
                content=content,
                orient=Qt.Orientation.Horizontal,
                isClosable=False,
                duration=5000,
                position=InfoBarPosition.BOTTOM_RIGHT,
                parent=self.extractedTextView if changedTag == "ETAG" else self.translatedTextView
            )
        elif errorType.find("LOCOK_") != -1:
            bar = InfoBar.success(
                title=msg,
                content=content,
                orient=Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal,
                isClosable=True,
                duration=4000,
                position=InfoBarPosition.TOP,
                parent=self.translatedTextView
            )
        elif errorType.find("LOCMIS_") != -1:
            bar = InfoBar.warning(
                title=msg,
                content=content,
                orient=Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal,
                isClosable=True,
                duration=6000,
                position=InfoBarPosition.TOP,
                parent=self.translatedTextView
            )
        elif errorType.find("LOCEXC_") != -1:
            bar = InfoBar.error(
                title=msg,
                content=content,
                orient=Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal,
                isClosable=True,
                duration=6000,
                position=InfoBarPosition.TOP,
                parent=self.translatedTextView
            )
        else:
            bar = InfoBar.error(
                title=msg,
                content=content,
                orient=Qt.Orientation.Vertical if content else Qt.Orientation.Horizontal,
                isClosable=True,
                duration=8000,
                position=InfoBarPosition.TOP,
                parent=self
            )
        self.previewErrorMessages[errorType] = bar
        bar.closedpyqtSignal.connect(lambda: self._removeErrorMsg(errorType))
from typing import Any, Self, override

from module.config.internal.app_args import AppArgs
from module.config.internal.names import ModuleNames
from module.config.tools.config_tools import retrieveDictValue
from module.config.templates.abstract_template import BaseTemplate
from module.config.templates.template_enums import UITypes, UIGroups
from module.config.validators import validateLoglevel, validateTheme, validatePath, validateLangTag
from module.logger import logger


class AppTemplate(BaseTemplate):
    _instance = None
    _logger = logger

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.template_name = ModuleNames.app_name
            cls._app_config_template = cls._instance._createTemplate()
        return cls._instance

    @override
    @classmethod
    def getValue(self, key: str, parent_key: str=None, default: Any=None) -> Any:
        """ Return first value found. If there is no item with that key, return
        default.

        Has support for defining search scope with the parent key.
        A value will only be returned if it is within parent key's scope.
        """
        value = retrieveDictValue(
            d=self.getTemplate(),
            key=key,
            parent_key=parent_key,
            default=default
        )
        if value is None:
            if parent_key:
                self._logger.warn(f"Could not find key '{key}' inside the scope of parent key '{parent_key}' in the template. "
                                + f"Returning default: '{default}'")
            else:
                self._logger.warn(f"Could not find key '{key}' in the template. Returning default: '{default}'")
        return default if value is None else value

    @override
    def getTemplate(self) -> dict[str, dict]:
        return self._app_config_template

    @override
    def getTemplateName(self) -> str:
        return self.template_name

    @override
    def _createTemplate(self) -> dict[str, dict]:
        return {
            "General": {
                "loglevel": {
                    "ui_type": UITypes.COMBOBOX,
                    "ui_title": f"Set log level for {ModuleNames.app_name}",
                    "default": "INFO" if AppArgs.is_release else "DEBUG",
                    "values": AppArgs.template_loglevels,
                    "validators": [
                        validateLoglevel
                    ]
                },
                "messageSize": {
                    "ui_title": "Limit the size of (potentially) large info messages to reduce spam",
                    "ui_desc": "A value of -1 means no limit",
                    "ui_unit": "line",
                    "default": 15,
                    "min": -1,
                    "max": 30
                }
            },
            "Appearance": {
                "appTheme": {
                    "ui_type": UITypes.COMBOBOX,
                    "ui_title": "Set application theme",
                    "default": "System",
                    "values": AppArgs.template_themes,
                    "validators": [
                        validateTheme
                    ]
                },
                "appColor": {
                    "ui_type": UITypes.COLOR_PICKER,
                    "ui_title": "Set application color",
                    "default": "#2abdc7"
                },
                "appBackground": {
                    "ui_type": UITypes.FILE_SELECTION,
                    "ui_title": "Select background image",
                    "ui_file_filter": "Images (*.jpg *.jpeg *.png *.bmp)",
                    "default": "",
                    "validators": [
                        validatePath
                    ]
                },
                "backgroundOpacity": {
                    "ui_type": UITypes.SLIDER,
                    "ui_title": "Set background opacity",
                    "ui_desc": "A greater opacity yields a brighter background",
                    "default": 50,
                    "min": 0,
                    "max": 100
                },
                "backgroundBlur": {
                    "ui_type": UITypes.SLIDER,
                    "ui_title": "Set background blur radius",
                    "ui_desc": "A greater radius increases the blur effect",
                    "default": 0,
                    "min": 0,
                    "max": 30
                }
            },
            "XML": {
                "xmlLocation": {
                    "ui_exclude": True,
                    "default": "",
                    "ui_invalidmsg": {
                        "title": "Invalid path",
                        "desc": ""
                    },
                    "validators": [
                        validatePath
                    ]
                },
                "extractLangTag": {
                    "ui_exclude": True,
                    "default": "schinese",
                    "values": AppArgs.template_langTags,
                    "validators": [
                        validateLangTag
                    ]
                },
                "writeLangTag": {
                    "ui_exclude": True,
                    "default": "english",
                    "values": AppArgs.template_langTags,
                    "validators": [
                        validateLangTag
                    ]
                },
                "debugXML": {
                    "ui_title": "Enable debug mode",
                    "ui_desc": "Useful for debugging the XML engine",
                    "default": False
                },
                "colorCodeSep": {
                    "ui_title": "Exclude color codes from extraction",
                    "ui_desc": "Due to possible loss of text during translation, some color codes might still be included",
                    "default": True,
                    "ui_disable": False,
                    "ui_group_parent": [UIGroups.NESTED_CHILDREN, UIGroups.DISABLE_CHILDREN],
                    "ui_group": "colorCode"
                },
                "colorCodeSepLength": {
                    "ui_title": "Minimum text length for color code exclusion",
                    "ui_desc": "Any text with a length greater or equal to this will have color codes excluded",
                    "ui_unit": "character",
                    "default": 4,
                    "ui_disable": 0,
                    "min": 1,
                    "max": 20,
                    "ui_group": "colorCode"
                },
                "colorCodeDelim": {
                    "ui_title": "Character to delimit text between color codes",
                    "ui_desc": "Use a character not usually used in language. Otherwise, unexpected results might occur",
                    "default": "|",
                    "ui_group": "colorCode"
                },
                "colorCodeDelimSize": {
                    "ui_title": "Delimiter repeats",
                    "ui_desc": "Make the delimiter more likely to withstand translation. Without the delimiter, the translated text will be missing color codes",
                    "default": 4,
                    "min": 1,
                    "max": None,
                    "ui_group": "colorCode"
                },
                "outFilePrefix": {
                    "ui_title": "Add prefix to output XML file",
                    "ui_desc": "Can make it easier to discern translated files from non-translated",
                    "default": "TR_"
                }
            }
        }
from typing import Any, Self, override

from module.config.internal.app_args import AppArgs
from module.config.internal.names import ModuleNames
from module.config.tools.config_tools import retrieveDictValue
from module.config.templates.abstract_template import BaseTemplate
from module.config.templates.template_enums import UITypes
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
                }
            }
        }
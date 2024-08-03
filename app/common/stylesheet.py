from qfluentwidgets import StyleSheetBase, Theme, qconfig

import os
from enum import Enum

from module.config.internal.app_args import AppArgs


class StyleSheet(StyleSheetBase, Enum):
    """ Style sheet  """

    # Interfaces
    MAIN_WINDOW = "main_window"
    HOME_INTERFACE = "home_interface"
    XML_INTERFACE = "xml_interface"
    SETTINGS_INTERFACE = "settings_interface"
    SETTINGS_SUBINTERFACE = "settings_subinterface"

    # Components
    SAMPLE_CARD = f"components{os.sep}sample_card"
    LINK_CARD = f"components{os.sep}link_card"
    CONSOLE_VIEW = f"components{os.sep}console_view"
    INPUT_VIEW = f"components{os.sep}input_view"
    SETTING_WIDGET = f"components{os.sep}setting_widget"
    SETTING_CARD = f"components{os.sep}setting_card"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f"{AppArgs.qss_dir}{os.sep}{theme.value.lower()}{os.sep}{self.value}.qss"
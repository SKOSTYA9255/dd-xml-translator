from typing import TypeAlias

from app.components.settings.checkbox import CheckBox_
from app.components.settings.color_picker import ColorPicker
from app.components.settings.combobox import ComboBox_
from app.components.settings.line_edit import LineEdit_
from app.components.settings.slider import Slider_
from app.components.settings.spinbox import SpinBox_
from app.components.settings.switch import Switch

AnySetting: TypeAlias = (ColorPicker
                         | ComboBox_
                         | LineEdit_
                         | Slider_
                         | SpinBox_
                         | Switch
                         | CheckBox_
                         )
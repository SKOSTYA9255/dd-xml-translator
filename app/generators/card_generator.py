from qfluentwidgets import FluentIconBase
from qfluentwidgets import FluentIcon as FIF
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QIcon

import traceback
from typing import Union, Optional, override

from app.components.settingcards.expanding_settingcard import ExpandingSettingCard
from app.components.settingcards.scroll_settingcardgroup import ScrollSettingCardGroup
from app.components.settingcards.setting_card import GenericSettingCard, ChildSettingCard
from app.generators.generatorbase import GeneratorBase

from module.config.internal.app_args import AppArgs
from module.config.templates.template_enums import UIGroups, UITypes
from module.config.tools.template_options.groups import Group
from module.tools.types.config import AnyConfig
from module.tools.types.gui_cards import AnySettingCard
from module.tools.types.templates import AnyTemplate
"""
Explanation of terms:
    setting = A key which influences some decision in the program.
              Equivalent to a line in the config file or the GUI element created from said config.
              For instance, the setting for the line 'loglevel = "DEBUG"' in a config is 'loglevel'.

    option  = A child key of a setting in the Template.
              For instance, the setting "loglevel" contains a child key "default"
              (specifying the default value for "loglevel").
"""
class CardGenerator(GeneratorBase):
    def __init__(self, config: AnyConfig, template: AnyTemplate, config_name: Optional[str]=None,
                 default_group: Optional[str]=None, hide_group_label: bool=True,
                 parent: Optional[QWidget]=None, icons: Optional[list[Union[str, QIcon, FluentIconBase]]]=None) -> None:
        """Generate a Setting Card widget for each setting in the supplied template.
        The type of the Setting Card depends on various factors, including a setting's relation to other settings

        The Setting Card generator is useful for general-purpose templates containing a bit of everything.
        However, the Setting Cards do not look well in confined space, so keep that in mind.

        Parameters
        ----------
        config : AnyConfig
            The config object from which cards receive/store their values.

        template : AnyTemplate
            The template which cards are created from.
            The config should originate from the same template.

        config_name : str, optional
            The name of the config.
            By default None.

        default_group : str, optional
            The card group which is displayed on app start.
            By default None.

        hide_group_label : bool, optional
            Hide the name of the card group.
            Usually, some other GUI element takes care of displaying this.
            By default True.

        parent : QWidget, optional
            The parent of all card groups generated.
            By default None.

        icons : list[str | QIcon | FluentIconBase], optional
            Add an icon to each card generated.
            By default None.
        """
        super().__init__(
            config=config,
            template=template,
            config_name=config_name,
            default_group=default_group,
            hide_group_label=hide_group_label,
            parent=parent
        )
        self._icons = icons if icons else FIF.LEAF
        self._cards = self._generateCards(ScrollSettingCardGroup)

    @override
    def _createCard(self, cardType: UITypes, setting: str, options: str, content: str,
                    group: Group | None, parent: Optional[QWidget]=None) -> AnySettingCard | None:
        try:
            if isinstance(self._icons, list):
                icon = self._icons.pop(0)
            else:
                icon = self._icons

            title = options["ui_title"]
            widget = self._createSetting(
                cardType=cardType,
                setting_name=setting,
                options=options,
                parent=parent
            )
            # Create card widget
            if group and UIGroups.NESTED_CHILDREN in group.getUIGroupParent():
                if setting == group.getParentName():
                    card = ExpandingSettingCard(
                        setting=setting,
                        icon=icon,
                        title=title,
                        content=content,
                        parent=parent
                    )
                else:
                    card = ChildSettingCard(
                        setting=setting,
                        icon=icon,
                        title=title,
                        content=content,
                        parent=parent
                    )
            else:
                card = GenericSettingCard(
                    setting=setting,
                    icon=icon,
                    title=title,
                    content=content,
                    parent=parent
                )
            card.setOption(widget)
            return card
        except Exception:
            self._logger.error(f"Config '{self._template_name}': Error creating setting card for setting '{setting}'\n"
                               + traceback.format_exc(limit=AppArgs.traceback_limit))
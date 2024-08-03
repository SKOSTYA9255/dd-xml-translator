from abc import abstractmethod
from PyQt6.QtWidgets import QWidget
from typing import Optional

from app.generators.generator_tools import connectUIGroups, inferType, parseUnit, updateCardGrouping
from app.components.settings.checkbox import CheckBox_
from app.components.settings.color_picker import ColorPicker
from app.components.settings.combobox import ComboBox_
from app.components.settings.file_selection import FileSelect
from app.components.settings.line_edit import LineEdit_
from app.components.settings.slider import Slider_
from app.components.settings.spinbox import SpinBox_
from app.components.settings.switch import Switch

from module.config.internal.app_args import AppArgs
from module.config.templates.template_enums import UITypes
from module.config.tools.template_options.groups import Group
from module.config.tools.template_parser import TemplateParser
from module.logger import logger
from module.tools.types.config import AnyConfig
from module.tools.types.gui_cardgroups import AnyCardGroup
from module.tools.types.gui_cards import AnyCard, AnySettingCard
from module.tools.types.gui_settings import AnySetting
from module.tools.types.templates import AnyTemplate
from module.tools.utilities import iterToString


class GeneratorBase():
    _logger = logger

    def __init__(self, config: AnyConfig, template: AnyTemplate, config_name: Optional[str]=None,
                 default_group: Optional[str]=None, hide_group_label: bool=True, parent: Optional[QWidget]=None) -> None:
        if config.getFailureStatus():
            err_msg = f"Config '{type(config).__name__}' is invalid"
            raise RuntimeError(err_msg)
        self._config = config
        self._template = template
        self._template_name = self._template.getTemplateName()
        self._config_name = config_name if config_name else self._template_name
        self._default_group = default_group
        self._hide_group_label = hide_group_label
        self._parent = parent
        self._card_sort_order = {} # type: dict[str, list]    # Mapping of the correct card sort order.
        self._card_list = []       # type: list[AnyCardGroup] # Temp placement of unsorted cards.
        self._cards = []           # type: list[AnyCardGroup] # The cards sorted correctly.

    @abstractmethod
    def _createCard(self, cardType: UITypes, setting: str, options: dict, content: str,
                    group: Group | None, parent: Optional[QWidget]=None) -> AnyCard | None: ...

    def _createSetting(self, cardType: UITypes, setting_name: str, options: dict,
                      parent: Optional[QWidget]=None) -> AnySetting | None:
        """Create setting widget for use on a setting card.

        Parameters
        ----------
        cardType : UITypes
            The type of the setting, e.g. Switch.

        setting_name : str
            The name of the setting, i.e. its ID/key in the config.

        options : dict
            The options available for this setting, e.g. its default value.

        parent : QWidget, optional
            The parent of this setting, by default None.

        Returns
        -------
        AnySetting | None
            The setting widget object if created succesfully, else None.
        """
        widget = None
        if cardType == UITypes.SWITCH:
            widget = Switch(
                config=self._config,
                configkey=setting_name,
                configname=self._config_name,
                ui_disable=options["ui_disable"] if "ui_disable" in options else None,
                parent=parent
            )
        elif cardType == UITypes.CHECKBOX:
            widget = CheckBox_(
                config=self._config,
                configkey=setting_name,
                configname=self._config_name,
                ui_disable=options["ui_disable"] if "ui_disable" in options else None,
                parent=parent
            )
        elif cardType == UITypes.SLIDER:
            widget = Slider_(
                config=self._config,
                configkey=setting_name,
                configname=self._config_name,
                num_range=[options["min"], options["max"]],
                baseunit=parseUnit(setting_name, options, self._template_name),
                ui_disable=options["ui_disable"] if "ui_disable" in options else None,
                parent=parent
            )
        elif cardType == UITypes.SPINBOX:
            widget = SpinBox_(
                config=self._config,
                configkey=setting_name,
                configname=self._config_name,
                min_value=options["min"],
                ui_disable=options["ui_disable"] if "ui_disable" in options else None,
                parent=parent
            )
        elif cardType == UITypes.COMBOBOX:
            widget = ComboBox_(
                config=self._config,
                configkey=setting_name,
                configname=self._config_name,
                texts=options["values"],
                ui_disable=options["ui_disable"] if "ui_disable" in options else None,
                parent=parent
            )
        elif cardType == UITypes.LINE_EDIT:
            widget = LineEdit_(
                config=self._config,
                configkey=setting_name,
                configname=self._config_name,
                invalidmsg=options["ui_invalidmsg"] if "ui_invalidmsg" in options else None,
                ui_disable=options["ui_disable"] if "ui_disable" in options else None,
                tooltip=None,
                parent=parent
            )
        elif cardType == UITypes.COLOR_PICKER:
            widget = ColorPicker(
                config=self._config,
                configkey=setting_name,
                configname=self._config_name,
                parent=parent
            )
        elif cardType == UITypes.FILE_SELECTION:
            widget = FileSelect(
                config=self._config,
                configkey=setting_name,
                configname=self._config_name,
                caption=options["ui_title"],
                directory=f"{AppArgs.app_dir}",
                filter=options["ui_file_filter"],
                initial_filter=options["ui_file_filter"],
                ui_disable=options["ui_disable"] if "ui_disable" in options else None,
                parent=parent
            )
        else:
            self._logger.warn(f"Config '{self._template_name}': Invalid ui_type '{cardType}' for setting '{setting_name}'. "
                                + f"Expected one of '{iterToString(UITypes._member_names_, separator=', ')}'")
        return widget

    def _generateCards(self, CardGroup: AnyCardGroup) -> list[AnyCardGroup]:
        template = self._template.getTemplate()
        template_parser = TemplateParser()
        template_parser.parse(self._template_name, template)

        for section_name, section in template.items():
            card_group = CardGroup(f"{section_name}", self._parent) # type: AnyCardGroup
            for setting, options in section.items():

                if "ui_exclude" in options and options["ui_exclude"]:
                    self._logger.debug(f"Config '{self._template_name}': Excluding setting '{setting}' from settings panel")
                    continue

                # Parse the ui_group
                raw_group = f"{options["ui_group"]}" if "ui_group" in options else None

                # Split the ui_groups associated with this setting
                formatted_groups = template_parser.formatGroup(self._template_name, raw_group) if raw_group else None

                # If multiple groups are defined for a setting, the first is considered the main group
                main_group = template_parser.getGroup(self._template_name, formatted_groups[0]) if formatted_groups else None
                all_groups = [template_parser.getGroup(self._template_name, group) for group in formatted_groups] if formatted_groups else None

                card = self._createCard(
                    cardType=inferType(setting, options, self._template_name),
                    setting=setting,
                    options=options,
                    content=options["ui_desc"] if "ui_desc" in options else "",
                    group=main_group,
                    parent=card_group
                )
                if card:
                        if updateCardGrouping(
                            setting=setting,
                            cardGroup=card_group,
                            card=card,
                            groups=all_groups
                        ): self._updateCardSortOrder(card, card_group)
                else:
                    self._logger.warn(f"Config '{self._template_name}': Could not add setting '{setting}' to settings panel")

            if self._hide_group_label:
                card_group.getTitleLabel().setHidden(True)

            if self._default_group:
                if self._default_group == card_group.getTitleLabel().text():
                    self._default_group = card_group
            else:
                self._default_group = card_group

            self._card_list.append(card_group)

        final_all_groups = Group.getAllGroups(self._template_name)
        if final_all_groups:
            connectUIGroups(final_all_groups)
        self._addCardsBySortOrder()
        return self._card_list

    def _updateCardSortOrder(self, card: AnySettingCard,
                            cardGroup: AnyCardGroup) -> None:
        card_group_name = f"{cardGroup}"
        if card_group_name not in self._card_sort_order:
            self._card_sort_order |= {card_group_name: []}
        self._card_sort_order.get(card_group_name).append(card)

    def _addCardsBySortOrder(self) -> None:
        for i, card_group in enumerate(self._getCardList()):
            cards = self._card_sort_order.get(f"{card_group}")
            if cards:
                for card in cards:
                    card_group.addSettingCard(card)
            else:
                self._logger.warn(f"Config '{self._template_name}': Empty card group detected! Card group '{card_group.getTitleLabel().text()}' has no cards assigned to it. Removing")
                card_group.deleteLater()
                del self._getCardList()[i]

    def _getCardList(self) -> list[AnyCardGroup]:
        """ Temp placement of unsorted cards """
        return self._card_list

    def getCards(self) -> list[AnyCardGroup]:
        return self._cards

    def getDefaultGroup(self) -> AnyCardGroup:
        return self._default_group
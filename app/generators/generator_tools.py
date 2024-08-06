from typing import Iterable

from app.components.settings.switch import Switch

from module.config.internal.app_args import AppArgs
from module.config.templates.template_enums import UIGroups, UITypes
from module.config.tools.template_options.groups import Group
from module.logger import logger
from module.tools.types.gui_cardgroups import AnyCardGroup
from module.tools.types.gui_cards import AnyCard
from module.tools.utilities import iterToString

_logger_ = logger

def updateCardGrouping(setting: str, cardGroup: AnyCardGroup,
                card: AnyCard, groups: Iterable[Group] | None) -> bool:
    not_nested = True
    if groups:
        for group in groups:
            if setting == group.getParentName():
                # Note: parents are not added to the setting card group here,
                # since a parent can be a child of another parent
                group.setParentCard(card)
                group.setParentCardGroup(cardGroup) # Instead, save a reference to the card group
            else:
                if UIGroups.NESTED_CHILDREN in group.getUIGroupParent():
                    not_nested = False # Any nested setting must not be added directly to the card group
                group.addChildCard(card)
                group.addChildCardGroup(setting, cardGroup)
    return not_nested

def connectUIGroups(uiGroups: Iterable[Group]):
    for group in uiGroups:
        uiGroupParent = group.getUIGroupParent()
        parent        = group.getParentCard()
        parent_option = parent.getOption()

        if UIGroups.NESTED_CHILDREN in uiGroupParent:
            group.enforceLogicalNesting()
            for child in group.getChildCards():
                parent.addChild(child)

        if UIGroups.DISABLE_CHILDREN in uiGroupParent:
            for child in group.getChildCards():
                parent.disableChildren.connect(child.disableCard.emit)

        if UIGroups.SYNC_CHILDREN in uiGroupParent:
            for child in group.getChildCards():
                child_option = child.getOption()
                if isinstance(parent_option, Switch) and isinstance(child_option, Switch):
                    parent_option.getSwitchpyqtSignal().connect(child_option.setValueSync)
                else:
                    _logger_.warn(f"UI Group '{group.getGroupName()}': "
                                        + f"The option of both parent and child must be a switch. "
                                        + f"Parent '{parent.getCardName()}' has option of type '{type(parent_option).__name__}', "
                                        + f"child '{child.getCardName()}' has option of type '{type(child_option).__name__}'")

        if UIGroups.DESYNC_CHILDREN in uiGroupParent:
            for child in group.getChildCards():
                child_option = child.getOption()
                if isinstance(parent_option, Switch) and isinstance(child_option, Switch):
                    parent_option.getSwitchpyqtSignal().connect(child_option.setValueDesync)
                else:
                    _logger_.warn(f"UI Group '{group.getGroupName()}': "
                                        + f"The option of both parent and child must be a switch. "
                                        + f"Parent '{parent.getCardName()}' has option type '{type(parent_option).__name__}', "
                                        + f"child '{child.getCardName()}' has option type '{type(child_option).__name__}'")

        if UIGroups.DESYNC_TRUE_CHILDREN in uiGroupParent:
            for child in group.getChildCards():
                child_option = child.getOption()
                if isinstance(parent_option, Switch) and isinstance(child_option, Switch):
                    parent_option.getSwitchpyqtSignal().connect(child_option.setValueDesyncTrue)
                else:
                    _logger_.warn(f"UI Group '{group.getGroupName()}': "
                                        + f"The option of both parent and child must be a switch. "
                                        + f"Parent '{parent.getCardName()}' has option type '{type(parent_option).__name__}', "
                                        + f"child '{child.getCardName()}' has option type '{type(child_option).__name__}'")
        # Update parent's and its children's disable status
        if not group.isNestedChild():
            parent.notifyCard.emit(("updateState", None))

def inferType(setting: str, options: dict, config_name: str) -> UITypes | None:
    """ Infer card type from various options in the template """
    cardType = None
    if "ui_type" in options:
        cardType = options["ui_type"]
    elif "ui_invalidmsg" in options:
        cardType = UITypes.LINE_EDIT  # TODO: ui_invalidmsg should apply to all free-form input
    elif ("max" in options and options["max"] is None
          or "max" not in options and "min" in options):
        cardType = UITypes.SPINBOX
    elif isinstance(options["default"], bool):
        cardType = UITypes.SWITCH
    elif isinstance(options["default"], int):
        cardType = UITypes.SLIDER
    elif isinstance(options["default"], str):
        cardType = UITypes.LINE_EDIT # TODO: Temporary
    else:
        _logger_.warn(f"Config '{config_name}': Failed to infer ui_type for setting '{setting}'. The default value '{options["default"]}' has unsupported type '{type(options["default"])}'")
    return cardType

def parseUnit(setting: str, options: dict, config_name: str) -> str | None:
    baseunit = None
    if "ui_unit" in options:
        baseunit = options["ui_unit"]
        if not AppArgs.config_units.keys().__contains__(baseunit):
            _logger_.warn(f"Config '{config_name}': Setting '{setting}' has invalid unit '{options['ui_unit']}'. Expected one of '{iterToString(iter(AppArgs.config_units.keys()), separator=', ')}'")
    return baseunit
from enum import Enum


class UIGroups(Enum):
    """ Enums for ui_group_parent features """

    # This setting disables all child settings in its group when it changes state.
    DISABLE_CHILDREN = 0 # (Applies to: All)

    # This setting's children will be nested under it
    # Though the specifics of the nesting depend on the GUI config generator used.
    NESTED_CHILDREN = 1 # (Applies to: All)

    # This setting's children will change their value according to their parent
    SYNC_CHILDREN = 2 # (Applies to: Switch, CheckBox)

    # This setting's children will change their value opposite of their parent
    DESYNC_CHILDREN = 3 # (Applies to: Switch, CheckBox)

    # This setting's children will change their value opposite of their parent
    # (except if the parent's value is False - then the child remains unchanged)
    DESYNC_TRUE_CHILDREN = 4 # (Applies to: Switch, CheckBox)


class UITypes(Enum):
    """ Enums for UI type features """

    # Select color from color space
    COLOR_PICKER = 0

    # Drop-down select one of X possible values
    COMBOBOX = 1

    # One-line text field
    LINE_EDIT = 2

    # Sliding integer range
    SLIDER = 3

    # Integer input in a fixed, allowed range
    SPINBOX = 4

    # True/False
    SWITCH = 5

    # True/False
    CHECKBOX = 6

    # Select file
    FILE_SELECTION = 7
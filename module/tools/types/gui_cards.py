from typing import TypeAlias

from app.components.settingcards.expanding_settingcard import ExpandingSettingCard
from app.components.settingcards.setting_card import GenericSettingCard, ChildSettingCard

AnyCard: TypeAlias = (ExpandingSettingCard
                      | GenericSettingCard
                      | ChildSettingCard
                      )

AnyParentCard: TypeAlias = (ExpandingSettingCard
                            | GenericSettingCard
                            )

AnyNestingCard: TypeAlias = (ExpandingSettingCard
                             )

AnyChildCard: TypeAlias = ChildSettingCard

AnySettingCard: TypeAlias = (ExpandingSettingCard
                             | GenericSettingCard
                             | ChildSettingCard
                             )
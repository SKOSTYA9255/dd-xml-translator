from typing import Any, Callable


class ValidationInfo():
    def __init__(self) -> None:
        self._fields: dict[str, dict[str, tuple]] = {}
        self._validators: dict[str, dict[str, Any]] = {}

    def addField(self, section_name: str, field: dict):
        if not section_name in self._fields:
            self._fields |= {section_name: {}}
        self._fields[section_name] |= field

    def getFields(self) -> dict[str, dict[str, tuple]]:
        return self._fields

    def getValidators(self) -> dict[str, dict[str, Any]]:
        return self._validators

    def addSettingValidation(self, section_name: str, setting: str, validator: Callable):
        validator_name = f"{validator}"
        if section_name not in self._validators:
            self._validators |= {section_name: {}}

        if validator_name in self._validators[section_name]:
            self._validators[section_name][validator_name]["settings"].append(setting)
        else:
            validator_options = {"validator": validator, "settings": [setting]}
            self._validators[section_name] |= {validator_name: validator_options}
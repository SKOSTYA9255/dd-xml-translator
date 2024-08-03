from abc import ABC, abstractmethod
from typing import Any, Literal


class BaseConfig(ABC):
    """ Abstract Base Class for all configs """
    @abstractmethod
    def _initConfig(self) -> dict[str, Any]: ...

    @abstractmethod
    def _validateLoad(self, raw_config: dict) -> dict[str, Any]: ...

    @abstractmethod
    def _validate(self, save_config: dict, config_name: str) -> dict[str, Any]: ...

    @abstractmethod
    def getConfig(self) -> dict[str, Any]: ...

    @abstractmethod
    def getConfigName(self) -> str: ...

    @abstractmethod
    def getFailureStatus(self) -> bool: ...

    @abstractmethod
    def getValue(self, key: str, default: Any=None, use_internal_config: bool=False) -> Any: ...

    @abstractmethod
    def setValue(self, key: str, value: Any, config_name: str) -> Literal[1] | None: ...

    @abstractmethod
    def saveConfig(self) -> None: ...
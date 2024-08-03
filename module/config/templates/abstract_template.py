from abc import ABC, abstractmethod
from typing import Any


class BaseTemplate(ABC):
    """Abstract Base Class for all templates"""

    @abstractmethod
    def getValue(key: str, parent_key: str=None, default: Any=None) -> Any: ...

    @abstractmethod
    def getTemplateName(self) -> str: ...

    @abstractmethod
    def getTemplate(self) -> dict[str, dict]: ...

    @abstractmethod
    def _createTemplate(self) -> dict[str, dict]: ...
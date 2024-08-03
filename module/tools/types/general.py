import os
from typing import Any, TypeAlias

from pydantic import BaseModel

StrPath: TypeAlias = str | os.PathLike[str]
Model: TypeAlias = BaseModel
type NestedDict = dict[str, dict[str, dict[str, Any]]]
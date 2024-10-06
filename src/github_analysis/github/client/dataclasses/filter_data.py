from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Generic, TypeVar

ItemNode = TypeVar("ItemNode")


@dataclass
class FilterData(Generic[ItemNode]):
    until: datetime
    get_create_at_from_node: Callable[[ItemNode], datetime]

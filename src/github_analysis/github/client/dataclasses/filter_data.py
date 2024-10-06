from datetime import datetime
from typing import Callable, Generic, TypeVar

from attrs import define

ItemNode = TypeVar("ItemNode")


@define
class FilterData(Generic[ItemNode]):
    until: datetime
    get_create_at_from_node: Callable[[ItemNode], datetime]

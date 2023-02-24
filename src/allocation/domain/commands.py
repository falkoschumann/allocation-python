import dataclasses
from datetime import date
from typing import Optional


class Command:
    pass


@dataclasses.dataclass
class Allocate(Command):
    orderid: str
    sku: str
    qty: int


@dataclasses.dataclass
class CreateBatch(Command):
    ref: str
    sku: str
    qty: int
    eta: Optional[date] = None


@dataclasses.dataclass
class ChangeBatchQuantity(Command):
    ref: str
    qty: int

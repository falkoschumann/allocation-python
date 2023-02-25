import dataclasses


class Event:
    pass


@dataclasses.dataclass
class Allocated(Event):
    orderid: str
    sku: str
    qty: int
    batchref: str


@dataclasses.dataclass
class Deallocated(Event):
    orderid: str
    sku: str
    qty: int


@dataclasses.dataclass
class OutOfStock(Event):
    sku: str

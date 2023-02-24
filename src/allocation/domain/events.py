import dataclasses


class Event:
    pass


@dataclasses.dataclass
class OutOfStock(Event):
    sku: str

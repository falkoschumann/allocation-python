import uuid


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name: int | str = "") -> str:
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name: int | str = ""):
    return f"order-{name}-{random_suffix()}"

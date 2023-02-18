from abc import abstractmethod
from typing import Protocol

from allocation.domain import model


class AbstractProductRepository(Protocol):
    @abstractmethod
    def add(self, batch: model.Product):
        raise NotImplementedError

    @abstractmethod
    def get(self, sku) -> model.Product:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractProductRepository):
    def __init__(self, session):
        self.session = session

    def add(self, product):
        self.session.add(product)

    def get(self, sku):
        return self.session.query(model.Product).filter_by(sku=sku).first()

import sqlalchemy

from allocation.service_layer import unit_of_work


def allocations(orderid: str, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        results = uow.session.execute(
            sqlalchemy.sql.text(
                """
                SELECT sku, batchref
                  FROM allocations_view
                 WHERE orderid = :orderid
                """
            ),
            dict(orderid=orderid),
        )
        return [{"sku": sku, "batchref": batchref} for sku, batchref in results]

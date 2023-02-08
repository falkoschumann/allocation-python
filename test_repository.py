import unittest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import clear_mappers, Session

import model
import repository
from orm import mapper_registry, start_mappers


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:", echo=True)
        mapper_registry.metadata.create_all(engine)
        start_mappers()
        self.session = Session(engine)

    def tearDown(self):
        clear_mappers()

    def test_repository_can_save_a_batch(self):
        batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)
        repo = repository.SqlAlchemyRepository(self.session)

        repo.add(batch)
        self.session.commit()

        rows = list(self.session.execute(text('''
        SELECT reference, sku, _purchased_quantity, eta
          FROM batches
        ''')))
        self.assertEqual(rows, [("batch1", "RUSTY-SOAPDISH", 100, None)])

    def insert_order_line(self):
        self.session.execute(
            text('''
            INSERT INTO order_lines (orderid, sku, qty)
            VALUES ("order1", "GENERIC-SOFA", 12)
            ''')
        )
        [[orderline_id]] = self.session.execute(
            text('''
            SELECT id
              FROM order_lines
             WHERE orderid=:orderid
               AND sku=:sku
            '''),
            dict(orderid="order1", sku="GENERIC-SOFA"),
        )
        return orderline_id

    def insert_batch(self, batch_id):
        self.session.execute(
            text('''
            INSERT INTO batches (reference, sku, _purchased_quantity, eta)
            VALUES (:batch_id, "GENERIC-SOFA", 100, null)
            '''),
            dict(batch_id=batch_id),
        )
        [[batch_id]] = self.session.execute(
            text('''
            SELECT id
              FROM batches
             WHERE reference=:batch_id
               AND sku="GENERIC-SOFA"
            '''),
            dict(batch_id=batch_id),
        )
        return batch_id

    def insert_allocation(self, orderline_id, batch_id):
        self.session.execute(
            text('''
            INSERT INTO allocations (orderline_id, batch_id)
            VALUES (:orderline_id, :batch_id)
            '''),
            dict(orderline_id=orderline_id, batch_id=batch_id),
        )

    def test_repository_can_retrieve_a_batch_with_allocations(self):
        orderline_id = self.insert_order_line()
        batch1_id = self.insert_batch("batch1")
        self.insert_batch("batch2")
        self.insert_allocation(orderline_id, batch1_id)
        repo = repository.SqlAlchemyRepository(self.session)

        retrieved = repo.get("batch1")

        expected = model.Batch("batch1", "GENERIC-SOFA", 100, eta=None)
        self.assertEqual(retrieved, expected)  # Batch.__eq__ only compares reference
        self.assertEqual(retrieved.sku, expected.sku)
        self.assertEqual(retrieved._purchased_quantity, expected._purchased_quantity)
        self.assertEqual(retrieved._allocations, {
            model.OrderLine("order1", "GENERIC-SOFA", 12),
        })

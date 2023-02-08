import unittest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import clear_mappers, Session

import model
from orm import mapper_registry, start_mappers


class OrmTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:", echo=True)
        mapper_registry.metadata.create_all(engine)
        start_mappers()
        self.session = Session(engine)

    def tearDown(self):
        clear_mappers()

    def test_orderline_mapper_can_load_lines(self):
        self.session.execute(
            text('''
            INSERT INTO order_lines (orderid, sku, qty)
            VALUES ("order1", "RED-CHAIR", 12),
                   ("order1", "RED-TABLE", 13),
                   ("order2", "BLUE-LIPSTICK", 14)
            ''')
        )

        expected = [
            model.OrderLine("order1", "RED-CHAIR", 12),
            model.OrderLine("order1", "RED-TABLE", 13),
            model.OrderLine("order2", "BLUE-LIPSTICK", 14),
        ]
        self.assertEqual(self.session.query(model.OrderLine).all(), expected)

    def test_orderline_mapper_can_save_lines(self):
        new_line = model.OrderLine("order1", "DECORATIVE-WIDGET", 12)
        self.session.add(new_line)
        self.session.commit()

        rows = list(self.session.execute(text('''
            SELECT orderid, sku, qty
              FROM order_lines
            ''')))
        self.assertEqual(rows, [("order1", "DECORATIVE-WIDGET", 12)])

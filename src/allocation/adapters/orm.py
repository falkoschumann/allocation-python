import sqlalchemy.orm
from sqlalchemy import event
from sqlalchemy.sql import schema, sqltypes

from allocation.domain import model

mapper_registry = sqlalchemy.orm.registry()
metadata = mapper_registry.metadata

order_lines = schema.Table(
    "order_lines",
    metadata,
    schema.Column("id", sqltypes.Integer, primary_key=True, autoincrement=True),
    schema.Column("sku", sqltypes.String(255)),
    schema.Column("qty", sqltypes.Integer, nullable=False),
    schema.Column("orderid", sqltypes.String(255)), )

products = schema.Table(
    "products",
    metadata,
    schema.Column("sku", sqltypes.String(255), primary_key=True),
    schema.Column(
        "version_number", sqltypes.Integer, nullable=False, server_default="0"
    )
)

batches = schema.Table(
    "batches",
    metadata,
    schema.Column("id", sqltypes.Integer, primary_key=True, autoincrement=True),
    schema.Column("reference", sqltypes.String(255)),
    schema.Column("sku", schema.ForeignKey("products.sku")),
    schema.Column("_purchased_quantity", sqltypes.Integer, nullable=False),
    schema.Column("eta", sqltypes.Date, nullable=True), )

allocations = schema.Table(
    "allocations",
    metadata,
    schema.Column("id", sqltypes.Integer, primary_key=True, autoincrement=True),
    schema.Column("orderline_id", schema.ForeignKey("order_lines.id")),
    schema.Column("batch_id", schema.ForeignKey("batches.id")), )


def start_mappers():
    lines_mapper = mapper_registry.map_imperatively(
        model.OrderLine, order_lines
    )
    batches_mapper = mapper_registry.map_imperatively(
        model.Batch, batches, properties={
            "_allocations": sqlalchemy.orm.relationship(
                lines_mapper, secondary=allocations, collection_class=set
            )
        }, )
    mapper_registry.map_imperatively(
        model.Product, products, properties={
            "batches": sqlalchemy.orm.relationship(batches_mapper)
        }
    )


@event.listens_for(model.Product, "load")
def receive_load(product, _):
    product.events = []

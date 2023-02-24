from datetime import datetime

import flask.app
import flask.globals

from allocation.adapters import orm
from allocation.domain import commands
from allocation.service_layer import handlers, messagebus, unit_of_work

app = flask.app.Flask(__name__)
orm.start_mappers()


@app.route("/add_batch", methods=["POST"])
def add_batch():
    request = flask.globals.request
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    event = commands.CreateBatch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        eta
    )
    messagebus.handle(event, unit_of_work.SqlAlchemyUnitOfWork())
    return "OK", 201


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    try:
        request = flask.globals.request
        event = commands.Allocate(
            request.json["orderid"],
            request.json["sku"],
            request.json["qty"],
        )
        results = messagebus.handle(event, unit_of_work.SqlAlchemyUnitOfWork())
        batchref = results.pop(0)
    except handlers.InvalidSku as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201

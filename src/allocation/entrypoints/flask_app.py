from datetime import datetime

import flask.app
import flask.globals

from allocation import views
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
        messagebus.handle(event, unit_of_work.SqlAlchemyUnitOfWork())
    except handlers.InvalidSku as e:
        return {"message": str(e)}, 400

    return "OK", 202


@app.route("/allocations/<orderid>", methods=['GET'])
def allocations_view_endpoint(orderid):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    result = views.allocations(orderid, uow)
    if not result:
        return 'not found', 404
    return flask.jsonify(result), 200

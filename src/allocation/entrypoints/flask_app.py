from datetime import datetime

import flask.app
import flask.globals

from allocation import bootstrap, views
from allocation.domain import commands
from allocation.service_layer import handlers

app = flask.app.Flask(__name__)
bus = bootstrap.bootstrap()


@app.route("/add_batch", methods=["POST"])
def add_batch():
    eta = flask.globals.request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    event = commands.CreateBatch(
        flask.globals.request.json["ref"],
        flask.globals.request.json["sku"],
        flask.globals.request.json["qty"],
        eta,
    )
    bus.handle(event)
    return "OK", 201


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    try:
        event = commands.Allocate(
            flask.globals.request.json["orderid"],
            flask.globals.request.json["sku"],
            flask.globals.request.json["qty"],
        )
        bus.handle(event)
    except handlers.InvalidSku as e:
        return {"message": str(e)}, 400

    return "OK", 202


@app.route("/allocations/<orderid>", methods=["GET"])
def allocations_view_endpoint(orderid):
    result = views.allocations(orderid, bus.uow)
    if not result:
        return "not found", 404
    return flask.jsonify(result), 200

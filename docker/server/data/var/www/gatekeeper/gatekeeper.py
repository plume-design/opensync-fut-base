#!/usr/bin/env python3

import logging

from docker.server.data.var.www.gatekeeper.lib import gatekeeper_io
from flask import Flask
from flask import jsonify
from flask import make_response
from flask import request
from flask_cors import CORS


app = Flask(__name__, static_folder="static")
fut_cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"
CORS(app, expose_headers=["x-suggested-filename"])

gatekeeper_log_file = "/tmp/fut_gatekeeper.log"
gatekeeper_logger = logging.getLogger("GatekeeperLogger")
gatekeeper_logger_fh = logging.FileHandler(gatekeeper_log_file, mode="w")
gatekeeper_logger.setLevel(logging.DEBUG)
gatekeeper_logger.addHandler(gatekeeper_logger_fh)


@app.route("/gatekeeper", methods=["GET", "POST"])
def gatekeeper_api():
    if request.method == "GET":
        m = "This is GET call"
        gatekeeper_logger.info(m)
        foo = {"foo": "foo_val", "bar": {"subbar": "subbar_val"}}
        response = make_response(jsonify(foo))
        return response

    if request.method == "POST":
        m = "This is POST call to gatekeeper"
        gatekeeper_logger.info(m)
        req = gatekeeper_io.Req(request, logger=gatekeeper_logger)
        response = req.deserialize()
        return response


@app.route("/gatekeeper/test/<path:path>", methods=["GET", "POST"])
def gatekeeper_test(path):
    return {
        "success": True,
        "url_path": f"fut.opensync.io/gatekeeper/test/{path}",
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

import logging
import threading

from flask import Flask, Response
from http import HTTPStatus

import services
from config import config

app = Flask(__name__)
logger = logging.getLogger()


class HttpServer(threading.Thread):
    """
    Creates a new flask HTTP server.
    """

    def __init__(self):
        super().__init__(daemon=True, name='http_server')


    def run(self):
        # if debug is set to True, you can't access
        # flask across a network
        app.debug = False

        try:
            app.run(
                host=config.flask.host,
                port=config.flask.port
            )
        except KeyboardInterrupt:
            logger.info('Flask got interrupt. Quitting.')


@app.route("/livez")
def liveness():
    """
    Checks if the service is alive.
    Pod will be restarted if this endpoint returns an error.
    """
    return Response('Service is alive!', status=HTTPStatus.OK)


@app.route("/readyz")
def readiness():
    """
    Checks if the service is ready to accept requests.
    If the stream is not running, then the service is not ready as any requests received during this period will result in an error.
    Pod will not be restarted if this endpoint returns an error
    """
    if services.monitor.bitrate and services.monitor.bitrate > 5000:
        return Response('Service is ready!', status=HTTPStatus.OK)

    return Response('Stream is not running, service is not ready!', status=HTTPStatus.SERVICE_UNAVAILABLE)



from services.stream import LiveStream
from services.flask import HttpServer
from services.monitor import Monitor


stream = None
monitor = None
server = None


def start():
    """ starts all services """
    
    global stream
    global monitor
    global server

    # start the live stream
    stream = LiveStream()
    stream.start()

    # start the monitor
    monitor = Monitor()
    monitor.start()

    # start the flask server
    server = HttpServer()
    server.start()
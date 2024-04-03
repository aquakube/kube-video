import time
import logging
import threading
from xml.etree import ElementTree
import requests
from collections.abc import Iterable

from opentelemetry.sdk.metrics import Meter
from opentelemetry.metrics import CallbackOptions, Observation

from clients.opentelemetry import OpenTelemetryClient
from config import config
import services

logger = logging.getLogger()

class Monitor(threading.Thread):
    """
    Thread that periodically pulls data from nginx to either start or stop a stream
    """

    def __init__(self):
        super().__init__(daemon=True, name='monitor')
        self.opentelemetry_client = OpenTelemetryClient()
        self.bitrate = None


    def run(self):
        """
        Starts the bitrate monitor and performs routine health checks to attempt to recover on failures
        """
        self.opentelemetry_client.meter.create_observable_gauge(
            name='bitrate',
            unit='Mbps',
            callbacks=[self.get_observed_bitrate_callback()]
        )
        time.sleep(config.monitor.startup_delay)

        while True:
            self.health_check()
            time.sleep(config.monitor.poll_interval)


    def get_observed_bitrate_callback(self):
        """ Function for acquiring a cllback to read a property as an observable gauge"""

        def get_bitrate_callback(options: CallbackOptions):
            """ Callback function for getting the bitrate of a stream """
            return [
                Observation(
                    value = self.get_bitrate(),
                    attributes = {}
                )
            ]

        return get_bitrate_callback


    def get_bitrate(self):
        """ Returns the current bitrate of the stream """
        try:
            element: ElementTree.Element | None = next((element for element in self.poll() if config.video.name in element.find('name').text), None)
            self.bitrate = int(element.find('bw_in').text) if element is not None else None
            if self.bitrate:
                return round(self.bitrate * 1E-6, 4)
        except:
            logger.exception(f"Unexpected error in get_bitrate")
            self.bitrate = None


    def health_check(self):
        """ Checks the current bitrate of the stream and starts or stops the stream accordingly """
        try:
            if self.bitrate is None or self.bitrate < 5000:
                logger.info(f'Restarting stream with low bitrate: {self.bitrate}')
                services.stream.restart()
        except:
            logger.exception('Unexpected error in health_check')


    def poll(self) -> list:
        """
        Returns
        -------
        stream_data: list<xml.etree.ElementTree.Element> or None
            - [<Element 'stream' at 0x107f29310>, <Element 'stream' at 0x107f29db0>]
            - None if an exception or error occurred, the main process will ignore this response
        """
        stream_data = []

        try:
            response = requests.get(url=config.monitor.nginx_stats_url, timeout=5)
            if response.ok:
                root = ElementTree.fromstring(response.content)
                stream_data = root.findall('./server/application/live/stream')
        except requests.exceptions.Timeout:
            logger.error(f"The request to {config.monitor.nginx_stats_url} timed out")
        except Exception:
            logger.exception(f"The request to {config.monitor.nginx_stats_url} failed with exception")

        return stream_data

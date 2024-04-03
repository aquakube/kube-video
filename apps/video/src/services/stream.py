import logging
import threading

from video.gstreamer import GstreamerProcess

from config import config

logger = logging.getLogger(__name__)


class LiveStream(threading.Thread):
    """ Live stream class """

    def __init__(self):
        super().__init__(daemon=True, name=config.video.name)
        self.process = None

    def start(self):
        """ Starts the gstreamer process """
        if self.is_running():
            logger.debug(f"pipeline is already running, skipping start")
            return

        logger.debug(f"starting pipeline")
        self.process = GstreamerProcess(pipeline=config.video.pipeline)
        self.process.start()


    def stop(self):
        """ Stops the gstreamer process """
        if not self.is_running():
            logger.debug(f"pipeline is not running, skipping termination")
            return

        logger.debug(f"stopping pipeline")
        self.process.terminate()
        self.process.join()
        logger.debug(f"sucessfully stopped gstreamer process")
        self.process = None


    def restart(self):
        """ Restarts the gstreamer process """
        self.stop()
        self.start()


    def is_running(self):
        """ Returns True if pipline process is actively running, False otherwise. """
        return self.process is not None and self.process.is_alive()

import os
import logging
import multiprocessing
import time


# pylint: disable=wrong-import-position
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
# pylint: enable=wrong-import-position

Gst.debug_set_active(True)
Gst.debug_set_default_threshold(3)

logger = logging.getLogger()


class GstreamerProcess(multiprocessing.Process):
    """ The gstreamer process. """
    
    def __init__(self, pipeline: str):
        self.pipeline = pipeline
        super().__init__(daemon=True, name='gstreamer')

    def run(self):
        """ The running gstreamer process. """
        Gst.init(None)
        pipeline = Gst.parse_launch(self.pipeline)
        pipeline.set_state(Gst.State.PLAYING)

        try:
            while True:
                time.sleep(0.1)
        except:
            logger.exception(f"Unexpected error in gstreamer process")

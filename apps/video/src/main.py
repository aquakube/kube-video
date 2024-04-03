import time
import logging

import config


if __name__ == '__main__':
    """
    Streamer main entry point
    """

    # initialize the configuration
    config.initialize()

    # configure logging
    logging.basicConfig(level=logging.DEBUG if config.get_config().debug else logging.INFO)
    logger = logging.getLogger()

    # start the services
    import services
    services.start()

    while True:
        logger.debug('main loop')
        time.sleep(100)
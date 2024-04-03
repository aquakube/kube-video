import time
import logging

from kubernetes import config as k8s_config

import config


if __name__ == '__main__':
    """
    This service is responsible for handling events from the event bus and creating/deleting resources in the cluster.
    The video pipelines will be spun up or down based on the events received.
    """

    # initialize the configuration
    config.initialize()

    # configure logging
    logging.basicConfig(level=logging.DEBUG if config.get_config().debug else logging.INFO)
    logger = logging.getLogger()

    # load the kubernetes config
    k8s_config.load_config()

    # start the services
    import services
    services.start()

    try:
        while True:
            time.sleep(60)
            services.scheduler.print_jobs()
    except KeyboardInterrupt:
        services.stop()

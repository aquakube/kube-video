import re

from dataclasses import dataclass


@dataclass(frozen=True)
class VideoConfig:
    """ The Video resource configurations """

    name: str
    """ The name of the Video """

    pipeline: dict
    """ The spec of the Video resource which defines the pipeline"""

    version: str
    """ The application version """


@dataclass(frozen=True)
class KubernetesAttributes:
    """ Defines kubernets attributes for the service producing the metrics """

    pod_uid: str
    """ The UID of the Pod. (e.g '275ecb36-5aa8-4c2a-9c47-d8bb681b9aff') """

    pod_name: str
    """ The name of the Pod. (e.g 'mccp-pod-68bbc4fbfd') """

    namespace: str
    """ The name of the namespace that the pod is running in. (e.g 'video') """


@dataclass(frozen=True)
class FlaskConfig:
    """ The Flask configuration """

    port: int
    """ the port to expose the flask api on """

    host: str = "0.0.0.0"
    """
    the hostname to listen on. 
    defaults to ``'0.0.0.0'`` to have the server available externally
    """


@dataclass(frozen=True)
class MonitorConfig:
    """ The configuration for the monitor service """

    nginx_stats_url: str
    """ The url to retrieve nginx stats """

    startup_delay: int
    """ The delay in seconds before the monitor starts polling stats """

    poll_interval: int
    """ The interval in seconds between polling stats """


@dataclass(frozen=True)
class GlobalConfig:
    """The configuration for the service"""

    debug: bool
    """ Enable for development and debugging tasks """

    k8s: KubernetesAttributes
    """ The kubernetes attributes associated with the service """

    video: VideoConfig
    """ The Video CR configurations """

    flask: FlaskConfig
    """ The flask configurations """

    monitor: MonitorConfig
    """ The monitor configurations """

import os
from distutils.util import strtobool

from util.config import required_env
from models.config import GlobalConfig, VideoConfig, FlaskConfig, KubernetesAttributes, MonitorConfig

config = None


def get_config() -> GlobalConfig:
    return config


def initialize():
    global config

    video_config = VideoConfig(
        name = required_env('NAME'),
        pipeline=required_env('PIPELINE'),
        version=required_env('VERSION'),
    )

    flask_config = FlaskConfig(
        port = int(os.getenv('FLASK_PORT', 5000)),
    )

    k8s_attributes = KubernetesAttributes(
        pod_uid = required_env('KUBERNETES_POD_UID') ,
        pod_name = required_env('KUBERNETES_POD_NAME'),
        namespace = required_env('KUBERNETES_NAMESPACE_NAME')
    )

    monitor_config = MonitorConfig(
        nginx_stats_url = required_env('NGINX_STATS_URL'),
        startup_delay = int(os.getenv('MONITOR_STARTUP_DELAY', 20)),
        poll_interval = int(os.getenv('MONITOR_POLL_INTERVAL', 15)),
    )

    config = GlobalConfig(
        video = video_config,
        flask = flask_config,
        monitor = monitor_config,
        k8s = k8s_attributes,
        debug = strtobool(os.getenv('DEBUG', 'False')),
    )

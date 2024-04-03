import re

from config import config
from utilities.secret import get_secret

def get_rtsp_source(name: str) -> str:
    """
    Creates the rtsp source url for the video pipeline
    """
    device = config.video.devices.get(name)
    if device is None:
        raise Exception(f'Failed to find device {name} in the internal devices config list')

    path = ''
    query_string = ''
    if device['type'] == 'axis':
        path = device.get('path', config.video.default_axis_rtsp_url_path)
        query_string = device.get('query_string', config.video.default_axis_rtsp_url_query_string)
    if device['type'] == 'otaq':
        path = config.video.default_otaq_rtsp_url_path
        query_string = config.video.default_otaq_rtsp_url_query_string
    if device['type'] == 'hikvision':
        path = device.get('path', config.video.default_hikvision_rtsp_url_path)
        query_string = device.get('query_string', config.video.default_hikvision_rtsp_url_query_string)

    username, password = get_secret(name)
    if username and password:
        source = f"rtsp://{username}:{password}@{device['ip']}:554{path}"
    else:
        source = f"rtsp://{device['ip']}:554{path}"

    if query_string:
        source = f"{source}?{query_string}"
    return source


def get_rtmp_sink(name: str) -> str:
    """
    Creates the rtmp sink url for the video pipeline
    """
    return f'{config.video.sink}/{name}'


def get_protocol(name: str) -> str:
    """
    Returns the transport protocol over RTSP for the given camera
    """
    device = config.video.devices.get(name)
    return device.get('protocol', config.video.default_protocol)


def get_pipeline(name: str) -> str:
    """
    Returns the pipeline for the current video
    """
    pipeline = f"""
        rtspsrc location={get_rtsp_source(name)} \
            latency=0 drop-on-latency=true udp-reconnect=true ntp-sync=true \
            do-rtsp-keep-alive=true protocols={get_protocol(name)} timeout=10000000 \
        ! rtph264depay ! h264parse ! flvmux streamable=true \
        ! rtmpsink location={get_rtmp_sink(name)}
    """
    pipeline = re.sub('\s+', ' ', pipeline).strip()
    return pipeline


def get_port(name: str) -> int:
    """
    Returns the port for the current video
    """
    return config.video.devices.get(name)['port']


def get_camera_type(name: str):
    """
    Fetches the camera type for the current video
    """
    return config.video.devices.get(name)['type']


def get_version(name: str):
    """
    Fetches the version for the current video
    """
    return config.video.video_tag
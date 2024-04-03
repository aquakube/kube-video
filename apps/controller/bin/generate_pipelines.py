import os
import re
import yaml
import ast
from typing import List
from enum import Enum, auto

class CameraType(Enum):
    AXIS = auto()
    OTAQ = auto()


def load_config(file):
    """
    Parse the triton config file
    """
    config = None
    with open(file, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError:
            raise Exception(f"Failed to load the YML file '{file}'")
    return config


def get_rtsp_source(name: str) -> str:
    config = load_config("./apps/controller/bin/config.yaml")
    device = config.get(name)
    if device is None:
        raise Exception(f'Failed to find device {name} in config.yml')

    path =''
    query_string = ''
    if device.get('type') == 'axis':
        path = os.getenv("DEFAULT_AXIS_RTSP_URL_PATH")
        query_string = os.getenv("DEFAULT_AXIS_RTSP_URL_QUERY_STRING")
    if device.get('type') == 'otaq':
        path = os.getenv("DEFAULT_OTAQ_RTSP_URL_PATH")
        query_string = os.getenv("DEFAULT_OTAQ_RTSP_URL_QUERY_STRING")

    source = f"rtsp://{device.get('ip')}:554{path}"
    if query_string:
        source = f"{source}?{query_string}"
    return source


def get_rtmp_sink(name: str) -> str:
    base_sink_uri = os.getenv("SINK")
    return f'{base_sink_uri}/{name}'



def generate_pipeline_strings(names: List[str]) -> List[str]:
    """  """
    pipelines = []
    for name in names:
        pipeline = f"""
            rtspsrc location={get_rtsp_source(name)} \
                latency=0 drop-on-latency=true udp-reconnect=true ntp-sync=true \
                do-rtsp-keep-alive=true protocols=udp timeout=10000000 \
            ! rtph264depay ! h264parse ! flvmux streamable=true \
            ! rtmpsink location={get_rtmp_sink(name)}
        """
        pipeline = re.sub('\s+', ' ', pipeline).strip()
        pipelines.append(pipeline)
    return pipelines


if __name__ == '__main__':
    """
    SINK="rtmp://nginx.video.svc.cluster.local:1935/live" \
    DEFAULT_OTAQ_RTSP_URL_PATH="/user=admin&password=tlJwpbo6&channel=1&stream=0.sdp" \
    DEFAULT_AXIS_RTSP_URL_PATH="/axis-media/media.amp" \
    DEFAULT_OTAQ_RTSP_URL_QUERY_STRING="real_stream" \
    DEFAULT_AXIS_RTSP_URL_QUERY_STRING="streamprofile=fo-live-stream-1&camera=1" \
    python3 apps/controller/bin/generate_pipelines.py 
    """
    camera_names = [
        'pty-001-c2-internal',
        'pty-001-c2-bow',
        'pty-001-acc-stern',
        'pty-001-silage-internal',
        'pty-001-silage-starboard',
        'pty-001-silage-bow',
        'pty-001-silage-port',
        'pty-001-mast-bow',
        'pty-001-mast-stern',
        'pty-001-pump-room',
        'pty-001-f2-internal',
        'pty-001-f2-bowl-starboard',
        'pty-001-f2-bowl-port',
        'pty-001-f2-starboard',
        'pty-001-f2-stern',
        'pty-001-f2-port',
        'pty-001-f2-hopper-starboard',
        'pty-001-f2-hopper-port',
        'pty-001-eagle180-01',
        'pty-001-eagle180-02',
        'pty-001-eagle180-03',
        'pty-001-eagle180-04',
        'pty-001-eagle360-01',
        'pty-001-eagle360-02',
    ]
    pipelines = generate_pipeline_strings(camera_names)
    for name, pipeline in zip(camera_names, pipelines):
        print(f'{name}:')
        print(pipeline)
        print()

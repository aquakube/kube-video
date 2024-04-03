import os
import uuid
import json
from distutils.util import strtobool

from utilities.config import required_env, load_schema, convert_to_seconds
from models.config import GlobalConfig, KafkaConfig, EventConfig, Schemas, VideoConfig

config = None


def get_config() -> GlobalConfig:
    return config


def initialize() -> GlobalConfig:
    """
    Initializes the global configuration
    """
    global config

    kafka_config = KafkaConfig(
        brokers = [broker.strip() for broker in required_env('KAFKA_BROKERS').strip().split(',')],
        consume_topic = required_env('KAFKA_CONSUME_TOPIC'),
        consume_client_id = f"{required_env('KAFKA_CONSUME_CLIENT_PREFIX')}{str(uuid.uuid4())}",
        consume_group_id = required_env('KAFKA_CONSUME_GROUP_ID'),
        consume_offset = os.getenv('KAFKA_CONSUME_OFFSET', 'latest')
    )

    event_config = EventConfig(
        teardown_delay = convert_to_seconds(interval=os.getenv('MINIMUM_TEARDOWN_DELAY', '5m')),
        inactivity_threshold = convert_to_seconds(interval=os.getenv('INACTIVITY_THRESHOLD', '10m')),
        reconciliation_interval = convert_to_seconds(interval=os.getenv('RECONCILIATION_INTERVAL', '1m'))
    )

    schemas = Schemas(
        cloudevent = load_schema(file=required_env('CLOUDEVENT_SCHEMA_PATH')),
        aquavid_subscription_event = load_schema(file=required_env('AQUAVID_SUBSCRIPTION_EVENT_SCHEMA_PATH')),
    )

    video_config = VideoConfig(
        sink = required_env('VIDEO_SINK'),
        default_otaq_rtsp_url_path = required_env('DEFAULT_OTAQ_RTSP_URL_PATH'),
        default_axis_rtsp_url_path = required_env('DEFAULT_AXIS_RTSP_URL_PATH'),
        default_otaq_rtsp_url_query_string = required_env('DEFAULT_OTAQ_RTSP_URL_QUERY_STRING'),
        default_axis_rtsp_url_query_string = required_env('DEFAULT_AXIS_RTSP_URL_QUERY_STRING'),
        default_hikvision_rtsp_url_path = required_env('DEFAULT_HIKVISION_RTSP_URL_PATH'),
        default_hikvision_rtsp_url_query_string = os.getenv('DEFAULT_HIKVISION_RTSP_URL_QUERY_STRING'),
        default_protocol = os.getenv('DEFAULT_PROTOCOL', 'udp'),
        devices = json.loads(required_env('CAMERA_MAP')),
        video_tag = required_env('VIDEO_TAG')
    )

    config = GlobalConfig(
        debug = strtobool(os.getenv('DEBUG', 'False')),
        aquavid_url = required_env('AQUAVID_URL'),
        kafka = kafka_config,
        event = event_config,
        schemas = schemas,
        video = video_config
    )

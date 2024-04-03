"""Configuration that can be applicable to multiple models"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class KafkaConfig:
    """ The Kafka configuration """

    brokers: List[str]
    """
    List of kafka broker servers
    """

    consume_topic: str
    """
    List of topics to consume from
    """

    consume_group_id: str
    """
    The group id to assign to the consumer
    """

    consume_client_id: str
    """
    The client id of the consumer
    """

    consume_offset: str
    """
    Either 'latest' or 'earliest' to start consuming from the kafka topic
    A policy for resetting offsets on OffsetOutOfRange errors: 
        - 'earliest' will move to the oldest available message,
        - 'latest' will move to the most recent.
    """


@dataclass(frozen=True)
class EventConfig:
    """ The Event configuration """

    teardown_delay: int
    """
    The time delay (in seconds) the live stream pipeline should teardown after receiving a stop request
    """

    inactivity_threshold: int
    """
    The desired amount of time (in seconds) the main process should stop all pipelines if it has not processed an event
    """

    reconciliation_interval: int
    """
    The desired amount of time (in seconds) the main process should reconcile the state of the cluster with the desired state
    """


@dataclass(frozen=True)
class Schemas:

    cloudevent: dict
    """
    The JSON schema for cloudevent
    """

    aquavid_subscription_event: dict
    """
    The JSON schema for a subscription
    to the aquavid service
    """


@dataclass(frozen=True)
class VideoConfig:

    sink: str
    """
    The rtmp sink url
    """

    default_otaq_rtsp_url_path: str
    """
    The default otaq rtsp url path
    """

    default_axis_rtsp_url_path: str
    """
    The default axis rtsp url path
    """

    default_otaq_rtsp_url_query_string: str
    """
    The default otaq rtsp url query string
    """

    default_axis_rtsp_url_query_string: str
    """
    The default axis rtsp url query string
    """

    default_hikvision_rtsp_url_path: str
    """
    The default hikvision rtsp url path
    """

    default_hikvision_rtsp_url_query_string: str
    """
    The default hikvision rtsp url query string
    """

    default_protocol: str
    """
    The default protocol for the video pipeline. e.g RTSP over UDP or TCP.
    valid values ore 'udp', 'tcp', or 'tcp+udp'
    """

    video_tag: str
    """
    The image tag of the video application that should get deployed by the operator
    """

    devices: dict
    """
    The registerd devices to be used for the video pipeline
    This is loaded from the video controller config map,
    the format should be as follows:
    {
        'koa-002-f2-bowl-port': {
            'ip': 'x.y.z.a',
            'type': 'axis'
        },
    }
    """


@dataclass(frozen=True)
class GlobalConfig:

    debug: bool
    """
    Activate debug logging
    """

    aquavid_url: str
    """
    The aquavid service url
    """

    kafka: Optional[KafkaConfig] = None
    """
    Configurations for the kafka consumer and producer
    """

    event: Optional[EventConfig] = None
    """
    Configurations for handling events
    """

    schemas: Optional[Schemas] = None
    """
    The schemas needed to validate consumed events
    """

    video: Optional[VideoConfig] = None
    """
    Configurations for video pipelines
    """

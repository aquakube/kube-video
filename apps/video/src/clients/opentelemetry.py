import logging

from opentelemetry.sdk.metrics import MeterProvider, Meter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, KUBERNETES_POD_UID, KUBERNETES_POD_NAME, KUBERNETES_NAMESPACE_NAME
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter

from config import config
from util.config import required_env

logger = logging.getLogger()


class OpenTelemetryClient:
    """
    This class is responsible for configuring the OpenTelemetry SDK and API for use in the application.
    Codes against the OpenTelemetry Metrics API to collect telemetry data from the Video pod
    Sends its telemetry to the OpenTelemetry Collector via OTLP.
    """

    def __init__(self):
        """
        configures the OpenTelemetry SDK and API for use in the application
        """

        resource = Resource(
            attributes = {
                SERVICE_NAME: config.video.name,
                KUBERNETES_POD_UID: config.k8s.pod_uid,
                KUBERNETES_POD_NAME: config.k8s.pod_name,
                KUBERNETES_NAMESPACE_NAME: config.k8s.namespace,
            }
        )
        """
        A Resource is an immutable representation of the entity producing telemetry as Attributes.
        In this scenario, a video pipeline process is producing telemetry that is running in a container on Kubernetes,
        it has a Pod, it is in a namespace and possibly is part of a Deployment which also has a name. 
        All three of these attributes can be included in the Resource.
        """

        exporters: list[ConsoleMetricExporter, OTLPMetricExporter] = []
        """
        The exporters are responsible for sending the collected metrics to the configured destination.
        The environment variable OTEL_METRICS_EXPORTER is used to configure one or more exporters.
        """

        if 'console' in required_env('OTEL_METRICS_EXPORTER'):
            exporters.append(ConsoleMetricExporter())
            """
            The console exporter console exporter is useful for development and debugging tasks
            """
            
        if 'otlp' in required_env('OTEL_METRICS_EXPORTER'):
            exporters.append(OTLPMetricExporter())
            """
            This sends data to an OTLP endpoint or the OpenTelemetry Collector according to the environnment variables set.
            endpoint = os.getenv('OTEL_EXPORTER_OTLP_METRICS_ENDPOINT')
            insecure = os.getenv('OTEL_EXPORTER_OTLP_METRICS_INSECURE')
            """

        if not exporters:
            raise Exception("No exporters configured! Please set OTEL_METRICS_EXPORTER to 'console' or 'otlp' or both 'console,otlp'")  

        metric_readers = [
            PeriodicExportingMetricReader(
                exporter = exporter,
            )
            for exporter in exporters
        ]
        """
        The metric readers collect metrics based the configured intervals and timeout set in the environment variables:
        OTEL_METRIC_EXPORT_INTERVAL is the time interval in milliseconds between two consecutive exports for metrics.
        OTEL_METRIC_EXPORT_TIMEOUT is the maximum time in milliseconds to export data
        """

        provider = MeterProvider(
            metric_readers = metric_readers,
            resource = resource,
        )
        """ The MeterProvider is the entry point of the API. It provides access to Meters. """

        self.meter: Meter = provider.get_meter(
            name = config.video.name,
            version = config.video.version,
        )
        
        """
        The meter is responsible for creating instruments which are then used to produce measurements
        """

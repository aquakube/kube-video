import os
import yaml

import kopf
from jinja2 import Template
from kubernetes import client
from kubernetes.client.exceptions import ApiException

from utilities.jinja import load_deployment_template, load_service_template


def deployment(spec, name, namespace):
    """
    Patches the Deployment
    """
    # load the template
    template: Template = load_deployment_template()

    # render the template with the CR's spec and some additional metadata
    # note: do not use the CRs body as an environment variable, the last-applied-configuration causes problems
    rendered_template: str = template.render(
        # PIPELINE is the video pipeline to run
        pipeline=spec.get('pipeline'),
        # NGINX_STATS_URL the nginx url to retrives stats from
        nginx_stats_url = 'http://nginx.video.svc.cluster.local:8080/stat',
        # MONITOR_STARTUP_DELAY the delay in seconds before the monitor starts polling stats
        monitor_startup_delay = 60,
        # MONITOR_POLL_INTERVAL the interval in seconds between polling stats
        monitor_poll_interval = 60,
        # VERSION the app version
        version = spec.get('version'),
        # FLASK_PORT the port the flask app will listen on
        flask_port = spec.get('port'),
        # NAME is the camera / live stream name
        name=name,
        # DEBUG is the debug flag to development or debugging feature like console exporter
        debug = False,
        # OTEL_METRICS_EXPORTER is the exporter to use for metrics. valid values are 'otlp', 'console', or both e.g 'console,otlp'
        otel_metrics_exporter = 'otlp,console',
        # OTEL_METRIC_EXPORT_INTERVAL the time interval in milliseconds between two consecutive exports for metrics.
        otel_exporter_interval = '5000',
        # OTEL_METRIC_EXPORT_TIMEOUT is the maximum time in milliseconds to export data
        otel_exporter_timeout = '2500',
        # OTEL_EXPORTER_OTLP_METRICS_ENDPOINT is the target to which the metric exporter is going to send metrics
        otel_exporter_otlp_metrics_endpoint = os.getenv('OTEL_EXPORTER_OTLP_METRICS_ENDPOINT','telemetry-collector.opentelemetry.svc.cluster.local:4317'),
        # OTEL_EXPORTER_OTLP_METRICS_TIMEOUT is the maximum time the OTLP exporter will wait for each batch export for metrics.
        otel_exporter_otlp_metrics_timeout = '2500',
        # OTEL_EXPORTER_OTLP_METRICS_PROTOCOL represents the the transport protocol for metrics.
        otel_exporter_otlp_metrics_protocol = 'grpc',
        # OTEL_EXPORTER_OTLP_METRICS_INSECURE` represents whether to enable client transport security for gRPC requests for metrics.
        otel_exporter_otlp_metrics_insecure = 'true'
    )

    # convert the rendered template to a dict
    deployment: dict = yaml.safe_load(rendered_template)

    # add the recommended kubernetes labels to the Video CR, Deployment, and Pod
    # note: labels are added to the deployments pod template through the nested parameter
    # https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/
    kopf.label(
        objs=[deployment],
        labels={
            'app.kubernetes.io/name': name,
            'app.kubernetes.io/instance': f"{namespace}.{name}",
            'app.kubernetes.io/version': f"{spec.get('version', 'latest')}",
            'app.kubernetes.io/component': 'video',
            'app.kubernetes.io/part-of': 'foreveroceans',
            'app.kubernetes.io/managed-by': 'video-operator'
        },
        nested='spec.template'
    )

    # add the CR's uid to the pod's owner references.
    kopf.adopt(deployment)

    # create the deployment
    k8s_apps_v1 = client.AppsV1Api()

    k8s_apps_v1.patch_namespaced_deployment(
        name=name,
        namespace=namespace,
        body=deployment,
        
    )


def service(spec, name, namespace, version):
    """
    Patches the Service
    """
    template: Template = load_service_template()
    rendered_template: str = template.render(
        name = name,
        flask_port = spec.get('port'),
    )
    service: dict = yaml.safe_load(rendered_template)
    kopf.label(
        objs=[service],
        labels={
            'app.kubernetes.io/name': name,
            'app.kubernetes.io/instance': f"{namespace}.{name}",
            'app.kubernetes.io/version': version,
            'app.kubernetes.io/component': 'video',
            'app.kubernetes.io/part-of': 'foreveroceans',
            'app.kubernetes.io/managed-by': 'video-operator'
        }
    )
    kopf.adopt(service)
    core_v1_api = client.CoreV1Api()
    core_v1_api.patch_namespaced_service(
        name=name,
        body=service,
        namespace=namespace,
    )


def status(
    name: str,
    is_available: bool,
    group: str = "foreveroceans.io",
    version: str = "v1",
    plural: str = "videos",
    logger=None
):
    """
    Updates the CR's status to reflect availability
    """
    api =   client.CustomObjectsApi()

    try: 
        api.patch_namespaced_custom_object_status(
            group=group,
            version=version,
            namespace='video',
            plural=plural,
            name=name,
            body={ 'status': { 'available': str(is_available) } },
        )
    except ApiException as e:
        logger.exception(f"Failed to update video status")
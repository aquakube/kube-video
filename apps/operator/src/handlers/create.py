import os
import yaml

import kopf
from kubernetes import client
from jinja2 import Template

from utilities.jinja import load_deployment_template, load_service_template


def deployment(spec, namespace, name, logger):
    """
    Creates the Deployment
    """

    # load the template
    template: Template = load_deployment_template()

    # render the template with the CR's spec and some additional metadata
    # note: do not use the CRs body as an environment variable, the last-applied-configuration causes problems

    rendered_template: str = template.render(
        # PIPELINE is the video pipeline to run
        pipeline=spec.get('pipeline'), #.replace('"', "'").replace('\n', ' '),
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

    if not deployment_already_exists(name, namespace, logger):
        k8s_apps_v1.create_namespaced_deployment(
            body=deployment,
            namespace=namespace
        )


def service(spec, name, namespace, logger, version: str):
    """
    Creates the Service
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

    if not service_already_exists(name, namespace, logger):
        core_v1_api.create_namespaced_service(
            body=service,
            namespace=namespace,
        )


def deployment_already_exists(name, namespace, logger) -> bool:
    # create the deployment
    k8s_apps_v1 = client.AppsV1Api()

    api_response = k8s_apps_v1.list_namespaced_deployment(
        namespace,
    )
    for item in api_response.items:
        if item.metadata.name == name:
            logger.info("Found deployment: %s" % item.metadata.name)
            return True
    else:
        return False


def service_already_exists(name, namespace, logger) -> bool:
    # create the deployment
    core_v1_api = client.CoreV1Api()

    api_response = core_v1_api.list_namespaced_service(
        namespace,
    )

    for item in api_response.items:
        if item.metadata.name == name:
            logger.info("Found service: %s" % item.metadata.name)
            return True
    else:
        return False

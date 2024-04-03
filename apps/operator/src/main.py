import kopf

from handlers import create, update


@kopf.on.startup()
def startup(settings, **kwargs):
    """
    Execute this handler when the operator starts.
    No call to the API server is made until this handler
    completes successfully.
    """
    settings.execution.max_workers = 5
    settings.networking.request_timeout = 30
    settings.networking.connect_timeout = 10
    settings.persistence.finalizer = 'video.foreveroceans.io/finalizer'
    settings.persistence.progress_storage = kopf.AnnotationsProgressStorage(prefix='video.foreveroceans.io')
    settings.persistence.diffbase_storage = kopf.AnnotationsDiffBaseStorage(prefix='video.foreveroceans.io')


@kopf.on.cleanup()
def cleanup(logger, **kwargs):
    logger.info("im shutting down. Goodbye!")


@kopf.on.resume('videos.foreveroceans.io')
@kopf.on.create('videos.foreveroceans.io')
def on_create(spec, name, namespace, patch, logger, **kwargs):
    """ Create the Deployment and Service """
    create.deployment(spec, namespace, name, logger)
    create.service(spec, name, namespace, logger, version=spec.get('version', 'latest'))


@kopf.on.update("videos.foreveroceans.io")
def on_update(spec, name, namespace, **kwargs):
    """ Update the Deployment and Service"""
    update.deployment(spec, name, namespace)
    update.service(spec, name, namespace, version=spec.get('version', 'latest'))


@kopf.on.delete("videos.foreveroceans.io")
def on_delete(logger, **kwargs):
    """ Owner reference will delete the deployment and service."""
    logger.info("on_delete videos.foreveroceans.io")


def is_deployment_available(condition) -> bool:
    """ Returns true if the deployment is available, False otherwise """
    return condition["type"] == "Available" and condition["status"] == "True"


@kopf.on.field(
    'deployments',
    field='status.conditions',
    labels={'app.kubernetes.io/managed-by': 'video-operator'},
)
def deployment_status_changed(name, old, new, logger, **kwargs):
    """
    When the deployment status changes, update the CR status if it has changed.
    The deployment status reflects the pod being ready.
    The readiness probe reflects if the live stream is up.
    """
    was_available: bool = any(map(is_deployment_available, old)) if old else None
    is_available: bool = any(map(is_deployment_available, new))

    if was_available != is_available:
        logger.info(f"[video/status] {name} deployment status changed to {is_available}")
        update.status(name, is_available, logger=logger)

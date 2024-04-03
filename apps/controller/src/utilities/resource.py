import logging
import datetime

from kubernetes import client

import services
from config import config
from handlers import create, delete

logger = logging.getLogger()


def does_resource_exist(
    name: str,
    group: str = "foreveroceans.io",
    version: str = "v1",
    namespace: str = "video",
    plural: str = "videos",
):
    """
    Checks if a custom resource exists in a Kubernetes cluster.
    True if it exists, False if it does not exist, and raises an exception if there is an error.
    """

    try:
        api_instance = client.CustomObjectsApi()
        api_instance.get_namespaced_custom_object(group, version, namespace, plural, name)
        return True
    except client.exceptions.ApiException as exception:
        if exception.status == 404:
            return False

        raise exception


def list_managed_resources(
    group: str = "foreveroceans.io",
    version: str = "v1",
    namespace: str = "video",
    plural="videos",
    label_selector: str = "app.kubernetes.io/managed-by=video-controller",
):
    """
    Lists all custom resources that are managed by the video controller.
    """
    api_instance = client.CustomObjectsApi()
    return api_instance.list_namespaced_custom_object(group, version, namespace, plural, label_selector=label_selector)


def create_resource(name: str, check_existence: bool = True):
    """
    Attempts to create a custom resource with the given name if it does not already exist
    param:check_existence: If True, will check if the resource already exists before attempting to create it.
    The reconile loop already hits the kubernetes API to check if the resource exists, so this is an optimization.
    """
    # cancel any pending deletion jobs associated with the resource
    unmark_resource_for_deletion(name)

    # check if the resource already exists
    if check_existence and does_resource_exist(name):
        logger.warn(f'resource already exists for {name}. Skipping create action.')
        return

    # create the resource
    success = create.resource(name)
    if success:
        logger.debug(f'resource {name} has been created!')
    else:
        logger.warn(f'resource {name} failed to be created!')


def mark_resource_for_deletion(name: str):
    """
    Schedules the resource for deletion if it has not already been marked for deletion.
    This time delay on removing video resources should improve UX,
    Users will join and leave video rooms as they navigate around the frontend application
    """
    # do nothing if the resource has already been marked for deletion
    if services.scheduler.get_job(name) is not None:
        return

    # mark the resource for deletion
    deletion_time = datetime.datetime.now() + datetime.timedelta(seconds=config.event.teardown_delay)
    services.scheduler.add_job(
        delete_resource,
        args=[name],
        id=name,
        name=f'Delete {name}',
        trigger='date',
        run_date=deletion_time
    )
    logger.info(f'resource {name} has been marked for deletion @ {deletion_time}')


def unmark_resource_for_deletion(name: str):
    """
    Cancels the deletion job for the resource if it has been marked for deletion.
    """
    # do nothing if the resource has not been marked for deletion
    if services.scheduler.get_job(name) is None:
        return

    # unmark the resource for deletion
    services.scheduler.remove_job(name)
    logger.info(f'resource {name} has been unmarked for deletion')


def delete_resource(name: str):
    """
    Deletes the resource if it exists and removes it from the list of inactive streams.
    """
    # do nothing if the resource does not exist
    if not does_resource_exist(name):
        logger.warn(f'resource {name} does not exists. Skipping delete action.')
        return

    # delete the resource
    delete.resource(name)
    logger.info(f'resource {name} has been deleted')
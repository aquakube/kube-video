import logging
import datetime

from kubernetes import client
from kubernetes.client.exceptions import ApiException

logger = logging.getLogger()


def status(
    name: str,
    group: str = "foreveroceans.io",
    version: str = "v1",
    plural: str = "videos",
):
    """
    Updates the CR's status to reflect the last time it was updated
    """
    api = client.CustomObjectsApi()

    try: 
        api.patch_namespaced_custom_object_status(
            group=group,
            version=version,
            namespace='video',
            plural=plural,
            name=name,
            body={ 'status': { 'lastUpdated': str(datetime.datetime.utcnow()) } },
        )
    except ApiException as e:
        logger.exception(f"Failed to update video status")
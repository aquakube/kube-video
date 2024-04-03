import logging

from kubernetes import client

logger = logging.getLogger()


def resource(
    name: str,
    group: str = "foreveroceans.io",
    version: str = "v1",
    namespace: str = "video",
    plural: str = "videos",
):
    """
    Deletes the CR
    """

    try: 
        api = client.CustomObjectsApi()
        api.delete_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            name=name,
        )
    except Exception:
        logger.exception(f"Failed to delete {name} resource")
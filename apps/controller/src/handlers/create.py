import logging

from kubernetes import client

from utilities import video

logger = logging.getLogger()


def resource(
    name: str,
    group: str = "foreveroceans.io",
    version: str = "v1",
    namespace: str = "video",
    plural: str = "videos",
) -> bool:
    """
    Creates the video resource in the cluster and returns True if successful. False if not.
    """

    try: 
        api = client.CustomObjectsApi()
        api.create_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            body={
                "apiVersion": f"{group}/{version}",
                "kind": "Video",
                "metadata": {
                    "name": name,
                    "labels": {
                        "app.kubernetes.io/name": name,
                        "app.kubernetes.io/instance": f"{namespace}.{name}",
                        "app.kubernetes.io/version": "latest",
                        "app.kubernetes.io/component": "video",
                        "app.kubernetes.io/part-of": "foreveroceans",
                        "app.kubernetes.io/managed-by": "video-controller",
                        "video.foreveroceans.io/type": video.get_camera_type(name),
                    }
                },
                "spec": {
                    "pipeline": video.get_pipeline(name),
                    "port": video.get_port(name),
                    "version": video.get_version(name),
                }
            },
        )
        logger.info(f"Created {name} resource")
        return True
    except Exception:
        logger.exception(f"Failed to create {name} resource")
        return False
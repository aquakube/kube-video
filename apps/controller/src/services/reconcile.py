import logging
import requests

import services
from config import config
from handlers import delete
from utilities import resource as resource_util

logger = logging.getLogger()

def fetch_subscriptions():
    response = requests.get(config.aquavid_url + "/api/subscriptions")
    response.raise_for_status()
    return response.json()


def reconcile():
    """
    Attempts to reconcile the state of the cluster with the desired state,
    this is done by creating any missing resources and deleting any orphaned resource
    """
    try:
        subscriptions = fetch_subscriptions()
        resources = resource_util.list_managed_resources()

        # delete any orphaned resources
        for resource in resources["items"]:
            name = resource["metadata"]["name"]
            if name not in subscriptions:
                logger.warn(f"[Reconciliation] '{name}' is orphaned! deleting...")
                delete.resource(name)

        # create any missing resources
        for name in subscriptions:
            if not resource_util.does_resource_exist(name):
                logger.warn(f"[Reconciliation] '{name}' is missing! creating...")
                resource_util.create_resource(name, check_existence=False)

    except Exception:
        logger.exception("Unexpected error in reconcile")

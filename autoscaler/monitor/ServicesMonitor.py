import time
import logging

from ..models.Service import Service
from kubernetes import client, config

config.load_kube_config()

api_instance = client.CoreV1Api()


def get_all_services():
    api_response = api_instance.list_service_for_all_namespaces()

    services = api_response.items
    services = [Service(service.metadata.name,
                        service.metadata.namespace,
                        service.spec.ports,
                        service.spec.selector) for service in services]

    return services

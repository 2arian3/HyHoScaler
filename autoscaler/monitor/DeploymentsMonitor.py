import time
import logging

from ..models.Deployment import Deployment
from kubernetes import client, config

config.load_kube_config()

api_instance = client.AppsV1Api()


def get_all_deployments():
    api_response = api_instance.list_deployment_for_all_namespaces()
    
    deployments = api_response.items
    deployments = [Deployment(deployment.metadata.name,
                                   deployment.spec.template.spec.containers[0].image,
                                   deployment.spec.replicas,
                                   deployment.spec.template.spec.containers[0].ports,
                                   deployment.spec.template.spec.containers[0].env)
                        for deployment in deployments]
    
    return deployments
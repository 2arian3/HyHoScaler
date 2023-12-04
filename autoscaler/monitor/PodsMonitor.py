import time
import logging

from ..models.Pod import Pod
from kubernetes import client, config
from typing import List

config.load_kube_config()

api_instance = client.CoreV1Api()


def get_all_pods() -> List[Pod]:
    api_response = api_instance.list_pod_for_all_namespaces()

    pods = api_response.items
    pods = [Pod(pod.metadata.name, pod.metadata.namespace, pod.status.phase, pod.status.host_ip, pod.status.pod_ip,
                pod.status.start_time, pod.metadata.labels, pod.spec.containers, pod.spec.node_name, pod.spec.containers[0].resources) for pod in pods]

    return pods


def get_pods_by_service(service) -> List[Pod]:
    api_response = api_instance.list_pod_for_all_namespaces(label_selector=f"app={service}")

    pods = api_response.items
    pods = [Pod(pod.metadata.name, pod.metadata.namespace, pod.status.phase, pod.status.host_ip, pod.status.pod_ip,
                pod.status.start_time, pod.metadata.labels, pod.spec.containers, pod.spec.node_name, pod.spec.containers[0].resource) for pod in pods]

    return pods


def get_pods_by_node(node) -> List[Pod]:
    api_response = api_instance.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node}")

    pods = api_response.items
    pods = [Pod(pod.metadata.name, pod.metadata.namespace, pod.status.phase, pod.status.host_ip, pod.status.pod_ip,
                pod.status.start_time, pod.metadata.labels, pod.spec.containers, pod.spec.node_name, pod.spec.containers[0].resource) for pod in pods]

    return pods 

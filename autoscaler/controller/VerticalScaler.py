from kubernetes import client, config

from ..monitor import PodsMonitor
from ..logger import Logger

config.load_kube_config()


class VerticalScaler:

    NOT_TO_SCALE = ["kubernetes",
                    "kube-system",
                    "kube-public",
                    "loadgenerator",
                    "autoscaler",
                    "default",
                    "coredns",
                    "metrics-server",
                    "local-path-provisioner",
                    "prometheus-kube-prometheus-operator",
                    "prometheus-kube-state-metrics",
                    "prometheus-grafana"]
    

    CPU_RESOURCE_MAPPER = lambda unit: 1 if unit == 'm' else 1000
    MEMORY_RESOURCE_MAPPER = lambda unit: 1 if unit == 'Mi' else 1024

    def __init__(self):
        self.api_instance = client.CoreV1Api()


    def set_pod_resources(self, pod_name, new_cpu=None, new_memory=None, namespace="default") -> None:
        if new_cpu is None and new_memory is None:
            return

        for not_to_scale in self.NOT_TO_SCALE:
            if pod_name.startswith(not_to_scale):
                return
            
        pod = self.api_instance.read_namespaced_pod(name=pod_name, namespace=namespace)

        pod.spec.containers[0].resources = {
            'limits': {'cpu': 1000, 'memory': '1Gi'},
            'requests': {'cpu': '500m', 'memory': '1Gi'}
        }

        self.api_instance.replace_namespaced_pod(name=pod_name, namespace=namespace, body=pod)

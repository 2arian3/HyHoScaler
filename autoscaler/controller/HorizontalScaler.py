from kubernetes import client, config

from ..monitor import DeploymentsMonitor
from ..logger import Logger

config.load_kube_config()


class HorizontalScaler:

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

    def __init__(self):
        self.api_instance = client.AppsV1Api()


    def set_replica_num(self, replicas_number, deployment_name, deployment_ns="default") -> None:
        if deployment_name in HorizontalScaler.NOT_TO_SCALE:
            return

        api_response = self.api_instance.read_namespaced_deployment(deployment_name, deployment_ns)
        Logger.info(f"Deployment {deployment_name} is scaling to {replicas_number} replicas from {api_response.spec.replicas}")
        api_response.spec.replicas = replicas_number
        self.api_instance.patch_namespaced_deployment_scale(deployment_name, deployment_ns, api_response)


    def _default_replicas(self):
        d_monitor = DeploymentsMonitor()
        deployments = d_monitor.get_all_deployments()

        for deployment in deployments:
            if deployment.name in HorizontalScaler.NOT_TO_SCALE:
                continue
            
            print(deployment.name)
            self.set_replica_num(1, deployment.name)

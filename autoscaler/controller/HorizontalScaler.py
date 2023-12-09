from kubernetes import client, config

config.load_kube_config()


class HorizontalScaler:

    NOT_TO_SCALE = ["kubernetes", "kube-system", "kube-public", "loadgenerator", "autoscaler", "default"]

    def __init__(self):
        self.api_instance = client.AppsV1Api()


    def set_replica_num(self, replicas_number, deployment_name, deployment_ns="default") -> None:
        if deployment_name in HorizontalScaler.NOT_TO_SCALE:
            return

        api_response = self.api_instance.read_namespaced_deployment(deployment_name, deployment_ns)
        api_response.spec.replicas = replicas_number
        self.api_instance.patch_namespaced_deployment_scale(deployment_name, deployment_ns, api_response)

from kubernetes import client, config

config.load_kube_config()


class HorizontalScaler:
    def __init__(self):
        self.api_instance = client.AppsV1Api()


    def set_replica_num(self, replicas_number, deployment_name, deployment_ns="default"):
        api_response = self.api_instance.read_namespaced_deployment(deployment_name, deployment_ns)
        api_response.spec.replicas = replicas_number
        self.api_instance.patch_namespaced_deployment_scale(deployment_name, deployment_ns, api_response)

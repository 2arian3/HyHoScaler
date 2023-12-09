from typing import List

from ..models.Pod import Pod, PodCpuUsage, PodCpuRequest
from ..utils.env_vars import PROMETHEUS_URL

from prometheus_api_client import PrometheusConnect
from kubernetes import client, config


config.load_kube_config()


class PodsMonitor:

    def __init__(self):
        self.api_instance = client.CoreV1Api()
        self.prom = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)

    def get_all_pods(self) -> List[Pod]:
        api_response = self.api_instance.list_pod_for_all_namespaces()

        pods = api_response.items
        pods = [Pod(pod.metadata.name, pod.metadata.namespace, pod.status.phase, pod.status.host_ip, pod.status.pod_ip,
                    pod.status.start_time, pod.metadata.labels, pod.spec.containers, pod.spec.node_name, pod.spec.containers[0].resources) for pod in pods]

        return pods

    
    def get_pods_cpu_request(self, namespace="default") -> List[PodCpuRequest]:
        api_response = self.api_instance.list_pod_for_all_namespaces()
        pods = api_response.items

        cpu_requests = []
        for pod in pods:
            if pod.spec.containers[0].resources.requests and 'cpu' in pod.spec.containers[0].resources.requests:
                converted_cpu_request = float(pod.spec.containers[0].resources.requests['cpu'].replace('m', ''))
                cpu_requests.append(PodCpuRequest(pod.metadata.name, converted_cpu_request, pod.metadata.name.split('-')[0], pod.metadata.namespace))
            else:
                cpu_requests.append(PodCpuRequest(pod.metadata.name, None, pod.metadata.name.split('-')[0], pod.metadata.namespace))

        return cpu_requests


    def get_pods_by_service(self, service) -> List[Pod]:
        api_response = self.api_instance.list_pod_for_all_namespaces(label_selector=f"app={service}")

        pods = api_response.items
        pods = [Pod(pod.metadata.name, pod.metadata.namespace, pod.status.phase, pod.status.host_ip, pod.status.pod_ip,
                    pod.status.start_time, pod.metadata.labels, pod.spec.containers, pod.spec.node_name, pod.spec.containers[0].resource) for pod in pods]

        return pods


    def get_pods_by_node(self, node) -> List[Pod]:
        api_response = self.api_instance.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node}")

        pods = api_response.items
        pods = [Pod(pod.metadata.name, pod.metadata.namespace, pod.status.phase, pod.status.host_ip, pod.status.pod_ip,
                    pod.status.start_time, pod.metadata.labels, pod.spec.containers, pod.spec.node_name, pod.spec.containers[0].resource) for pod in pods]

        return pods
    

    def get_pods_cpu_usage(self, deployment_name=None) -> List[PodCpuUsage]:
        if deployment_name:
            query = f'sum(irate(container_cpu_usage_seconds_total{{cluster="", namespace="default", pod=~"{deployment_name}-.*"}}[2m])) by (pod)'
        else:
            query = f'sum(irate(container_cpu_usage_seconds_total{{cluster="", namespace="default"}}[2m])) by (pod)'
        
        query_result = self.prom.custom_query(query=query)
        
        cpu_usages = []
        for result in query_result:
            pod_name = result['metric']['pod']
            cpu_usages.append(PodCpuUsage(pod_name, float(result['value'][1]) * 1000, float(result['value'][0]), pod_name.split('-')[0]))
            
        return cpu_usages

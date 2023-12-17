from typing import List

from ..models.Pod import Pod, PodCpuUsage, PodCpuResource, PodMemoryUsage, PodMemoryResource
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

    
    def get_pods_cpu_resource(self, namespace="default") -> List[PodCpuResource]:
        api_response = self.api_instance.list_pod_for_all_namespaces()
        pods = api_response.items

        cpu_resources = []
        for pod in pods:
            if pod.status.phase != 'Running':
                continue

            if pod.spec.containers[0].resources.requests and 'cpu' in pod.spec.containers[0].resources.requests \
                and pod.spec.containers[0].resources.limits and 'cpu' in pod.spec.containers[0].resources.limits:
                converted_cpu_request = float(pod.spec.containers[0].resources.requests['cpu'].replace('m', ''))
                converted_cpu_limit = float(pod.spec.containers[0].resources.limits['cpu'].replace('m', ''))
                cpu_resources.append(PodCpuResource(pod.metadata.name, converted_cpu_request, converted_cpu_limit, pod.metadata.name.split('-')[0], pod.metadata.namespace))
            else:
                cpu_resources.append(PodCpuResource(pod.metadata.name, 64, 128, pod.metadata.name.split('-')[0], pod.metadata.namespace))

        return cpu_resources
    

    def get_pods_memory_resource(self, namespace="default") -> List[PodMemoryResource]:
        api_response = self.api_instance.list_pod_for_all_namespaces()
        pods = api_response.items

        memory_resources = []
        for pod in pods:
            if pod.status.phase != 'Running':
                continue
    
            if pod.spec.containers[0].resources.requests and 'memory' in pod.spec.containers[0].resources.requests \
                and pod.spec.containers[0].resources.limits and 'memory' in pod.spec.containers[0].resources.limits:
                converted_memory_request = float(pod.spec.containers[0].resources.requests['memory'].replace('Gi', '')) * 1024 if 'Gi' in pod.spec.containers[0].resources.requests['memory'] else float(pod.spec.containers[0].resources.requests['memory'].replace('Mi', ''))
                converted_memory_limit = float(pod.spec.containers[0].resources.limits['memory'].replace('Gi', '')) * 1024 if 'Gi' in pod.spec.containers[0].resources.requests['memory'] else float(pod.spec.containers[0].resources.requests['memory'].replace('Mi', ''))
                memory_resources.append(PodMemoryResource(pod.metadata.name, converted_memory_request, converted_memory_limit, pod.metadata.name.split('-')[0], pod.metadata.namespace))
            else:
                memory_resources.append(PodMemoryResource(pod.metadata.name, 100, 200, pod.metadata.name.split('-')[0], pod.metadata.namespace))

        return memory_resources


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
            query = f'sum(irate(container_cpu_usage_seconds_total{{cluster="", namespace="default", pod=~"{deployment_name}-.*"}}[1m])) by (pod)'
        else:
            query = f'sum(irate(container_cpu_usage_seconds_total{{cluster="", namespace="default"}}[1m])) by (pod)'
        
        query_result = self.prom.custom_query(query=query)
        
        cpu_usages = []
        for result in query_result:
            pod_name = result['metric']['pod']
            cpu_usages.append(PodCpuUsage(pod_name, float(result['value'][1]) * 1000, float(result['value'][0]), pod_name.split('-')[0]))
            
        return cpu_usages
    

    def get_pods_memory_usage(self, deployment_name=None) -> List[PodMemoryUsage]:
        if deployment_name:
            query = f'sum(container_memory_usage_bytes{{cluster="", namespace="default", pod=~"{deployment_name}-.*"}}) by (pod)'
        else:
            query = f'sum(container_memory_usage_bytes{{cluster="", namespace="default"}}) by (pod)'
        
        query_result = self.prom.custom_query(query=query)
        
        memory_usages = []
        for result in query_result:
            pod_name = result['metric']['pod']
            memory_usages.append(PodMemoryUsage(pod_name, float(result['value'][1]) / 1024 / 1024, float(result['value'][0]) / 1024 / 1024, pod_name.split('-')[0]))
            
        return memory_usages

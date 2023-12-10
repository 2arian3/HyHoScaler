from typing import List, Dict

from ..utils.env_vars import PROMETHEUS_URL
from ..models.Deployment import (Deployment, 
                                DeploymentAverageCpuUsage,
                                DeploymentAverageMemoryUsage)

from kubernetes import client, config
from prometheus_api_client import PrometheusConnect

config.load_kube_config()


api_instance = client.AppsV1Api()


class DeploymentsMonitor:
    
    def __init__(self):
        self.api_instance = client.AppsV1Api()
        self.prom = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True) # make sure to disable SSL verification in case of self signed certificates


    def get_all_deployments(self) -> List[Deployment]:
        api_response = api_instance.list_deployment_for_all_namespaces()
        
        deployments = api_response.items
        deployments = [Deployment(deployment.metadata.name,
                                    deployment.spec.template.spec.containers[0].image,
                                    deployment.status.replicas,
                                    deployment.status.ready_replicas,
                                    float(deployment.spec.template.spec.containers[0].resources.requests['cpu'].replace('m', '')) if deployment.spec.template.spec.containers[0].resources.requests and 'cpu' in deployment.spec.template.spec.containers[0].resources.requests else None,
                                    float(deployment.spec.template.spec.containers[0].resources.requests['memory'].replace('Mi', '')) if deployment.spec.template.spec.containers[0].resources.requests and 'memory' in deployment.spec.template.spec.containers[0].resources.requests else None,
                                    float(deployment.spec.template.spec.containers[0].resources.limits['cpu'].replace('m', '')) if deployment.spec.template.spec.containers[0].resources.limits and 'cpu' in deployment.spec.template.spec.containers[0].resources.limits else None,
                                    float(deployment.spec.template.spec.containers[0].resources.limits['memory'].replace('Mi', '')) if deployment.spec.template.spec.containers[0].resources.limits and 'memory' in deployment.spec.template.spec.containers[0].resources.limits else None,
                                    deployment.spec.template.spec.containers[0].ports,
                                    deployment.spec.template.spec.containers[0].env)
                            for deployment in deployments]
        
        return deployments
    

    def get_deployments_average_memory_usage(self) -> Dict[str, DeploymentAverageMemoryUsage]:
        query = """
                sum(
                (container_memory_usage_bytes{cluster="", namespace="default"})
                * on(namespace,pod)
                group_left(workload, workload_type) namespace_workload_pod:kube_pod_owner:relabel{cluster="", namespace="default"}
                ) by (workload, workload_type)
                """
        
        deployments = self.get_all_deployments()

        query_result = self.prom.custom_query(query=query)
        query_result = {q['metric']['workload']: [float(q['value'][1]) / (1024 ** 2), float(q['value'][0])] for q in query_result} # Convert B to Mi
        average_memory_usages = {}
        
        for deployment in deployments:
            deployment_name = deployment.name
            if deployment_name in query_result:
                average_memory_usages[deployment_name] = DeploymentAverageMemoryUsage(deployment_name, query_result[deployment_name][0], deployment.ready_replicas, query_result[deployment_name][1])

        return average_memory_usages


    def get_deployments_average_cpu_usage(self) -> Dict[str, DeploymentAverageCpuUsage]:
        query = """
                sum(
                irate(container_cpu_usage_seconds_total{cluster="", namespace="default"}[2m])
                * on(namespace,pod)
                group_left(workload, workload_type) namespace_workload_pod:kube_pod_owner:relabel{cluster="", namespace="default", workload_type="deployment"}
                ) by (workload, workload_type)
                """
        
        deployments = self.get_all_deployments()

        query_result = self.prom.custom_query(query=query)
        query_result = {q['metric']['workload']: [float(q['value'][1])*1000, float(q['value'][0])] for q in query_result}
        average_cpu_usages = {}

        for deployment in deployments:
            deployment_name = deployment.name
            if deployment_name in query_result:
                average_cpu_usages[deployment_name] = DeploymentAverageCpuUsage(deployment_name, query_result[deployment_name][0], deployment.ready_replicas, query_result[deployment_name][1])

        return average_cpu_usages
from typing import List, Dict

from ..utils.env_vars import PROMETHEUS_URL
from ..models.Deployment import (Deployment, 
                                DeploymentAverageCpuUsage,
                                DeploymentAverageMemoryUsage)
from ..models.Pod import (PodCpuUsage,
                          PodCpuResource,
                          PodMemoryUsage,
                          PodMemoryResource)

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
    

    def _get_pod_count(self, deployment_name) -> Dict[str, int]:
        query = """count(kube_pod_info{namespace="default"}
                            ) by (created_by_kind,created_by_name)"""
        
        query_result = self.prom.custom_query(query=query)
        
        filtered_res = [{
                        'name': q['metric']['created_by_name'],
                        'count': int(q['value'][1]),
                        } for q in query_result]

        for res in filtered_res:
            if res['name'].startswith(deployment_name):
                return res['count']
        # if not found, return None
        return None
    

    def get_all_deployments_pod_count(self) -> Dict[str, int]:
        deployments = self.get_all_deployments()
        return {deployment.name: self._get_pod_count(deployment.name) for deployment in deployments}
    

    def get_all_deployment_kubernetes_count(self) -> Dict[str, int]:
        result = {}
        deploy_list = self.get_all_deployments()
        for d in deploy_list:
            result[d.name + '_ordered'] = d.replicas
            result[d.name + '_ready'] = d.ready_replicas
        return result
    

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
                irate(container_cpu_usage_seconds_total{cluster="", namespace="default"}[1m])
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


    def get_deployments_total_cpu_usage(self) -> Dict[str, float]:
        query = """
                sum(
                irate(container_cpu_usage_seconds_total{cluster="", namespace="default"}[1m])
                * on(namespace,pod)
                group_left(workload, workload_type) namespace_workload_pod:kube_pod_owner:relabel{cluster="", namespace="default", workload_type="deployment"}
                ) by (workload, workload_type)
                """
        
        deployments = self.get_all_deployments()

        query_result = self.prom.custom_query(query=query)
        query_result = {q['metric']['workload']: [float(q['value'][1])*1000, float(q['value'][0])] for q in query_result}

        for d in deployments:
            if d.name not in query_result:
                query_result[d.name] = None

        return query_result
    

    def get_deployments_total_cpu_utilization(self, pods_cpu_usage: List[PodCpuUsage], pods_cpu_request: List[PodCpuResource]) -> Dict[str, float]:
        deployments = self.get_all_deployments()

        total_cpu_utilization = {deployment.name: 0 for deployment in deployments}

        for deployment in deployments:
            pods_u = filter(lambda pod: deployment.name in pod.name, pods_cpu_usage)
            pods_r = filter(lambda pod: deployment.name in pod.name, pods_cpu_request)

            pods_u = {pod.name: pod.cpu_usage for pod in pods_u}
            pods_r = {pod.name: pod.cpu_request for pod in pods_r}

            for name in pods_u:
                if name in pods_r:
                    total_cpu_utilization[deployment.name] += pods_u[name] / pods_r[name]
        
        total_cpu_utilization = dict(filter(lambda deployment: deployment[1] > 0, total_cpu_utilization.items()))

        return total_cpu_utilization
    

    def get_deployments_total_memory_utilization(self, pods_memory_usage: List[PodMemoryUsage], pods_memory_request: List[PodMemoryResource]) -> Dict[str, float]:
        deployments = self.get_all_deployments()

        total_memory_utilization = {deployment.name: 0 for deployment in deployments}

        for deployment in deployments:
            pods_u = filter(lambda pod: deployment.name in pod.name, pods_memory_usage)
            pods_r = filter(lambda pod: deployment.name in pod.name, pods_memory_request)

            pods_u = {pod.name: pod.memory_usage for pod in pods_u}
            pods_r = {pod.name: pod.memory_request for pod in pods_r}

            for name in pods_u:
                if name in pods_r:
                    total_memory_utilization[deployment.name] += pods_u[name] / pods_r[name]
        
        total_memory_utilization = dict(filter(lambda deployment: deployment[1] > 0, total_memory_utilization.items()))

        return total_memory_utilization
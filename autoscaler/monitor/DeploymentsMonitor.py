import time
import logging
from typing import List, Dict

from ..utils.env_vars import PROMETHEUS_URL
from ..models.Deployment import Deployment

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
                                    deployment.spec.replicas,
                                    deployment.spec.template.spec.containers[0].ports,
                                    deployment.spec.template.spec.containers[0].env)
                            for deployment in deployments]
        
        return deployments
    

    def _extract_pod_count_from_query_result(self, query_result, deployment_name) -> int:
        for res in query_result:
            if res['name'].startswith(deployment_name):
                return res['count']
        # if not found, return None
        return None
    

    def get_pods_count_by_deployment(self, deployment_name, namespace="default") -> int:
        query = f"sum(kube_pod_info{{namespace='{namespace}'}}) by (created_by_kind,created_by_name)"
        query_result = self.prom.custom_query(query=query)

        query_result = [{'name': q['metric']['created_by_name'],'count': int(q['value'][1])} for q in query_result]

        return self._extract_pod_count_from_query_result(query_result, deployment_name)
    

    def get_all_deployment_pod_counts(self, namespace="default") -> Dict[str, int]:
        query = f"sum(kube_pod_info{{namespace='{namespace}'}}) by (created_by_kind,created_by_name)"
        query_result = self.prom.custom_query(query=query)

        query_result = [{'name': q['metric']['created_by_name'],'count': int(q['value'][1])} for q in query_result]

        deployments = [deployment.name for deployment in self.get_all_deployments()]

        deploy_pod_counts = {}
        for d in deployments:
            deploy_pod_counts[d] = self._extract_pod_count_from_query_result(query_result, d)

        return deploy_pod_counts
    

    def get_all_deployments_cpu_usage(self) -> Dict[str, float]:
        query = """
                sum(
                irate(container_cpu_usage_seconds_total{cluster="", namespace="default"}[2m])
                * on(namespace,pod)
                group_left(workload, workload_type) namespace_workload_pod:kube_pod_owner:relabel{cluster="", namespace="default", workload_type="deployment"}
                ) by (workload, workload_type)
                """
        
        deployments = [deployment.name for deployment in self.get_all_deployments()]

        wl_cpu_res = self.prom.custom_query(query=query)
        # filter results (unit is millicores)
        filtered_cpu_query = { q['metric']['workload']: float(q['value'][1])*1000 for q in wl_cpu_res if q['metric']['workload'] in deployments}
        # if metric skipped, put in None instead
        for d in deployments:
            if d not in filtered_cpu_query:
                filtered_cpu_query[d] = None
        return filtered_cpu_query

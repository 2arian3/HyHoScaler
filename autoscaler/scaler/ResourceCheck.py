from ..controller import HorizontalScaler
from ..monitor import PodsMonitor, DeploymentsMonitor
from ..logger import Logger
from ..utils.constants import (
    SCALING_IN_CPU_THRESHOLD,
    SCALING_OUT_CPU_THRESHOLD,
    SCALING_IN_MEMORY_THRESHOLD,
    SCALING_OUT_MEMORY_THRESHOLD,
    PING_PONG_EFFECT_THRESHOLD
)

import math
from typing import Set


scaler = HorizontalScaler()

'''
Implementing the base rule-based autoscaler for the CPU usage metric.
'''
def check_deployments_cpu_usage(not_to_check=set()) -> Set[str]:
    Logger.info("Checking deployments CPU usage")

    scaled_deploys = set()

    d_monitor = DeploymentsMonitor()
    p_monitor = PodsMonitor()

    deployments = d_monitor.get_all_deployments()
    
    pods_u = p_monitor.get_pods_cpu_usage()
    pods_r = p_monitor.get_pods_cpu_resource()

    deployments_utilization = d_monitor.get_deployments_total_cpu_utilization(pods_u, pods_r)

    for deployment in deployments:
        if deployment.name in not_to_check:
            continue

        if deployment.name in deployments_utilization:
            required_replicas = math.ceil(deployments_utilization[deployment.name] / SCALING_OUT_CPU_THRESHOLD)

            if required_replicas > deployment.ready_replicas:
                Logger.warning(f"Required replicas for deployment {deployment.name} is {required_replicas} which is higher than {SCALING_OUT_CPU_THRESHOLD}")
                scaler.set_replica_num(required_replicas, deployment.name)
                scaled_deploys.add(deployment.name)

    return scaled_deploys


def check_deployments_memory_usage(not_to_check=set()) -> Set[str]:
    Logger.info("Checking deployments memory usage")

    scaled_deploys = set()

    d_monitor = DeploymentsMonitor()
    p_monitor = PodsMonitor()

    deployments = d_monitor.get_all_deployments()
    
    pods_u = p_monitor.get_pods_memory_usage()
    pods_r = p_monitor.get_pods_memory_resource()

    deployments_utilization = d_monitor.get_deployments_total_memory_utilization(pods_u, pods_r)

    for deployment in deployments:
        if deployment.name in not_to_check:
            continue

        if deployment.name in deployments_utilization:
            required_replicas = math.ceil(deployments_utilization[deployment.name] / SCALING_OUT_MEMORY_THRESHOLD)

            if required_replicas > deployment.ready_replicas:
                Logger.warning(f"Required replicas for deployment {deployment.name} is {required_replicas} which is higher than {SCALING_OUT_MEMORY_THRESHOLD}")
                scaler.set_replica_num(required_replicas, deployment.name)
                scaled_deploys.add(deployment.name)

    return scaled_deploys
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


scaler = HorizontalScaler()

'''
Implementing the base rule-based autoscaler for the CPU usage metric.
'''
def check_deployments_cpu_usage():
    Logger.info("Checking deployments CPU usage")

    d_monitor = DeploymentsMonitor()
    p_monitor = PodsMonitor()
    deployments = d_monitor.get_all_deployments()
    
    pods_u = p_monitor.get_pods_cpu_usage()
    pods_r = p_monitor.get_pods_cpu_resource()

    deployments_utilization = d_monitor.get_deployments_total_cpu_utilization(pods_u, pods_r)
    deployments_cpu_usage = d_monitor.get_deployments_average_cpu_usage()

    for deployment in deployments:
        if deployment.name in deployments_utilization:
            required_replicas = math.ceil(deployments_utilization[deployment.name] / SCALING_OUT_CPU_THRESHOLD)
            deployment_cpu_usage = deployments_cpu_usage[deployment.name].average_cpu_usage
            print(deployment.name, deployments_utilization[deployment.name], deployment_cpu_usage / 1000, required_replicas)
            if required_replicas > deployment.ready_replicas:
                if abs((deployment_cpu_usage / 1000) / SCALING_OUT_CPU_THRESHOLD - 1) > PING_PONG_EFFECT_THRESHOLD:
                    Logger.warning(f"Required replicas for deployment {deployment.name} is {required_replicas} which is higher than {SCALING_OUT_CPU_THRESHOLD}")
                    scaler.set_replica_num(required_replicas, deployment.name)


def check_deployments_memory_usage():
    Logger.info("Checking deployments memory usage")

    d_monitor = DeploymentsMonitor()
    deployments = d_monitor.get_all_deployments()
    deployments_memory_usage = d_monitor.get_deployments_average_memory_usage()

    for deployment in deployments:
        if deployment.name in deployments_memory_usage:
            memory_usage = deployments_memory_usage[deployment.name].average_memory_usage
            if (memory_usage / deployment.memory_limit) > SCALING_OUT_MEMORY_THRESHOLD:
                # Avoiding ping-pong effect
                if abs(memory_usage / deployment.memory_limit - 1) > PING_PONG_EFFECT_THRESHOLD:
                    Logger.warning(f"Memory usage of deployment {deployment.name} is {memory_usage} which is higher than {SCALING_OUT_MEMORY_THRESHOLD}")
                    scaler.set_replica_num(deployment.ready_replicas + 1, deployment.name)
            elif (memory_usage / deployment.memory_limit) < SCALING_IN_MEMORY_THRESHOLD:
                if deployment.ready_replicas <= 1:
                    continue

                # if abs(cpu_usage / deployment.cpu_limit - 1) > PING_PONG_EFFECT_THRESHOLD:
                #     Logger.warning(f"CPU usage of deployment {deployment.name} is {cpu_usage} which is lower than {SCALING_IN_CPU_THRESHOLD}")
                #     scaler.set_replica_num(deployment.ready_replicas + 1, deployment.name)
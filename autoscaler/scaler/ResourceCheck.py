from ..controller import HorizontalScaler
from ..monitor import PodsMonitor, DeploymentsMonitor
from ..logger import Logger


def check_deployments_cpu_usage():
    # Logger.info("Checking deployments CPU usage")

    d_monitor = DeploymentsMonitor()
    deployments = d_monitor.get_all_deployments()
    deployments_cpu_usage = d_monitor.get_deployments_average_cpu_usage()

    for deployment in deployments:
        if deployment.name in deployments_cpu_usage:
            print(deployment.name, deployment.cpu_limit, deployment.cpu_request, deployments_cpu_usage[deployment.name])
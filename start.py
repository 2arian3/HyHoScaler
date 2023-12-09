from autoscaler.monitor import *

if __name__ == '__main__':
    p_monitor = PodsMonitor()
    d_monitor = DeploymentsMonitor()

    print(d_monitor.get_deployments_average_cpu_usage())
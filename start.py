from autoscaler.monitor import *

if __name__ == '__main__':
    p_monitor = PodsMonitor()

    print(p_monitor.get_pods_cpu_usage())
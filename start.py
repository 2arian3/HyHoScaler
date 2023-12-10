from autoscaler.monitor import *
from autoscaler.scaler import *
from autoscaler.controller import *
from autoscaler.logger import Logger

import time


if __name__ == '__main__':
    # HorizontalScaler()._default_replicas()

    while True:
        print(DeploymentsMonitor().get_deployments_average_cpu_usage())
        check_deployments_cpu_usage()
        check_deployments_memory_usage()
        time.sleep(15)
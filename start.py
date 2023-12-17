from autoscaler.monitor import *
from autoscaler.scaler import *
from autoscaler.controller import *

import loader.load_test as load_test

import time


if __name__ == '__main__':
    # HorizontalScaler()._default_replicas()

    load_test.start()

    # while True:
    #     print(DeploymentsMonitor().get_deployments_average_cpu_usage())
    #     check_deployments_cpu_usage()
    #     time.sleep(30)
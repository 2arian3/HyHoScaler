import time

from .monitor import *
from .scaler import *
from .controller import *


def initialize_autoscaler():

    while True:
        print(DeploymentsMonitor().get_deployments_average_cpu_usage())
        check_deployments_cpu_usage()
        time.sleep(30)
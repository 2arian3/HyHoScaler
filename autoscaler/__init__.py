import time

from .monitor import *
from .scaler import *
from .controller import *


def initialize_autoscaler():

    while True:
        scaled_deploys = check_deployments_cpu_usage()
        scaled_deploys = check_deployments_memory_usage(scaled_deploys)
        time.sleep(30)
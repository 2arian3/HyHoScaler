import time

from .monitor import *
from .scaler import *
from .controller import *

from .utils.constants import QUERY_INTERVAL


def initialize_autoscaler():

    while True:
        scaled_deploys = check_deployments_cpu_usage()
        scaled_deploys = check_deployments_memory_usage(scaled_deploys)
        time.sleep(QUERY_INTERVAL)
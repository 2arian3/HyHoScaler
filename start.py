from autoscaler.monitor import *
from autoscaler.scaler import *
from autoscaler.controller import *
from autoscaler.logger import Logger


if __name__ == '__main__':
    check_deployments_cpu_usage()
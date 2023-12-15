class Pod:

    def __init__(self, name, namespace, status, host_ip, pod_ip, start_time, labels, containers, node_name, resources):
        self.name = name
        self.namespace = namespace
        self.status = status
        self.host_ip = host_ip
        self.pod_ip = pod_ip
        self.start_time = start_time
        self.labels = labels
        self.containers = containers
        self.node_name = node_name
        self.resources = resources


    def __repr__(self) -> str:
        return f"Pod(name={self.name}, namespace={self.namespace}, status={self.status}, host_ip={self.host_ip}, " \
               f"pod_ip={self.pod_ip}, start_time={self.start_time}, labels={self.labels}, containers={self.containers}, " \
               f"node_name={self.node_name}, resources={self.resources})"


class PodCpuUsage:

    def __init__(self, name, cpu_usage, captured_time, deployment, namespace="default"):
        self.name = name
        self.cpu_usage = cpu_usage # in millicores
        self.captured_time = captured_time
        self.deployment = deployment
        self.namespace = namespace
    

    def __repr__(self) -> str:
        return f"PodCpuUsage(name={self.name}, deployment={self.deployment}, cpu_usage={self.cpu_usage}, captured_time={self.captured_time}"


class PodCpuResource:

    def __init__(self, name, cpu_request, cpu_limit, deployment, namespace="default"):
        self.name = name
        self.cpu_request = cpu_request # in millicores
        self.cpu_limit = cpu_limit # in millicores
        self.deployment = deployment
        self.namespace = namespace
    

    def __repr__(self) -> str:
        return f"PodCpuResource(name={self.name}, deployment={self.deployment}, cpu_request={self.cpu_request}, cpu_limit={self.cpu_limit}"
    

class PodMemoryResource:

    def __init__(self, name, memory_request, memory_limit, deployment, namespace="default"):
        self.name = name
        self.memory_request = memory_request # in Mi
        self.memory_limit = memory_limit # in Mi
        self.deployment = deployment
        self.namespace = namespace
    

    def __repr__(self) -> str:
        return f"PodMemoryResource(name={self.name}, deployment={self.deployment}, memory_request={self.memory_request}, memory_limit={self.memory_limit}"
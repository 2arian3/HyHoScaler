class Deployment:

    def __init__(self, name, image, replicas, ready_replicas, cpu_request, memory_request, cpu_limit, memory_limit, ports, env):
        self.name = name
        self.image = image
        self.replicas = replicas
        self.ready_replicas = ready_replicas
        self.cpu_limit = cpu_limit # in millicores
        self.memory_limit = memory_limit
        self.cpu_request = cpu_request # in millicores
        self.memory_request = memory_request
        self.ports = ports
        self.env = env

    
    def __repr__(self) -> str:
        return f"Deployment(name={self.name}, replicas={self.replicas}, ready_replicas={self.ready_replicas}, cpu_request={self.cpu_request}, memory_request={self.memory_request}, cpu_limit={self.cpu_limit}, memory_limit={self.memory_limit})"
    

class DeploymentAverageCpuUsage:

    def __init__(self, name, total_cpu_usage, replicas, captured_time, namespace="default"):
        self.name = name
        self.average_cpu_usage = total_cpu_usage / replicas # in millicores
        self.replicas = replicas
        self.captured_time = captured_time
        self.namespace = namespace
    
    def __repr__(self) -> str:
        return f"DeploymentAverageCpuUsage(name={self.name}, average_cpu_usage={self.average_cpu_usage}, captured_time={self.captured_time})"
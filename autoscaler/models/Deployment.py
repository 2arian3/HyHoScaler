class Deployment:

    def __init__(self, name, image, replicas, ready_replicas, ports, env):
        self.name = name
        self.image = image
        self.replicas = replicas
        self.ready_replicas = ready_replicas
        self.ports = ports
        self.env = env

    
    def __repr__(self) -> str:
        return f"Deployment(name={self.name}, replicas={self.replicas}, ready_replicas={self.ready_replicas})"
    

class DeploymentAverageCpuUsage:

    def __init__(self, name, total_cpu_usage, replicas, captured_time, namespace="default"):
        self.name = name
        self.average_cpu_usage = total_cpu_usage / replicas # in millicores
        self.replicas = replicas
        self.captured_time = captured_time
        self.namespace = namespace
    
    def __repr__(self) -> str:
        return f"DeploymentAverageCpuUsage(name={self.name}, average_cpu_usage={self.average_cpu_usage}, captured_time={self.captured_time})"
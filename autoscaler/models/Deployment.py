class Deployment:

    def __init__(self, name, image, replicas, ports, env):
        self.name = name
        self.image = image
        self.replicas = replicas
        self.ports = ports
        self.env = env

    
    def __repr__(self) -> str:
        return f"Deployment(name={self.name}, image={self.image}, replicas={self.replicas}, ports={self.ports}, env={self.env})"
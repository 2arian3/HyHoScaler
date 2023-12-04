class Service:

    def __init__(self, name, namespace, ports, selector):
        self.name = name
        self.namespace = namespace
        self.ports = ports
        self.selector = selector

    
    def __repr__(self) -> str:
        return f"Service(name={self.name}, namespace={self.namespace}, ports={self.ports}, selector={self.selector})"
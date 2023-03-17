
from collections import defaultdict


class Registry:
    def __init__(self):
        self.registry = {}

    def register(self, name, item):
        self.registry[name] = item

    def items(self):
        return self.registry.items()


mvt_registry = Registry()
cluster_registry = Registry()
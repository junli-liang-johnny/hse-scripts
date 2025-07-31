from rdflib import Graph
from .namespace import void

class VoidDump:
    def __init__(self, input_graph: Graph):
        self.input_graph = input_graph

    def parse(self):
        if self.input_graph is None:
            return []

        void_dumps = self.input_graph.subjects(object=void.VoidDump)

        return void_dumps

    def find(self, void_dump) -> str:
        return self.input_graph.value(void_dump, predicate=void.dataDump)
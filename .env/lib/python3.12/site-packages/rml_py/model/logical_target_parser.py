from rdflib import Graph
from .namespace import rmlt, rml
from .void_dump import VoidDump
from sys import exit

class LogicalTargetParser:
    def __init__(self, input_graph: Graph):
        self.input_graph = input_graph

    def parse(self, predicate_object_map):
        try:
            logical_target_object = list(self.input_graph.objects(subject=predicate_object_map, predicate=rml.logicalTarget))[0]
        except IndexError:
            print("No logical target found in the predicate object map: ", predicate_object_map)
            exit(1)

        if logical_target_object is None:
            return (None, None, None, None)

        target = self.input_graph.value(logical_target_object, predicate=rmlt.target)

        if target is None:
            return (None, None, None, None)

        data_dump = VoidDump(self.input_graph).find(target)

        seriliazation = self.input_graph.value(logical_target_object, predicate=rmlt.serialization)

        return logical_target_object, target, seriliazation, data_dump
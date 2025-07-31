from ..namespace import rr, rml
from rdflib import Graph

class PredicateObjectMapParser:
	def __init__(self, input_graph: Graph):
		self.input_graph = input_graph

	def parse(self, predicate_object_map) -> tuple:
		if self.input_graph is None:
			return None, None, None, None
		predicate_list = list(self.input_graph.objects(predicate_object_map, predicate=rr.predicate))
		object_map = self.input_graph.value(predicate_object_map, predicate=rr.objectMap)
		object_list = list(self.input_graph.objects(predicate_object_map, predicate=rr.object))
		logical_target = self.input_graph.value(predicate_object_map, predicate=rml.logicalTarget)

		return predicate_list, object_map, object_list, logical_target
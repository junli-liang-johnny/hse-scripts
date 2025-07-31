from rml_py.model.rml.object_map_parser import ObjectMapParser
from rml_py.model.namespace import rmlpy

class SubjectObjectMapParser(ObjectMapParser):
	def __init__(self, graph):
		super().__init__(graph)

	def parse(self, object_map):
		reference, obj, language, datatype, split_by, template = super().parse(object_map)

		_reference = self.graph.value(object_map, rmlpy.reference)

		return _reference, obj, language, datatype, split_by, template
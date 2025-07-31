from ..namespace import rr, rml, rmlpy

class ObjectMapParser:
	def __init__(self, graph):
		self.graph = graph

	def parse(self, object_map):
		reference = self.graph.value(object_map, rml.reference)
		obj = self.graph.value(object_map, rmlpy.object)
		language = self.graph.value(object_map, rr.language)
		datatype = self.graph.value(object_map, rr.datatype)
		split_by = self.graph.value(object_map, rmlpy.splitBy)
		template = self.graph.value(object_map, rr.template)

		return reference, obj, language, datatype, split_by, template
from ..namespace import rr, rml, rmlpy
from rdflib import Graph
from ..core.subject_object_map_parser import SubjectObjectMapParser
from sys import exit

class SubjectMapParser:
	def __init__(self, graph: Graph):
		self.graph = graph

	def parse(self, subject_map):
		template = self.graph.value(subject_map, rr.template)
		logical_target = self.graph.value(subject_map, predicate=rml.logicalTarget)
		rdf_class, reference, split_by = self._rdf_class(subject_map)

		return template, {"rdf_class": rdf_class, "rdf_class_ref": reference, "split_by": split_by}, logical_target

	def _rdf_class(self, subject_map):
		if self.graph.value(subject_map, rr['class']) is not None:
			return list(self.graph.objects(subject_map, rr['class'])), None, None

		subject_object_map = self.graph.value(subject_map, rmlpy.subjectObjectMap)
		subject_object_map_parser = SubjectObjectMapParser(self.graph)
		reference, obj, language, datatype, split_by, _template = subject_object_map_parser.parse(subject_object_map)

		if split_by is not None:
			return None, reference, split_by

		if reference is not None:
			return None, reference, None

		else:
			print("SubjectMapParser._rdf_class: No class found in the configuration file.")
			exit(1)


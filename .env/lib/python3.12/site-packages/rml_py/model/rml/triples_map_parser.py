from ..namespace import rr

class TriplesMapParser:
	def __init__(self, graph):
		self.graph = graph

	def subjects(self) -> list:
		return list(self.graph.subjects(object=rr.TriplesMap))
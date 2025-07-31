
from rdflib import Graph 
from .model.config_parser import ConfigParser
from .model.csv2rdf import CSV2RDF
from .model.toRDF import ToRDF
from .model.format_parser import FormatParser

def convert(config_file: str) -> None:
	"""
	Convert an RML file to a different format.
	
	Args:
			config_file (str): The path to the config file in TTL.
	"""
	# Parse in an RDF file
	input_graph = Graph()
	print("Input graph created")
	input_graph.parse(config_file, format="turtle")
	print("Input graph parsed")
	output_graph_dict: dict[str: tuple[Graph, str]] = {}

	namespaces = input_graph.namespaces()
	format_parser = FormatParser()

	for source_file, file_type, template, class_map, columns in ConfigParser(input_graph).parse():
		if source_file is None:
			ToRDF().to_rdf(template, class_map, columns, output_graph_dict)
		else:
			CSV2RDF(source_file).process_csv_to_rdf(template, class_map, columns, output_graph_dict)

	# Serialize the graph to a TTL file
	for destination in output_graph_dict:
		output_graph, format = output_graph_dict[destination]
		print("Destination: ", destination, ", output_graph: ", output_graph)
		print("\n")
		format_str = format_parser.parse(format)
		for prefix, uri in namespaces:
			output_graph.bind(prefix, uri)
		output_graph.serialize(destination, format_str)
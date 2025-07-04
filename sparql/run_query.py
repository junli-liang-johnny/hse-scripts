from rdflib import Graph, Namespace, DCTERMS

def run_update_file(ttl_file: str, query_file: str, output: str) -> None:
		"""
		Load a Turtle file and run a SPARQL query on it.

		:param ttl_file: Path to the Turtle file.
		:param query_file: Path to the SPARQL query file.
		"""
		# Load the Turtle file into a graph
		g = Graph()
		g.bind("dcterms", DCTERMS)
		g.bind("dct", DCTERMS)
		g.parse(ttl_file, format='turtle')

		# Read the SPARQL query from the file
		with open(query_file, 'r') as f:
				query = f.read()

		# Execute the SPARQL query
		g.update(query)

		g.serialize(destination=output, format='turtle')

def run_update(ttl_file: str, query: str, output: str) -> None:
		"""
		Load a Turtle file and run a SPARQL query on it.

		:param ttl_file: Path to the Turtle file.
		:param query: SPARQL query string.
		"""
		# Load the Turtle file into a graph
		g = Graph()
		g.bind("dcterms", DCTERMS)
		g.bind("dct", DCTERMS)
		g.parse(ttl_file, format='turtle')

		# Execute the SPARQL query
		g.update(query)

		g.serialize(destination=output, format='turtle')

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description="Run a SPARQL query on a Turtle file.")
	parser.add_argument("--ttl-file", type=str, help="Path to the Turtle file.")
	parser.add_argument("--query", type=str, help="SPARQL query string.")
	parser.add_argument("--query-file", type=str, help="Path to the SPARQL query file.")
	parser.add_argument("--output", type=str, help="Path to the output file.")
	args = parser.parse_args()

	if args.query_file:
		run_update_file(args.ttl_file, args.query_file, args.output)
	elif args.query:
		run_update(args.ttl_file, args.query, args.output)
	else:
		print("Please provide either a query string or a query file.")
		parser.print_help()
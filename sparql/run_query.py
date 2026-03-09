from rdflib import Graph, Namespace, DCTERMS, DCAT

HSE = Namespace("https://w3id.org/hse/")
PHI = Namespace("https://w3id.org/hse/ontology/phi#")
PHD = Namespace("https://w3id.org/hse/ontology/phd#")
DPV = Namespace("https://w3id.org/dpv#")
PHT = Namespace("https://w3id.org/hse/terminology#")

def create_graph() -> Graph:
	g = Graph()
	g.bind("dcterms", DCTERMS)
	g.bind("dct", DCTERMS)
	g.bind("dcat", DCAT)
	g.bind("hse", HSE)
	g.bind("phi", PHI)
	g.bind("phd", PHD)
	g.bind("dpv", DPV)
	g.bind("pht", PHT)
	return g

def run_update_file(ttl_file: str, query_file: str, output: str) -> None:
		"""
		Load a Turtle file and run a SPARQL query on it.

		:param ttl_file: Path to the Turtle file.
		:param query_file: Path to the SPARQL query file.
		"""
		# Load the Turtle file into a graph
		g = create_graph()
		g.parse(ttl_file, format='turtle')

		# Re-bind prefixes after parsing to avoid rdflib creating phi1/phd1 duplicates
		g.bind("phi", PHI)
		g.bind("phd", PHD)
		g.bind("pht", PHT)

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
		g = create_graph()
		g.parse(ttl_file, format='turtle')

		# Execute the SPARQL query
		g.update(query)

		g.serialize(destination=output, format='turtle')

def main():
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

if __name__ == "__main__":
	main()
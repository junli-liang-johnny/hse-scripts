from rml_py import convert
import argparse

def main():
	parser = argparse.ArgumentParser(description="Convert CSV to RDF using RML mapping.")
	parser.add_argument("--config", help="Path to the config ttl file.")
	args = parser.parse_args()

	# Convert CSV to RDF using the provided mapping
	convert(args.config)

if __name__ == "__main__":
	main()
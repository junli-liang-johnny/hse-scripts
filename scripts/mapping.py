import argparse
import sys
import os

# Dynamically add the parent directory of 'scripts' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.csv_utils import load_and_print_csv
from scripts.rdf_mapping.csv_rdf_convert import r2rml_csv_convert

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Load and print CSV data.")
	parser.add_argument(
		"--input", 
		type=str,
		required=True,
		help="Path to the CSV file"
		)

	parser.add_argument(
		"--output", 
		type=str,
		required=True,
		help="Path to the output CSV file"
		)

	args = parser.parse_args()
	# load_and_print_csv(args.input)

	r2rml_csv_convert(args.input, args.output)
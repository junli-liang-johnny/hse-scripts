import argparse
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

"""
python -m scripts.pipeline.sparql.fields_completeness -e http://localhost:3030/v5 -o ../hse-data/output/dq/v2/mro_fields_completeness.csv
"""

def main():
	parser = argparse.ArgumentParser(description="Fields completeness assessment")
	parser.add_argument("--sparql-endpoint", "-e", default="http://localhost:3030/indicators", help="SPARQL endpoint URL")
	parser.add_argument("-o", "--output-csv", default="fields_completeness_output.csv", help="Output file")
	args = parser.parse_args()

	sparql_endpoint = args.sparql_endpoint
	output_csv = args.output_csv

	sparql = SPARQLWrapper(sparql_endpoint)

	with open("./sparql/v2/MRO_completeness.rq", "r") as f:
		query = f.read()

	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	data = [
		{
			"indicator": result["indicator"]["value"],
			"requiredFieldCompletenessPercent": float(result["requiredFieldCompletenessPercent"]["value"]),
			"mandatoryCompletenessPercent": float(result["mandatoryCompletenessPercent"]["value"]),
			"recommendedCompletenessPercent": float(result["recommendedCompletenessPercent"]["value"]),
			"optionalCompletenessPercent": float(result["optionalCompletenessPercent"]["value"]),
			"overallCompletenessPercent": float(result["overallCompletenessPercent"]["value"])
		}
		for result in results["results"]["bindings"]
	]
	df = pd.DataFrame(data)
	df.to_csv(output_csv, index=False)
	print(f"Results written to {output_csv}")

if __name__ == "__main__":
	main()
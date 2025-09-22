import argparse
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

"""
python -m scripts.pipeline_scripts.sparql.fields_completeness -e http://localhost:3030/v5 -o ../hse-data/output/dq/v2/mro_fields_completeness.csv
"""

def main():
	parser = argparse.ArgumentParser(description="Fields completeness assessment")
	parser.add_argument("--sparql-endpoint", "-e", default="http://localhost:3030/v5", help="SPARQL endpoint URL")
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
	def to_percent(val):
		return round(float(val) * 100, 2)

	data = [
		{
			"indicator": result["indicator"]["value"],
			"requiredFieldCompletenessPercent": to_percent(result["requiredFieldCompletenessPercent"]["value"]),
			"mandatoryCompletenessPercent": to_percent(result["mandatoryCompletenessPercent"]["value"]),
			"recommendedCompletenessPercent": to_percent(result["recommendedCompletenessPercent"]["value"]),
			"optionalCompletenessPercent": to_percent(result["optionalCompletenessPercent"]["value"]),
			"overallCompletenessPercent": to_percent(result["overallCompletenessPercent"]["value"])
		}
		for result in results["results"]["bindings"]
	]
	df = pd.DataFrame(data)
	df.to_csv(output_csv, index=False)
	print(f"Results written to {output_csv}")

	# output raw results
	data = [
		{
			"indicator": result["indicator"]["value"],
			"requiredFieldCompletenessPercent": result["requiredFieldCompletenessPercent"]["value"],
			"mandatoryCompletenessPercent": result["mandatoryCompletenessPercent"]["value"],
			"recommendedCompletenessPercent": result["recommendedCompletenessPercent"]["value"],
			"optionalCompletenessPercent": result["optionalCompletenessPercent"]["value"]
		}
		for result in results["results"]["bindings"]
	]
	df = pd.DataFrame(data)
	raw_output_csv = output_csv.replace(".csv", "_raw.csv")
	df.to_csv(raw_output_csv, index=False)
	print(f"Raw results written to {raw_output_csv}")

if __name__ == "__main__":
	main()
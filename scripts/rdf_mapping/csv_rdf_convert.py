"""
this script converts a csv file to another csv file that is ready to be 
used by R2RML mapping tool
"""
from scripts.csv_utils import load_and_print_csv
import csv

def r2rml_csv_convert(input_file: str, output_file: str) -> None:
	"""
	this function converts a csv file to another csv file that is ready to be used by R2RML mapping tool
	"""
	reader = load_and_print_csv(input_file, print_rows=False)
	with open(output_file, mode='w', encoding='utf-8') as outfile:
		writer = csv.writer(outfile)

		filtered_rows = filter_csv(reader, input_file)
		# print(f"Filtered rows: {filtered_rows}")

		if filtered_rows:
			filtered_rows[0] = [
				column_name_mapping.get(col, col) for col in filtered_rows[0]
			]
		
		# Write the filtered rows to the output file
		writer.writerows(filtered_rows)
	
	print(f"Converted {input_file} to {output_file}")

column_name_mapping = {
	'dct:publisher [ a dct:Publisher; foaf:name ]': 'dct:publisher',
	'dct:Provenance [a dct:ProvenanceStatement;\nrdfs:label ]': 'dct:Provenance',
	'dct:Provenance [a dct:ProvenanceStatement; rdfs:label ]': 'dct:Provenance',
	'dcterms:temporal [a dct:PeriodOfTime;  dcat:startDate ""^^xsd:dateTime; dcat:endDate ""^^xsd:dateTime.]': 'dct:temporal',
	'dcterms:temporal [a dct:PeriodOfTime;  dcat:endDate ""^^xsd:dateTime.]': 'dct:temporal',
	'dcat:distribution [ a dcat:Distribution; dct:format]': 'dcat:distribution',
	'dcat:contactPoint [vcard:individual vard:fn]': 'dcat:contactPoint',
	'dcterms:accrualPeriodicity <http://purl.org/linked-data/sdmx/2009/code#': 'dcterms:accrualPeriodicity',
	'adms:sample[ a dcat:Distribution; dcat:accessURL]': 'adms:sample',
	'healthdcatap:hdab [a foaf:Agent;  foaf:name ]': 'healthdcatap:hdab',
}

"""
	key: file name string
	value: list of row indexes to be removed
"""
row_index_remove_mapping = {
	'data/schema/OAHP_DataCatalogueSchemaProposal -v05.12.xlsx - Indicators.csv': [0, 2],
	'./data/schema/OAHP_DataCatalogueSchemaProposal -v05.12.xlsx - Indicators.csv': [0, 2],
	'./data/combined_indicators_copy.csv': [0, 2],
	'./data/cso/combined_indicators.csv': [0, 2],
	'data/schema/OAHP_DataCatalogueSchemaProposal -v05.12.xlsx - Data sources.csv': [0, 2, 3],
	'./data/schema/OAHP_DataCatalogueSchemaProposal -v05.12.xlsx - Data sources.csv': [0, 2, 3],
	'./data/combined_datasets_copy.csv': [0, 2, 3],
	'./data/cso/combined_datasets.csv': [0, 2, 3],
}

def filter_csv(csv_reader: list, input_file) -> list:
	"""
	Filter the CSV data based on specific criteria.
	:param csv_reader: List of rows from the CSV file
	:return: Filtered list of rows
	"""
	print(f"Input file: {input_file}")
	rows_to_remove = row_index_remove_mapping.get(input_file, [])
	print(f"Rows to remove: {rows_to_remove}")
	filtered_rows = [
		[col.strip() for col in row]
		for index, row in enumerate(csv_reader)
		if index not in rows_to_remove
	]
	return filtered_rows

if __name__ == "__main__":
	import argparse
	import sys
	import os

	parser = argparse.ArgumentParser(description="Convert CSV file for R2RML mapping.")
	parser.add_argument(
		"--input", 
		type=str,
		required=True,
		help="Path to the input CSV file"
	)
	parser.add_argument(
		"--output", 
		type=str,
		required=True,
		help="Path to the output CSV file"
	)

	args = parser.parse_args()
	r2rml_csv_convert(args.input, args.output)
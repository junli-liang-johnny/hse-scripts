"""
this script converts a csv file to another csv file that is ready to be 
used by R2RML mapping tool
"""
from scripts.csv_utils import load_and_print_csv
import csv

def r2rml_csv_convert(input_file: str, row_indexes_to_remove: list[int], output_file: str) -> None:
	"""
	this function converts a csv file to another csv file that is ready to be used by R2RML mapping tool
	"""
	reader = load_and_print_csv(input_file, print_rows=False)
	with open(output_file, mode='w', encoding='utf-8') as outfile:
		writer = csv.writer(outfile)

		filtered_rows = filter_csv(reader, input_file, row_indexes_to_remove)
		print(f"Length of filtered rows: {len(filtered_rows)}")
		cleaned_rows = remove_special_characters(filtered_rows, output_log_file=output_file.replace('.csv', '_cleaning_log.txt'))
		print(f"Length of cleaned rows: {len(cleaned_rows)}")

		# Write the filtered rows to the output file
		writer.writerows(cleaned_rows)

	print(f"Converted {input_file} to {output_file}")

"""
	key: file name string
	value: list of row indexes to be removed
"""

schema_file_prefix = "../hse-data"

row_index_remove_mapping = {
	schema_file_prefix+'/data/schema/OAHP_DataCatalogueSchemaProposal -v05.12.xlsx - Indicators.csv': [0, 2],
	schema_file_prefix+'/data/schema/OAHP_DataCatalogueSchemaProposal -v05.12.xlsx - Indicators.csv': [0, 2],
	schema_file_prefix+'/data/combined_indicators_copy.csv': [0, 2],
	schema_file_prefix+'/data/cso/combined_indicators.csv': [0, 2],
	schema_file_prefix+'/data/schema/OAHP_DataCatalogueSchemaProposal -v05.12.xlsx - Data sources.csv': [0, 2, 3],
	schema_file_prefix+'/data/schema/OAHP_DataCatalogueSchemaProposal -v05.12.xlsx - Data sources.csv': [0, 2, 3],
	schema_file_prefix+'/data/combined_datasets_copy.csv': [0, 2, 3],
	schema_file_prefix+'/data/cso/combined_datasets.csv': [0, 2, 3],
	schema_file_prefix+'/data/schema/delphi_indicators_v.05.12.csv': [0, 2],
	schema_file_prefix+'/data/schema/OAHP_MasterDataCatalogueVersion0005.xlsx - Indicators.csv.csv': [0, 2],
}

def filter_csv(csv_reader: list, input_file, row_indexes_to_remove: list[int]) -> list:
	"""
	Filter the CSV data based on specific criteria.
	:param csv_reader: List of rows from the CSV file
	:return: Filtered list of rows
	"""
	# print("mapping file dict: ", row_index_remove_mapping)
	print(f"Input file: {input_file}")
	if row_indexes_to_remove and len(row_indexes_to_remove) > 0:
		rows_to_remove = row_indexes_to_remove
	else:
		rows_to_remove = row_index_remove_mapping.get(input_file, [])
	print(f"Rows to remove: {rows_to_remove}")
	filtered_rows = [
		[col.strip() for col in row]
		for index, row in enumerate(csv_reader)
		if index not in rows_to_remove
	]
	return filtered_rows

def remove_special_characters(rows: list[list[str]], output_log_file: str) -> list[list[str]]:
	"""
	Remove special characters from each cell in the CSV data.
	:param rows: List of rows from the CSV file
	:return: List of rows with special characters removed
	"""
	with open(output_log_file, mode="w", encoding="utf-8") as log_file:
		log_file.write("Log of cleaned cells:\n")
		log_file.write("="*100 + "\n")

	cleaned_rows = []
	for row in rows:
		# cleaned_row = [col.replace('\n', ' ').replace('\r', ' ').strip() for col in row]
		cleaned_row = []
		for col in row:
			cleaned_col = col.replace('\n', ' ').replace('\r', ' ').strip()
			if col != cleaned_col:
				with open(output_log_file, mode="a", encoding="utf-8") as log_file:
					log_file.write(f"Identifier:\n{row[1]}\n{'-'*100}\nOriginal:\n{col}\n{'-'*100}\nCleaned:\n{cleaned_col}\n{'='*100}\n")
			cleaned_row.append(cleaned_col)
		cleaned_rows.append(cleaned_row)
	return cleaned_rows

def main():
	import argparse

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
	parser.add_argument('--row-index-remove', type=int, nargs='+', help="Row indexes to remove, e.g., --row-index-remove 0 --row-index-remove 2")

	args = parser.parse_args()
	r2rml_csv_convert(args.input, args.row_index_remove, args.output)

if __name__ == "__main__":
	main()
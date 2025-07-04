"""
This script extracts a specified column from a CSV file and creates a new CSV file with a custom header and namespace.
"""
import csv
import uuid
import argparse
from scripts.rdf_mapping.csv_rdf_convert import filter_csv

def create_csv(config: dict) -> None:
		"""
		Generalized function to create a new CSV file by extracting a specific column.
		:param config: Dictionary containing all configuration parameters
		"""
		try:
				input_file = config["input_file"]
				output_file = config["output_file"]
				column_name = config["column_name"]
				new_header = config["new_header"]
				namespace = config["namespace"]
				id_template = config["id_template"]
				extracted_value_insert_index = config.get("extracted_value_insert_index", -1)
				optional_values_to_insert = config.get("optional_values_to_insert", [])
				identifier_csv = config.get("identifier_csv", None)  # Path to the additional CSV file
				identifier_column = config.get("identifier_column", None)  # Column to fetch identifiers from
				
				identifiers = _load_identifiers(identifier_csv, identifier_column) if identifier_csv and identifier_column else []
				print(f"Identifiers loaded: {identifiers}")

				with open(input_file, mode='r', encoding='utf-8') as infile:
						reader = filter_csv(list(csv.reader(infile)), input_file)
						filtered_rows = _minimise_rows(reader, column_name)
						print(f"Filtered rows: {filtered_rows}")

						output_data = [new_header]

						for index, value in enumerate(filtered_rows):
							if identifiers and index < len(identifiers):
								row_id = identifiers[index] if index >= len(identifiers) and identifiers[index] != "None" else namespace + id_template.format(uuid=str(uuid.uuid4()))
							else:
								row_id = namespace + id_template.format(uuid=str(uuid.uuid4()))

							if optional_values_to_insert:
								_converted_values = [
									value.replace("{uuid}", str(uuid.uuid4())) if "{uuid}" in value else value
									for value in optional_values_to_insert
								]	
								output_row = [row_id] + _converted_values
								if extracted_value_insert_index != -1:
									output_row.insert(extracted_value_insert_index, value)
								output_data.append(output_row)
							else:
								if extracted_value_insert_index != -1:
									output_data.append([row_id, value])
									# output_data.append([row_id, value.split(",")])
								else:
									output_data.append([row_id])

				with open(output_file, mode='w', encoding='utf-8') as outfile:
						writer = csv.writer(outfile)
						writer.writerows(output_data)

				print(f"CSV created successfully at {output_file}")

		except FileNotFoundError:
				print(f"Error: The file '{config['input_file']}' was not found.")
		except Exception as e:
				print(f"An error occurred: {e}")

def _load_identifiers(csv_file: str, column: str) -> list:
		"""
		Load identifiers from a CSV file.
		:param csv_file: Path to the CSV file
		:param column: Column name to extract identifiers from
		:return: List of identifiers
		"""
		try:
			with open(csv_file, mode='r', encoding='utf-8') as infile:
				reader = csv.DictReader(infile)
				return [row[column] for row in reader]
		except FileNotFoundError:
			print(f"Error: The file '{csv_file}' was not found.")
			return []	

def _minimise_rows(csv_reader: list[list], column_name: str) -> list[list]:
		"""
		Remove duplicate rows based on a specific column.
		Only return the first occurrence of each unique value in the specified column.
		:param csv_reader: List of rows from the CSV file
		:param column_name: Column name to filter by
		:return: Filtered list of rows
		"""
		unique_values = set()
		filtered_rows = []
		print(f"CSV header: {csv_reader[0]}")
		column_index = csv_reader[0].index(column_name)

		for row in csv_reader:
			value = row[column_index].strip()
			print(f"Processing value: {value}")
			if value != '' and value not in unique_values:
				unique_values.add(value)
				filtered_rows.append(value)

		return filtered_rows[1:]

if __name__ == "__main__":
		parser = argparse.ArgumentParser(description="Generalized CSV creation script.")
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
		parser.add_argument(
				"--column",
				type=str,
				required=True,
				help="Name of the column to extract"
		)
		parser.add_argument(
				"--header",
				type=str,
				nargs='+',
				required=True,
				help="New header for the output CSV file"
		)
		parser.add_argument(
				"--namespace",
				type=str,
				required=True,
				help="Base namespace for generating IDs"
		)
		parser.add_argument(
				"--id-template",
				type=str,
				required=True,
				help="Template for generating row IDs (use {uuid} as a placeholder for UUIDs)"
		)
		parser.add_argument(
				"--extracted-value-insert-index",
				type=int,
				default=-1,
				help="Index to insert the extracted value in the new CSV (default: -1)"
		)
		parser.add_argument(
				"--optional-values-to-insert",
				type=str,
				nargs='+',
				default=[],
				help="List of additional values to insert in the new CSV"
		)
		parser.add_argument(
				"--identifier-csv",
				type=str,
				default=None,
				help="Path to the additional CSV file for identifiers"
		)
		parser.add_argument(
				"--identifier-column",
				type=str,
				default=None,
				help="Column name to extract identifiers from in the additional CSV file"
		)

		args = parser.parse_args()

		config = {
				"input_file": args.input,
				"output_file": args.output,
				"column_name": args.column,
				"new_header": args.header,
				"namespace": args.namespace,
				"id_template": args.id_template,
				"extracted_value_insert_index": args.extracted_value_insert_index,
				"optional_values_to_insert": args.optional_values_to_insert,
				"identifier_csv": args.identifier_csv,
				"identifier_column": args.identifier_column
		}

		create_csv(config)

def create_subject_csv(
	csv_reader: list,
	namespace: str,
	id_template_column: str,
	split_by: str = None,
	template_split_index: int = None
) -> list:

	"""
	Add a subject/identifier column to a CSV data (list of rows) based on a namespace and a column value.

	:param csv_reader: List of rows (each row is a dictionary) from the CSV file
	:param namespace: Namespace to prepend to the identifier
	:param id_template_column: Column name to use for generating the identifier
	:return: List of rows with the added 'new_id' column
	"""
	try:
		# Ensure the id_template_column exists in the CSV
		if not csv_reader or id_template_column not in csv_reader[0]:
			raise KeyError(f"Column '{id_template_column}' does not exist in the input data.")

		# Add 'new_id' to each row
		updated_rows = []
		for row in csv_reader:
			if split_by is not None and template_split_index is not None:
				# Split the identifier based on the specified column and index
				split_value = row[id_template_column].split(split_by)[template_split_index]
				new_id = namespace + str(split_value)
			else:
				new_id = namespace + str(row[id_template_column]).replace(" ", "-")
			updated_row = {'id': new_id, **row}  # Add 'new_id' as the first column
			updated_rows.append(updated_row)

		return updated_rows

	except KeyError as e:
		print(f"Error: {e}")
		return []
	except Exception as e:
		print(f"An error occurred: {e}")
		return []

def main():
	import argparse
	import csv

	parser = argparse.ArgumentParser(description="Create a subject CSV with a new identifier column.")
	parser.add_argument("--input", help="Path to the input CSV file.")
	parser.add_argument("--output", help="Path to the output CSV file.")
	parser.add_argument("--namespace", help="Namespace to prepend to the identifier.")
	parser.add_argument("--id-template-column", help="Column name to use for generating the identifier.")
	parser.add_argument(
		"--split-by",
		type=str,
		default=None,
		help="Column name to split the identifier by (optional)."
	)
	parser.add_argument(
		"--template-split-index",
		type=int,
		default=None,
		help="Index to split the identifier template (optional)."
	)
	parser.add_argument(
		"--row-index-remove",
		type=int,
		nargs='*',
		default=[],
		help="Row indexes to remove from the input CSV (0-based). E.g. --row-index-remove 0 2"
	)
	args = parser.parse_args()

	# Read the input CSV, optionally stripping extra header rows first
	with open(args.input, mode='r', encoding='utf-8') as infile:
		raw_rows = list(csv.reader(infile))
	row_indexes_to_remove = args.row_index_remove if args.row_index_remove else []
	if row_indexes_to_remove:
		from scripts.rdf_mapping.csv_rdf_convert import filter_csv
		filtered_rows = filter_csv(raw_rows, args.input, row_indexes_to_remove)
		header = filtered_rows[0]
		csv_reader = [dict(zip(header, row)) for row in filtered_rows[1:]]
	else:
		csv_reader = [dict(zip(raw_rows[0], row)) for row in raw_rows[1:]]
	# Create the subject CSV
	params = {
		'csv_reader': csv_reader,
		'namespace': args.namespace,
		'id_template_column': args.id_template_column,
		'split_by': args.split_by,
		'template_split_index': args.template_split_index
	}
	subject_csv = create_subject_csv(**params)
	print(f"Created {len(subject_csv)} rows with new identifiers.")
	# Write the output CSV
	with open(args.output, mode='w', encoding='utf-8', newline='') as outfile:
		fieldnames = ['id'] + list(subject_csv[0].keys())[1:]  # Include 'id' and the rest of the columns
		writer = csv.DictWriter(outfile, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(subject_csv)

	print(f"Output written to {args.output}")

if __name__ == "__main__":
	main()

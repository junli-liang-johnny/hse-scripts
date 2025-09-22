import pandas as pd
import argparse
from typing import List
import io

id_template = 'hse'
# Total desired ID length (e.g. hse + 7 digits = 10)
id_length = 10

def create_padded_id(index: str) -> str:
	number_part = str(index).zfill(id_length - len(id_template))
	return f"{id_template}{number_part}"

def handle_multiple_ids(index: str) -> str:
	id_parts = str(index).split(',')
	# return create_padded_id(id_parts[0].strip())
	return id_parts[0].strip()  # Return first valid ID after stripping whitespace

def handle_space_separated_ids(id: str) -> str:
	return id.replace(' ', '-')  # Replace spaces with hyphens

def process_id_recreation(df: pd.DataFrame) -> pd.DataFrame:
	"""Recreate identifiers while preserving the original in owl:sameAs.

	Rules:
	  * Always assign a new sequential padded ID.
	  * Preserve the original (even if multiple/comma separated) in owl:sameAs.
	  * If original contained commas, append note in skos:note.
	"""
	id_count = 1
	for index, row in df.iterrows():
		original_id = row.get('dct:identifier')
		# print(f'Original id: {original_id}')

		# Build new ID
		new_id = create_padded_id(id_count)
		id_count += 1

		# Store original id only if it is a non-empty string
		if pd.notna(original_id) and str(original_id).strip():
			df.at[index, 'owl:sameAs'] = str(original_id).strip()
		else:
			df.at[index, 'owl:sameAs'] = ''

		# Multiple IDs note
		if pd.notna(original_id) and ',' in str(original_id):
			existing_note = row.get('skos:note')
			note_fragment = f" Original ID: {original_id}."
			if pd.isna(existing_note) or not existing_note:
				df.at[index, 'skos:note'] = note_fragment.strip()
			else:
				df.at[index, 'skos:note'] = str(existing_note) + note_fragment

		# print(f'New id {new_id}')
		df.at[index, 'dct:identifier'] = new_id
	return df

def main():
	parser = argparse.ArgumentParser(description="Recreate IDs in a CSV file.")
	parser.add_argument('--input-file', required=True, help='Path to the input CSV file')
	parser.add_argument('--output-file', required=True, help='Path to the output CSV file')
	args = parser.parse_args()

	input_file = args.input_file
	output_file = args.output_file

	# Lines we want to preserve from the source (original display headers & cardinalities)
	skiprows = [0, 2]

	with open(input_file, 'r', newline='') as f:
		src_lines = f.readlines()

	if len(src_lines) < 2:
		raise ValueError("Input file must contain at least two header lines.")

	# Read data excluding preserved lines (now sanitized line1 is header for pandas)
	df = pd.read_csv(input_file, skiprows=skiprows)
	df.dropna(how='all', inplace=True)  # Remove rows where all elements are NaN

	print(f'Loaded CSV shape (after initial clean): {df.shape}')
	print(f'Sample columns: {list(df.columns)[:10]}')

	processed_df = process_id_recreation(df)

	# Build output preserving ordering: sanitized line0, processed header, sanitized line2, processed data
	# processed_csv_lines = processed_df.to_csv(index=False, lineterminator='\n').splitlines(keepends=True)

	processed_df.to_csv(output_file, index=False, lineterminator='\n')

	print(f'Saved processed csv shape: {processed_df.shape}')
	print('Sample (first 3 rows):')
	print(processed_df.head(3))

if __name__ == "__main__":
	main()
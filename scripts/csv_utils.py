import csv
import pandas as pd
import glob

def load_and_print_csv(file_path, print_rows=True):
	"""
	Load data from a CSV file and print each row.
	:param file_path: Path to the CSV file
	"""
	try:
		with open(file_path, mode='r', encoding='utf-8') as file:
			reader = list(csv.reader(file))

			if print_rows:
				for index, row in enumerate(reader):
					print(f"Row {index}: {row}")
		return reader
	except FileNotFoundError:
		print(f"Error: The file '{file_path}' was not found.")
	except Exception as e:
		print(f"An error occurred: {e}")
def write_csv(file_path, data: list[list[str]]):
	"""
	Write data to a CSV file.
	:param file_path: Path to the CSV file
	:param data: Data to be written to the CSV file
	"""
	try:
		with open(file_path, mode='w', newline='', encoding='utf-8') as file:
			writer = csv.writer(file)
			writer.writerows(data)
	except Exception as e:
		print(f"An error occurred while writing to the file: {e}")

def validate_csv(csv_file: str, expected_header: list) -> bool:
	"""
	Validate the CSV data against the expected header.
	:param csv_reader: List of rows from the CSV file
	:param expected_header: Expected header for validation
	:return: True if valid, False otherwise
	"""
	try:
		with open(csv_file, mode='r', encoding='utf-8') as file:
			csv_reader = list(csv.reader(file))
	except FileNotFoundError:
		print(f"Error: The file '{csv_file}' was not found.")
		return False
	except Exception as e:
		print(f"An error occurred: {e}")
		return False

	if not csv_reader:
		print("Error: The CSV file is empty.")
		return False

	header = csv_reader[0]
	if header != expected_header:
		print(f"Error: The header does not match the expected format. Expected: {expected_header}, Found: {header}")
		return False

	df = pd.read_csv(csv_file)
	print("The file is a valid CSV.")
	print(f"Number of rows: {len(df)}")
	print(f"Columns: {list(df.columns)}")

	return True

def insert_additional_headers(csv_file: str, additional_headers: list[list[str]], header_indices: list[int]) -> None:
	"""
	Insert additional headers at specific row indices in a CSV file.
	:param csv_file: Path to the CSV file
	:param additional_headers: List of additional headers to be added
	:param header_indices: List of row indices where the headers should be inserted
	"""
	try:
		# Read the existing CSV file into a list of rows
		with open(csv_file, mode='r', encoding='utf-8') as file:
			rows = list(csv.reader(file))

			# Insert additional headers at the specified indices
		for header, index in zip(additional_headers, header_indices):
			rows.insert(index, header)

			# Write the modified rows back to the CSV file
		with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
			writer = csv.writer(file)
			writer.writerows(rows)

		print(f"Additional headers inserted successfully into {csv_file}.")
	except Exception as e:
		print(f"An error occurred: {e}")

def combine_csv_files(input_files: list[str], output_file: str, header_rows: int) -> None:
		"""
		Combine multiple CSV files into a single CSV file, handling multiple header rows.
		:param input_files: List of input CSV files
		:param output_file: Path to the output CSV file
		:param header_rows: Number of header rows to skip in each input file
		"""
		try:
				dataframes = []
				for file in input_files:
						# Skip the specified number of header rows
						df = pd.read_csv(file, skiprows=header_rows)
						dataframes.append(df)

				# Combine all dataframes into one
				combined_df = pd.concat(dataframes, ignore_index=True)

				# Save the combined dataframe to the output file
				combined_df.to_csv(output_file, index=False)
				print(f"Combined {len(input_files)} files into {output_file}.")
		except Exception as e:
				print(f"An error occurred: {e}")

def deduplicate_csv(csv_file: str) -> None:
	"""
	Deduplicate the rows in a CSV file and log the dropped rows.
	:param csv_file: Path to the CSV file
	"""
	try:
		# Read the CSV file
		df = pd.read_csv(csv_file)

		# Identify duplicate rows
		duplicates = df[df.duplicated(keep='first')]

		# Drop duplicates
		df.drop_duplicates(inplace=True)

		# Save the deduplicated dataframe back to the file
		df.to_csv(csv_file, index=False)

		# Log the dropped rows
		if not duplicates.empty:
			print(f"Dropped {len(duplicates)} duplicate rows:")
			print(duplicates)

		print(f"Deduplication completed successfully for {csv_file}.")
	except Exception as e:
		print(f"An error occurred: {e}")

def get_all_file_paths(directory: str, extension: str = "*") -> list:
	"""
	Get all file paths from a directory with a specific extension.
	:param directory: Path to the directory
	:param extension: File extension to filter (e.g., '*.csv')
	:return: List of file paths
	"""
	return glob.glob(f"{directory}/**/*.{extension}", recursive=True)
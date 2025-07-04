from scripts.csv_utils import load_and_print_csv
from scripts.hse2ucd.config import files2process

def load_process_files():
	header: list[str] = []
	process_files: list[list[str]] = []

	for index, file in enumerate(files2process):
		# Load the CSV file
		file_csv = load_and_print_csv(file, print_rows=False)

		if len(header) == 0:
			# Store the header from the first file
			header = file_csv[0]

		# Append the processed DataFrame to the list
		process_files.append(file_csv[1:])

	# Return the list of processed files
	return header, process_files

if __name__ == "__main__":
	# Load and process the files
	header, process_files = load_process_files()

	print("Headers: "+ str(header))

	# Print the processed files
	for index, file in enumerate(process_files):
		print(f"Processed File {index + 1}:")
		print(file)
		print("\n")
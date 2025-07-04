import pandas as pd

def clean_csv(file_path, output_file_path):
	"""
	Validate the CSV file by checking for duplicates and empty rows.
	"""
	df = pd.read_csv(file_path)

	# drop duplicates
	df_cleaned = df.drop_duplicates()

	# drop empty rows
	df_cleaned = df_cleaned.dropna(how='all')

	# drop \n characters, leading and trailing spaces and double quotes
	df_cleaned = df_cleaned.map(lambda x: x.strip().replace('\n', '').replace('"', '') if isinstance(x, str) else x)

	# save the cleaned file
	df_cleaned.to_csv(output_file_path, index=False)

	print(f"Validation completed. Cleaned file saved to {output_file_path}")
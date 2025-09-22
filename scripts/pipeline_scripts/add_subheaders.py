import pandas as pd
import argparse

def main():
	# parse command line arguments
	parser = argparse.ArgumentParser(description='Join datasets for analysis.')
	parser.add_argument('--input', type=str, required=True, help='Path to the input CSV file')
	parser.add_argument('--output', type=str, default='reordered_output.csv', help='Output file path')
	parser.add_argument('--subheaders', type=str, nargs='+', required=True, help='Subheaders to add (space-separated). The length of this subheaders should be less than or equal to the number of columns in the input CSV file.')
	parser.add_argument('--fill-value', type=str, default='', help='Value to fill missing subheader columns (default: empty string)')
	parser.add_argument('--start-row-index', type=int, default=0, help='Index to start adding subheaders if subheaders length is less then the input (default: 0)')
	parser.add_argument('--start-column-index', type=int, default=0, help='Index to start adding subheaders if subheaders length is less then the input (default: 0)')
	args = parser.parse_args()

	input_path = args.input
	output_path = args.output
	subheaders = args.subheaders
	fill_value = args.fill_value
	start_row_index = args.start_row_index
	start_column_index = args.start_column_index

	# print parameters
	print(f"Input path: {input_path}")
	print(f"Output path: {output_path}")
	print(f"Subheaders: {subheaders}")
	print(f"Fill value: {fill_value}")
	print(f"Start row index: {start_row_index}")
	print(f"Start column index: {start_column_index}")

	# Load the CSV file
	print(f"Loading CSV file: {input_path}")
	df = pd.read_csv(input_path)
	print(f"Original shape: {df.shape}")
	print(f"Original columns: {df.columns.tolist()}")

	# Create subheader rows
	print(f"\nAdding {len(subheaders)} subheader rows: {subheaders}")

	# Create subheader rows as DataFrames
	new_row = {}
	input_columns = df.columns.tolist()
	if len(subheaders) < len(input_columns):
		for index, col in enumerate(input_columns):
			if start_column_index > index:
				new_row[col] = fill_value
			else:
				new_row[col] = subheaders[index - start_column_index] if index - start_column_index < len(subheaders) else fill_value
	else:
		for index, col in enumerate(input_columns):
			new_row[col] = subheaders[index]

	# Convert subheader rows to DataFrame
	subheader_df = pd.DataFrame([new_row])
	
	# Concatenate: original first row, subheaders, then rest of data
	if start_column_index > 0:
		result = pd.concat([df.iloc[:start_row_index], subheader_df, df.iloc[start_row_index:]], ignore_index=True)
	else:
		result = pd.concat([subheader_df, df], ignore_index=True)
	
	print(f"Result shape: {result.shape}")
	print(f"Added {len(subheaders)} subheader rows")
	
	# Save the result
	result.to_csv(output_path, index=False)
	print(f"CSV with subheaders saved to: {output_path}")
	
	# Display first few rows to show the result
	print(f"\nFirst {min(5, len(result))} rows of the result:")
	print(result.head())

if __name__ == "__main__":
	main()
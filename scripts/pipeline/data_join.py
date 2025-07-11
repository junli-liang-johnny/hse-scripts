import pandas as pd
import argparse

def main():
	# parse command line arguments
	parser = argparse.ArgumentParser(description='Join datasets for analysis.')
	parser.add_argument('--delphi', type=str, required=True, help='Path to the Delphi dataset')
	parser.add_argument('--master', type=str, default='data/master.csv', help='Path to the master dataset')
	parser.add_argument('--on', type=str, default='id', help='Column name to join on')
	parser.add_argument('--output', type=str, default='output.csv', help='Output file path')
	args = parser.parse_args()

	delphi_path = args.delphi
	master_path = args.master
	on_column = args.on
	output_path = args.output

	# load the datasets
	delphi_df = pd.read_csv(delphi_path)
	master_df = pd.read_csv(master_path)

	drop_columns = [
		'DOMAIN',
		'INDICATOR',
		'RESPONDENT 1',
		'RESPONDENT 2',
		'RESPONDENT 3',
		'RESPONDENT 4',
		'RESPONDENT 5',
		'RESPONDENT 6',
		'RESPONDENT 7',
		'RESPONDENT 8',
		'RESPONDENT 9',
		'RESPONDENT 10',
		'RESPONDENT 11',
		'RESPONDENT 12',
		'RESPONDENT 13'
	]

	filtered_master_df = master_df.drop(columns=drop_columns)

	result = pd.merge(delphi_df, filtered_master_df, on=on_column)

	# # print columns with _x or _y suffix
	# x_columns = [col for col in result.columns if col.endswith('_x')]
	# y_columns = [col for col in result.columns if col.endswith('_y')]
	
	# if x_columns or y_columns:
	# 	print(f"Columns with _x suffix: {x_columns}")
	# 	print(f"Columns with _y suffix: {y_columns}")
	# else:
	# 	print("No columns with _x or _y suffix found")

	# print the result
	print(result)
	print(f"Columns in the result: {result.columns.tolist()}")

	# save the result to a CSV file
	result.to_csv(output_path, index=False)

if __name__ == "__main__":
	main()
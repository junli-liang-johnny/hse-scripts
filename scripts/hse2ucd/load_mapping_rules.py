from scripts.csv_utils import load_and_print_csv
from scripts.hse2ucd.config import mapping_rules_file
import pandas as pd
from pprint import pprint

def load_mapping_rules(file_path):
	"""
	Load mapping rules from a CSV file.
	:param file_path: Path to the CSV file
	:return: List of mapping rules
	"""

	# Read the CSV file into a DataFrame
	df = pd.read_csv(file_path)

	# Drop rows where 'UCD field' is NaN (empty)
	df = df.dropna(subset=['UCD field'])

	# Create dictionaries based on the 'UCD sheet tab'
	indicators_dict = df[df['UCD sheet tab'] == 'Indicators'].set_index('UCD field')['HSE field'].to_dict()
	datasets_dict = df[df['UCD sheet tab'] == 'Datasets'].set_index('UCD field')['HSE field'].to_dict()

	# Replace 'nan' with 'None' in the dictionaries
	indicators_dict = {k: (None if pd.isna(v) else v) for k, v in indicators_dict.items()}
	datasets_dict = {k: (None if pd.isna(v) else v) for k, v in datasets_dict.items()}

	# Replace '\n' with a whitespace in the keys of both dictionaries
	indicators_dict = {k.replace('\n', ' '): v for k, v in indicators_dict.items()}
	datasets_dict = {k.replace('\n', ' '): v for k, v in datasets_dict.items()}

	print("Loaded Mapping Rules:")
	pprint("Indicators Dictionary:")
	pprint(indicators_dict)
	pprint("Datasets Dictionary:")
	pprint(datasets_dict)
	return indicators_dict, datasets_dict

if __name__ == "__main__":
	# Load the mapping rules
	mapping_rules = load_mapping_rules(mapping_rules_file)